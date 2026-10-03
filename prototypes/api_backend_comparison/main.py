"""Matched application example and bounded Windows verification probe."""

import argparse
import platform
import sys
from pathlib import Path

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QPoint, QPointF, QTimer, Qt, qVersion
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from model import Button, Label, Pulse, Star, Theme, Window


LIGHT = Theme()
DARK = Theme(surface="#252238", ink="#f8f5ff", accent="#466dbe", star="#82e0d1")


class App:
    def __init__(self, window, theme=LIGHT):
        self.window, self.theme = window, theme
        self.qt_app = QApplication.instance() or QApplication([])
        self.callbacks = {type(spec).__name__.lower(): spec.on_click for spec in window.children if hasattr(spec, "on_click")}
        self.backend = None

    def set_theme(self, theme):
        self.theme = theme
        self.backend.set_theme()

    def start(self, backend_name):
        from direct import Backend as DirectBackend
        from qml_backend import Backend as QmlBackend
        self.backend = (DirectBackend if backend_name == "direct" else QmlBackend)(self)

    def run(self, backend_name):
        self.start(backend_name)
        return self.qt_app.exec()


def build_app():
    counts = {"button": 0, "star": 0}
    app = None

    def button_clicked():
        counts["button"] += 1
        app.set_theme(DARK if app.theme is LIGHT else LIGHT)
        print(f"BUTTON count={counts['button']} theme={app.theme.surface}", flush=True)

    def star_clicked():
        counts["star"] += 1
        print(f"STAR count={counts['star']}", flush=True)

    window = Window("Backend comparison", (
        Label("Python-authored Qt Quick UI"),
        Button("Change theme", button_clicked, fill="#d86642", pulse=Pulse()),
        Star(star_clicked),
    ))
    app = App(window)
    return app, counts


def probe(app, counts, backend_name):
    window, items = app.backend.window, app.backend.items

    def geometry():
        return {name: (round(item.mapToScene(QPointF(0, 0)).x()),
                       round(item.mapToScene(QPointF(0, 0)).y()),
                       round(item.width()), round(item.height())) for name, item in items.items()}

    def click(item, dx, dy):
        point = item.mapToScene(QPointF(dx, dy))
        QTest.mouseClick(window, Qt.MouseButton.LeftButton,
                         pos=QPoint(round(point.x()), round(point.y())))

    def begin():
        print(f"INITIAL visible={window.isVisible()} size={window.width()}x{window.height()} geometry={geometry()} scale={items['button'].scale():.3f}", flush=True)
        click(items["button"], 1, 1)
        click(items["button"], 100, 26)
        click(items["star"], 60, 30)
        click(items["star"], 10, 10)
        print(f"INPUT counts={counts} theme={app.theme.surface} override={app.window.children[1].fill}", flush=True)
        window.resize(600, 400)
        QTimer.singleShot(150, resized)

    def resized():
        print(f"RESIZED size={window.width()}x{window.height()} geometry={geometry()} scale={items['button'].scale():.3f}", flush=True)
        # Key activation is exercised separately from synthesized mouse input.
        items["button"].forceActiveFocus()
        QTest.keyClick(window, Qt.Key.Key_Space)
        print(f"KEY counts={counts} theme={app.theme.surface}", flush=True)
        QTimer.singleShot(100, app.qt_app.quit)

    QTimer.singleShot(250, begin)
    return app.qt_app.exec()


def capture(app, backend_name):
    window = app.backend.window

    def save(stage):
        path = Path(__file__).with_name(f"{backend_name}-{stage}.png")
        print(f"CAPTURE {path.name} saved={window.grabWindow().save(str(path))}", flush=True)

    def initial():
        save("initial")
        app.set_theme(DARK)
        window.resize(600, 400)
        QTimer.singleShot(250, resized)

    def resized():
        save("resized")
        app.qt_app.quit()

    QTimer.singleShot(250, initial)
    return app.qt_app.exec()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("direct", "qml"), required=True)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    app, counts = build_app()
    print(f"ENV platform={platform.platform()} python={sys.version.split()[0]} PySide6={pyside_version} Qt={qVersion()}", flush=True)
    app.start(args.backend)
    if args.probe:
        return probe(app, counts, args.backend)
    if args.capture:
        return capture(app, args.backend)
    return app.qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
