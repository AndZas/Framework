"""App-authored Python example; --probe exercises the requested scenarios."""

import argparse
import platform
import sys
from pathlib import Path

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QPoint, QTimer, Qt, qVersion
from PySide6.QtTest import QTest

from api import App, Button, Pulse, Star, Theme, Window


LIGHT = Theme()
DARK = Theme(surface="#252238", ink="#f8f5ff", accent="#466dbe", accent_end="#284e80", star="#82e0d1")


def build_app():
    app = App(theme=LIGHT)
    counts = {"button": 0, "star": 0}

    def clicked():
        counts["button"] += 1
        print(f"BUTTON callback count={counts['button']}", flush=True)

    def switch_theme():
        app.set_theme(DARK if app.theme is LIGHT else LIGHT)
        print(f"THEME surface={app.theme.surface}", flush=True)

    def star_clicked():
        counts["star"] += 1
        print(f"STAR callback count={counts['star']}", flush=True)

    main = app.add(Window(title="Python API spike"))
    button = main.add(Button("Click me", on_click=clicked, pulse=Pulse()))
    theme_button = main.add(Button("Change theme", on_click=switch_theme))
    override = main.add(Button("Orange override", fill="#d86642"))
    star = main.add(Star(on_click=star_clicked))
    secondary = app.add(Window(title="Second Python window", width=310, height=170))
    secondary.add(Button("Independent window"))
    return app, main, secondary, button, theme_button, override, star, counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    app, main_window, second_window, button, theme_button, override, star, counts = build_app()
    print(f"ENV platform={platform.platform()} python={sys.version.split()[0]} PySide6={pyside_version} Qt={qVersion()}", flush=True)
    if not args.probe:
        return app.run()

    app.start()
    print(f"WINDOWS count={len(app.windows)} distinct={main_window.native is not second_window.native} visible={main_window.native.isVisible() and second_window.native.isVisible()}", flush=True)

    def capture(name):
        path = Path(__file__).with_name(name)
        saved = main_window.native.grabWindow().save(str(path))
        print(f"CAPTURE {name} saved={saved}", flush=True)

    def probe():
        native = main_window.native
        QTest.mouseClick(native, Qt.MouseButton.LeftButton, pos=QPoint(int(button.x() + 110), int(button.y() + 24)))
        rounded_inside = counts["button"]
        QTest.mouseClick(native, Qt.MouseButton.LeftButton, pos=QPoint(int(button.x() + 1), int(button.y() + 1)))
        rounded_after_corner = counts["button"]
        QTest.mouseClick(native, Qt.MouseButton.LeftButton, pos=QPoint(int(theme_button.x() + 110), int(theme_button.y() + 24)))
        QTest.mouseClick(native, Qt.MouseButton.LeftButton, pos=QPoint(int(star.x() + 60), int(star.y() + 30)))
        star_inside = counts["star"]
        QTest.mouseClick(native, Qt.MouseButton.LeftButton, pos=QPoint(int(star.x() + 10), int(star.y() + 10)))
        star_after_corner = counts["star"]
        print(f"PROBE rounded_inside={rounded_inside} rounded_after_corner={rounded_after_corner} star_inside={star_inside} star_after_corner={star_after_corner} dark={app.theme is DARK} override={override.fill} scale={button.scale():.3f}", flush=True)
        QTimer.singleShot(50, lambda: capture("probe-dark.png"))
        QTimer.singleShot(160, finish)

    def finish():
        print(f"ANIMATION scale_later={button.scale():.3f}", flush=True)
        app.qt_app.quit()

    QTimer.singleShot(200, lambda: capture("probe-light.png"))
    QTimer.singleShot(600, probe)
    return app.qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
