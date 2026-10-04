"""Internal Qt adaptation. Author examples never depend on these objects."""
from pathlib import Path
import sys
import traceback
import warnings

import shiboken6
from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Property, Qt, Signal, Slot, QThread, QEvent
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtGui import QGuiApplication

from ._model import Button, Column, Label, Row, Window
from .theme import _resolve, ThemeError
from .animation import AnimationError, Playback


class Children(QAbstractListModel):
    ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent):
        super().__init__(parent)
        self.nodes = []

    def roleNames(self):
        return {self.ROLE: b"nodeData"}

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.nodes)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == self.ROLE and index.isValid() and 0 <= index.row() < len(self.nodes):
            return self.nodes[index.row()]
        return None

    def append(self, node):
        row = len(self.nodes)
        self.beginInsertRows(QModelIndex(), row, row)
        self.nodes.append(node)
        self.endInsertRows()


class Node(QObject):
    textChanged = Signal()
    styleChanged = Signal()
    animationRequested = Signal('QVariantMap')
    animationCancelled = Signal()

    def __init__(self, value, app):
        super().__init__(app.bridge)
        self.value, self.app = value, app
        self._animation_host = None
        self._active = self._pending = None
        self._serial = 0
        self._active_serial = 0
        self._animation_error = None
        kinds = {Window: "column", Column: "column", Row: "row", Label: "label", Button: "button"}
        if type(value) not in kinds:
            raise TypeError(f"Unsupported experimental node: {type(value).__name__}")
        self._kind = kinds[type(value)]
        self._id = f"node-{len(app.nodes)}"
        app.nodes.append(self)
        value._runtime = self
        self.model = Children(self)
        if hasattr(value, "children"):
            for child in value.children:
                self.model.append(Node(child, app))

    def check_thread(self):
        if QThread.currentThread() != self.thread():
            raise RuntimeError('UI updates must run on the application thread')

    def append(self, child):
        self.model.append(Node(child, self.app))

    @Slot(QObject)
    def attachAnimations(self, host):
        self._animation_host = host
        host.destroyed.connect(self._host_destroyed)

    def _host_destroyed(self):
        self._animation_host = None
        if self._active:
            self._active._state = "closed"
            self._active = None

    def play(self, timeline):
        self.check_thread()
        if (self.app._animations_closed or self._animation_host is None
                or not shiboken6.isValid(self._animation_host)):
            raise AnimationError("animation target is closed or not yet presented; play from a later UI callback")
        plan = timeline._plan(type(self.value).__name__, self.appearance)
        self._serial += 1
        plan['serial'] = self._serial
        handle = Playback(self.value, timeline)
        self._pending = handle
        self._animation_error = "Qt Quick did not acknowledge playback"
        try:
            self.animationRequested.emit(plan)
            if self._animation_error:
                raise AnimationError(self._animation_error)
            return handle
        finally:
            self._pending = None

    @Slot(int, str)
    def animationReady(self, serial, error):
        if self._pending is None or serial != self._serial:
            return
        self._animation_error = error
        if not error:
            if self._active:
                self._active._state = "replaced"
            self._active = self._pending
            self._active_serial = serial
            self._active._state = "running"

    @Slot(int)
    def animationFinished(self, serial):
        if serial == self._active_serial and self._active:
            self._active._state = "completed"
            self._active = None

    def stop_animation(self, handle):
        self.check_thread()
        if self._active is handle:
            self.cancel_animation("stopped")

    def cancel_animation(self, state):
        if self._active:
            self.animationCancelled.emit()
            self._active._state = state
            self._active = None

    @Property(str, constant=True)
    def kind(self):
        return self._kind

    @Property(str, constant=True)
    def nodeId(self):
        return self._id

    @Property(str, notify=textChanged)
    def text(self):
        return getattr(self.value, "text", "")

    @Property(bool, constant=True)
    def heading(self):
        return getattr(self.value, "heading", False)

    @Property(QObject, constant=True)
    def childrenModel(self):
        return self.model

    @Property("QVariantMap", notify=styleChanged)
    def appearance(self):
        values = self.app.public.resolved_theme | getattr(self.value, "style", {})
        # Nested tuple QVariant conversion is deliberately avoided at the QML boundary.
        gradient = values.pop("gradient")
        values.update(hasGradient=gradient is not None,
                      gradientStart=gradient[0] if gradient else values["accent"],
                      gradientEnd=gradient[1] if gradient else values["accent"])
        return values


class Bridge(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app

    @Slot()
    def closeAnimations(self):
        self.app._animations_closed = True
        for node in self.app.nodes:
            node.cancel_animation("closed")

    @Slot(str)
    def activate(self, node_id):
        try:
            node = next(node for node in self.app.nodes if node.nodeId == node_id)
            node.value.on_click()
        except Exception as exc:
            description = f"Callback {node_id}: {exc}"
            self.app.errors.append(description)
            print(description, file=sys.stderr, flush=True)
            traceback.print_exc()


class Runtime:
    def __init__(self, window, public=None):
        self.qt_app = QGuiApplication.instance() or QGuiApplication([])
        self.public = public or window._app
        self.errors, self.nodes = [], []
        self._animations_closed = False
        self.bridge = Bridge(self)
        self.hints = self.qt_app.styleHints()
        values = _resolve(self.public.theme, self.system_scheme())
        self.public._resolved = values
        self.hints.colorSchemeChanged.connect(self.system_changed)
        # Window has a deterministic implicit Column; explicit root Column
        # introduces one extra container with no additional margins.
        self.root_node = Node(window, self)
        QQuickStyle.setStyle("Basic")
        self.engine = QQmlApplicationEngine()
        self.engine.warnings.connect(self.warnings)
        context = self.engine.rootContext()
        context.setContextProperty("bridge", self.bridge)
        context.setContextProperty("rootNode", self.root_node)
        context.setContextProperty("windowTitle", window.title)
        context.setContextProperty("initialWidth", window.width)
        context.setContextProperty("initialHeight", window.height)
        self.engine.load(str(Path(__file__).with_name("qml") / "Main.qml"))
        if not self.engine.rootObjects():
            self.hints.colorSchemeChanged.disconnect(self.system_changed)
            self.engine.deleteLater()
            self.qt_app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            for node in self.nodes:
                node.value._runtime = None
            raise RuntimeError("Internal QML load failed: " + "\n".join(self.errors))
        self.window = self.engine.rootObjects()[0]
        self.quick = shiboken6.wrapInstance(shiboken6.getCppPointer(self.window)[0], QQuickWindow)

    def system_scheme(self):
        return {Qt.ColorScheme.Light: "light", Qt.ColorScheme.Dark: "dark"}.get(self.hints.colorScheme())

    def set_theme(self, choice):
        self.root_node.check_thread()
        values = _resolve(choice, self.system_scheme())
        self.apply_theme(choice, values)

    def apply_theme(self, choice, values):
        self.public._theme, self.public._resolved = choice, values
        for node in self.nodes:
            node.styleChanged.emit()

    def system_changed(self, scheme):
        if self.public.theme == "system":
            try:
                values = _resolve("system", {Qt.ColorScheme.Light: "light", Qt.ColorScheme.Dark: "dark"}.get(scheme))
            except ThemeError as exc:
                message = f"{exc}; retaining previous appearance"
            else:
                self.apply_theme("system", values)
                return
            warnings.warn(message, RuntimeWarning, stacklevel=2)

    def warnings(self, warnings):
        for warning in warnings:
            self.errors.append(warning.toString())
            print(f"QML ERROR {warning.toString()}", file=sys.stderr, flush=True)

    def run(self):
        result = self.qt_app.exec()
        return 1 if self.errors else result

    def close(self):
        self.bridge.closeAnimations()
        self.window.close()
        self.hints.colorSchemeChanged.disconnect(self.system_changed)
        self.engine.deleteLater()
        # Destroy QML before bridge objects; include teardown in diagnostics.
        self.qt_app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        for node in self.nodes:
            node.value._runtime = None
            node.app = None
        shiboken6.delete(self.bridge)
        self.nodes.clear()
        self.root_node = None
        self.bridge.app = None
        self.qt_app.processEvents()
