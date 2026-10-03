"""Python-only application example and bounded Windows verification."""

import argparse
import platform
import sys
from pathlib import Path

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, QPoint, QPointF, Property, Qt, QTimer, Signal, Slot, qVersion
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import shiboken6

from model import Control, Pulse, Theme, Window


LIGHT = Theme()
DARK = Theme(surface="#252238", ink="#f8f5ff", accent="#466dbe", star="#82e0d1")
ROLES = ("controlId", "kind", "label", "fill", "pulseDuration", "pulsePeak")


class ControlModel(QAbstractListModel):
    def __init__(self, controls):
        super().__init__()
        self.controls = list(controls)
        self.role_ids = {name: Qt.ItemDataRole.UserRole + i for i, name in enumerate(ROLES)}

    def roleNames(self):
        return {value: name.encode() for name, value in self.role_ids.items()}

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.controls)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.controls):
            return None
        control = self.controls[index.row()]
        fields = {
            "controlId": control.id, "kind": control.kind, "label": control.text,
            "fill": control.fill or "", "pulseDuration": control.pulse.duration_ms if control.pulse else 0,
            "pulsePeak": control.pulse.peak_scale if control.pulse else 1.0,
        }
        return next((fields[name] for name, value in self.role_ids.items() if value == role), None)

    def add(self, control):
        row = len(self.controls)
        self.beginInsertRows(QModelIndex(), row, row)
        self.controls.append(control)
        self.endInsertRows()

    def remove(self, control_id):
        row = next(i for i, control in enumerate(self.controls) if control.id == control_id)
        self.beginRemoveRows(QModelIndex(), row, row)
        self.controls.pop(row)
        self.endRemoveRows()


class Bridge(QObject):
    themeChanged = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app

    @Property(str, notify=themeChanged)
    def surface(self):
        return self.app.theme.surface

    @Property(str, notify=themeChanged)
    def ink(self):
        return self.app.theme.ink

    @Property(str, notify=themeChanged)
    def accent(self):
        return self.app.theme.accent

    @Property(str, notify=themeChanged)
    def star(self):
        return self.app.theme.star

    @Property(int, constant=True)
    def initialWidth(self):
        return self.app.window.width

    @Property(int, constant=True)
    def initialHeight(self):
        return self.app.window.height

    @Property(str, constant=True)
    def title(self):
        return self.app.window.title

    @Slot(str)
    def activate(self, control_id):
        callback = self.app.callbacks.get(control_id)
        if callback is None:
            message = f"Unknown control ID: {control_id}"
            self.app.errors.append(message)
            print(f"BRIDGE ERROR {message}", flush=True)
            return
        try:
            callback()
        except Exception as exc:
            message = f"Callback {control_id}: {type(exc).__name__}: {exc}"
            self.app.errors.append(message)
            print(f"BRIDGE ERROR {message}", flush=True)


class App:
    def __init__(self, window, theme=LIGHT):
        self.window, self.theme = window, theme
        self.qt_app = QApplication.instance() or QApplication([])
        self.model = ControlModel(window.children)
        self.callbacks = {control.id: control.on_click for control in window.children}
        if len(self.callbacks) != len(window.children):
            raise ValueError("Control IDs must be unique")
        if any(control.kind not in ("button", "star") for control in window.children):
            raise ValueError("This spike supports button and star only")
        self.errors = []
        self.bridge = Bridge(self)
        QQuickStyle.setStyle("Basic")
        self.engine = QQmlApplicationEngine()
        self.engine.warnings.connect(self._warnings)
        self.engine.rootContext().setContextProperty("bridge", self.bridge)
        self.engine.rootContext().setContextProperty("controlsModel", self.model)
        self.engine.load(str(Path(__file__).with_name("Main.qml")))
        if not self.engine.rootObjects():
            raise RuntimeError("Internal QML failed to load; see QML warnings above")
        self.native_window = self.engine.rootObjects()[0]
        if not self.native_window.metaObject().inherits(QQuickWindow.staticMetaObject):
            raise RuntimeError("Internal QML root is not a QQuickWindow")
        self.quick_window = shiboken6.wrapInstance(shiboken6.getCppPointer(self.native_window)[0], QQuickWindow)

    def _warnings(self, warnings):
        for warning in warnings:
            message = warning.toString()
            self.errors.append(message)
            print(f"QML ERROR {message}", flush=True)

    def set_theme(self, theme):
        self.theme = theme
        self.bridge.themeChanged.emit()

    def add(self, control):
        if control.id in self.callbacks:
            raise ValueError(f"Duplicate control ID: {control.id}")
        if control.kind not in ("button", "star"):
            raise ValueError(f"Unsupported control type: {control.kind}")
        self.callbacks[control.id] = control.on_click
        self.model.add(control)

    def remove(self, control_id):
        self.model.remove(control_id)
        del self.callbacks[control_id]

    def run(self):
        return self.qt_app.exec()


def build_app():
    counts = {}
    app_ref = []

    def callback(control_id, switch_theme=False):
        def clicked():
            counts[control_id] = counts.get(control_id, 0) + 1
            if switch_theme:
                app = app_ref[0]
                app.set_theme(DARK if app.theme is LIGHT else LIGHT)
            print(f"ACTIVATE id={control_id} count={counts[control_id]}", flush=True)
        return clicked

    controls = (
        Control("theme", "button", "Change theme", callback("theme", True), pulse=Pulse()),
        Control("orange", "button", "A long label that wraps to two lines when the window becomes narrow", callback("orange"), fill="#d86642"),
        Control("third", "button", "Third independent button", callback("third")),
        Control("star", "star", "", callback("star")),
    )
    app = App(Window("QML controls and dynamic Python tree", controls))
    app_ref.append(app)
    return app, counts, callback


def probe(app, counts, callback):
    window = app.native_window
    failures = []

    def control(index):
        item = window.controlAt(index)
        if item is None:
            raise RuntimeError(f"QML control missing at index {index}")
        return item

    def click(index, x=None, y=None):
        window.scrollTo(index)
        app.qt_app.processEvents()
        item = control(index)
        local = QPointF(x if x is not None else item.width() / 2, y if y is not None else item.height() / 2)
        point = item.mapToScene(local)
        QTest.mouseClick(window, Qt.MouseButton.LeftButton, pos=QPoint(round(point.x()), round(point.y())))
        app.qt_app.processEvents()

    def check(name, actual, expected):
        passed = actual == expected
        print(f"CHECK {name} actual={actual!r} expected={expected!r} pass={passed}", flush=True)
        if not passed:
            failures.append(name)

    def save(name):
        path = Path(__file__).with_name(name)
        saved = app.quick_window.grabWindow().save(str(path))
        print(f"CAPTURE {path.name} saved={saved}", flush=True)
        if not saved:
            failures.append(name)

    def initial():
        print(f"INITIAL visible={window.isVisible()} size={window.width()}x{window.height()} count={app.model.rowCount()}", flush=True)
        check("visible", window.isVisible(), True)
        check("initial-count", app.model.rowCount(), 4)
        save("initial.png")
        click(0)
        click(1)
        click(2)
        click(3, 50, 45)
        click(3, 2, 2)
        check("distinct-callbacks", [counts.get(i, 0) for i in ("theme", "orange", "third", "star")], [1, 1, 1, 1])
        print(f"THEME surface={app.theme.surface} override={app.model.controls[1].fill} scale={control(0).scale():.3f}", flush=True)
        window.resize(300, 500)
        QTimer.singleShot(250, narrow)

    def narrow():
        print(f"NARROW size={window.width()}x{window.height()} button-width={control(1).width():.1f} scale={control(0).scale():.3f}", flush=True)
        save("narrow.png")
        new = Control("dynamic", "button", "Added after showing", callback("dynamic"))
        app.add(new)
        app.qt_app.processEvents()
        check("dynamic-added", app.model.rowCount(), 5)
        click(4)
        click(2)
        check("dynamic-and-existing", [counts.get("dynamic", 0), counts.get("third", 0)], [1, 2])
        app.remove("dynamic")
        app.qt_app.processEvents()
        check("dynamic-removed", app.model.rowCount(), 4)
        click(2)
        check("after-remove", counts.get("third", 0), 3)
        for i in range(50):
            key = f"repeat-{i:02}"
            app.add(Control(key, "button", f"Repeated control {i:02}", callback(key)))
        QTimer.singleShot(250, repeated)

    def repeated():
        check("repeated-count", app.model.rowCount(), 54)
        click(4)
        click(53)
        check("repeated-interaction", [counts.get("repeat-00", 0), counts.get("repeat-49", 0)], [1, 1])
        print(f"REPEATED count={app.model.rowCount()} first={counts.get('repeat-00')} last={counts.get('repeat-49')} errors={len(app.errors)}", flush=True)
        save("repeated.png")
        check("qml-errors", len(app.errors), 0)
        QTimer.singleShot(100, finish)

    def finish():
        window.close()
        window.deleteLater()
        app.qt_app.processEvents()
        print(f"RESULT failures={failures}", flush=True)
        app.qt_app.exit(1 if failures else 0)

    QTimer.singleShot(300, initial)
    return app.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    print(f"ENV platform={platform.platform()} python={sys.version.split()[0]} PySide6={pyside_version} Qt={qVersion()}", flush=True)
    app, counts, callback = build_app()
    return probe(app, counts, callback) if args.probe else app.run()


if __name__ == "__main__":
    raise SystemExit(main())
