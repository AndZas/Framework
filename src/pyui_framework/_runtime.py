"""Internal Qt adaptation. Author examples never depend on these objects."""
from pathlib import Path
import sys
import traceback

import shiboken6
from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Property, Qt, Signal, Slot, QThread
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtGui import QGuiApplication

from ._model import Button, Column, Label, Row, Window


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

    def __init__(self, value, app):
        super().__init__(app.bridge)
        self.value, self.app = value, app
        kinds = {Window: "column", Column: "column", Row: "row", Label: "label", Button: "button"}
        if type(value) not in kinds:
            raise TypeError(f"Unsupported experimental node: {type(value).__name__}")
        self._kind = kinds[type(value)]
        self._id = f"node-{len(app.nodes)}"
        app.nodes.append(self)
        self.model = Children(self)
        if hasattr(value, "children"):
            for child in value.children:
                self.model.append(Node(child, app))
            value._runtime = self
        if isinstance(value, Label):
            value._runtime = self

    def check_thread(self):
        if QThread.currentThread() != self.thread():
            raise RuntimeError('UI updates must run on the application thread')

    def append(self, child):
        self.model.append(Node(child, self.app))

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


class Bridge(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app

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
    def __init__(self, window):
        self.qt_app = QGuiApplication.instance() or QGuiApplication([])
        self.errors, self.nodes = [], []
        self.bridge = Bridge(self)
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
            raise RuntimeError("Internal QML load failed: " + "\n".join(self.errors))
        self.window = self.engine.rootObjects()[0]
        self.quick = shiboken6.wrapInstance(shiboken6.getCppPointer(self.window)[0], QQuickWindow)

    def warnings(self, warnings):
        for warning in warnings:
            self.errors.append(warning.toString())
            print(f"QML ERROR {warning.toString()}", file=sys.stderr, flush=True)

    def run(self):
        result = self.qt_app.exec()
        return 1 if self.errors else result

    def close(self):
        self.window.close()
        for node in self.nodes:
            node.value._runtime = None
        self.engine.deleteLater()
        self.qt_app.processEvents()
