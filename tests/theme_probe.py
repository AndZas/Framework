"""Visible Windows theme verification using synthetic Qt input, never OS settings."""
import argparse
import json
import platform
import runpy
import sys
import traceback
import warnings
from pathlib import Path
from unittest.mock import patch
import PySide6
from PySide6.QtCore import QObject, QPoint, QPointF, Qt, QTimer, qVersion, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
from pyui_framework import App, Button, Label, Theme, ThemeError


def main(mode, output):
    messages = []
    previous_handler = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    qt_app = QGuiApplication([])
    root = Path(__file__).resolve().parents[1]
    studio = runpy.run_path(str(root / "examples/themes.py"))
    output.mkdir(parents=True, exist_ok=True)
    reload_path = output / "reload.theme"
    reload_path.write_text((root / "examples/lagoon.theme").read_text(encoding="utf-8"), encoding="utf-8")
    app = studio["build"](reload_path) if mode == "studio" else App(runpy.run_path(str(root / "examples/hello.py"))["build"]())
    window = app._window
    evidence = dict(environment=dict(platform=platform.platform(), python=sys.version,
                                     PySide6=PySide6.__version__, Qt=qVersion()), app=mode,
                    checks=[], failures=[], system_os_transition="unverified")
    runtimes = []

    def exercise():
        rt = app._runtime
        runtimes.append(rt)
        viewport = rt.window.findChild(QObject, "viewport")
        bar = rt.window.findChild(QObject, "verticalScrollBar")

        def check(name, condition):
            evidence["checks"].append(name)
            assert condition, name

        def node(value):
            return next(n for n in rt.nodes if n.value is value)

        def item(value):
            name = node(value).nodeId
            def find(parent):
                if parent.objectName() == name:
                    return parent
                for child in parent.childItems():
                    result = find(child)
                    if result is not None:
                        return result
            return find(rt.quick.contentItem())

        def click(text):
            value = next(n.value for n in rt.nodes if isinstance(n.value, Button) and n.value.text == text)
            visual = item(value)
            # Reveal action with actual wheel input before delivering its click.
            QTest.wheelEvent(rt.window, QPoint(30, 40), QPoint(0, 3600))
            QTest.qWait(100)
            for _ in range(30):
                p = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
                if 20 <= p.y() <= rt.window.height() - 20:
                    break
                QTest.wheelEvent(rt.window, QPoint(30, 40), QPoint(0, -120))
                QTest.qWait(35)
            p = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
            check("action visible: " + text, 20 <= p.y() <= rt.window.height()-20)
            QTest.mouseClick(rt.window, Qt.MouseButton.LeftButton, pos=QPoint(round(p.x()), round(p.y())))
            QTest.qWait(80)

        def capture(name):
            image = rt.quick.grabWindow()
            check("capture " + name, image.save(str(output / (name + ".png"))))
            return image

        def assert_error(operation, fragment):
            before = app.resolved_theme, [getattr(n.value, "style", {}) for n in rt.nodes]
            image = rt.quick.grabWindow()
            try:
                operation()
            except ThemeError as exc:
                check("error source " + fragment, fragment in str(exc))
                evidence.setdefault("invalid_inputs", []).append(str(exc))
            else:
                raise AssertionError("expected ThemeError")
            QTest.qWait(40)
            check("rollback " + fragment, before == (app.resolved_theme, [getattr(n.value, "style", {}) for n in rt.nodes]))
            check("visible rollback " + fragment, image == rt.quick.grabWindow())

        try:
            check("visible window", rt.window.isVisible())
            capture("default")
            local = next(n.value for n in rt.nodes if isinstance(n.value, Button) and (mode != "studio" or n.value.text == "Local sample"))
            label = next(n.value for n in rt.nodes if isinstance(n.value, Label))
            old_item, old_window = item(local), rt.window
            initial_style = dict(accent="#b36a17", accent_text="#ffffff", radius=24, gradient=None)
            local.set_style(**initial_style)
            label.set_style(foreground="#aa3344", opacity=.8)
            for choice in ("light", "dark", "system", studio["CUSTOM"], Theme.load(root / "examples/lagoon.theme")):
                app.set_theme(choice)
                QTest.qWait(80)
                check("persistent identity and override", item(local) is old_item and rt.window is old_window and local.style == initial_style)
                check("resolved precedence", node(local).appearance["accent"] == "#b36a17" and node(label).appearance["foreground"] == "#aa3344")
            app.set_theme("dark")
            QTest.qWait(80)
            capture("dark-local")
            label.set_style()
            local.set_style()
            QTest.qWait(80)
            check("clear inheritance", node(local).appearance["accent"] == app.resolved_theme["accent"])
            check("visible Label inheritance", item(label).property("color").name() == app.resolved_theme["foreground"])
            app.set_theme(Theme.load(root / "examples/lagoon.theme"))
            QTest.qWait(80)
            file_image = capture("file")
            app.set_theme(studio["CUSTOM"])
            QTest.qWait(80)
            check("file Python pixels equal", file_image == capture("python"))
            # Framework APIs must reject worker-thread mutation before changing state.
            from threading import Thread
            thread_errors = []
            def worker():
                for operation in (lambda: app.set_theme("light"), lambda: local.set_style(radius=2),
                                  lambda: label.set_style(opacity=.2), lambda: window.set_style(opacity=.2)):
                    try:
                        operation()
                    except RuntimeError as exc:
                        thread_errors.append(str(exc))
            before_thread = app.resolved_theme, local.style, label.style, window.style
            thread = Thread(target=worker)
            thread.start()
            thread.join()
            check("worker-thread mutation rejected atomically", len(thread_errors) == 4 and
                  before_thread == (app.resolved_theme, local.style, label.style, window.style))
            for text, fragment in [
                (":theme { radius: 2px; }", "radius"),
                (":theme { nope: #123456; }", "nope"),
                (":theme { opacity: 2; }", "opacity"),
                (":theme { accent: red; }", "accent"),
                (":theme { accent: #123456 }", "semicolon"),
            ]:
                assert_error(lambda t=text: app.set_theme(Theme.parse(t, source="invalid.theme")), fragment)
            assert_error(lambda: app.set_theme(Theme.load(output / "missing.theme")), "missing.theme")
            assert_error(lambda: app.set_theme("invalid"), "App theme")
            assert_error(lambda: local.set_style(accent="#123456", opacity=2), "Button style")
            assert_error(lambda: label.set_style(foreground=12), "Label style")
            assert_error(lambda: window.set_style(opacity=-1), "Window style")
            window.set_style(background="#345678", opacity=1)
            check("window local style", rt.window.color().name() == "#345678")
            app.set_theme("light")
            QTest.qWait(80)
            check("window local persistence, no child cascade", rt.window.color().name() == "#345678" and
                  item(label).property("color").name() == app.resolved_theme["foreground"])
            window.set_style()
            check("window clear inheritance", rt.window.color().name() == app.resolved_theme["background"])
            app.set_theme("system")
            evidence["initial_system_scheme"] = rt.hints.colorScheme().name
            for scheme in (Qt.ColorScheme.Light, Qt.ColorScheme.Dark, Qt.ColorScheme.Light):
                rt.hints.setColorScheme(scheme)
                QTest.qWait(100)
                check("Qt scheme override accepted " + scheme.name, rt.hints.colorScheme() == scheme)
                check("live System " + scheme.name, app.resolved_theme == __import__("pyui_framework.theme", fromlist=["_resolve"])._resolve(scheme.name.lower()))
            rt.hints.unsetColorScheme()
            QTest.qWait(100)
            with patch.object(rt, "system_scheme", return_value=None):
                app.set_theme("light")
                assert_error(lambda: app.set_theme("system"), "Unknown")
            app.set_theme("system")
            before = app.resolved_theme
            with warnings.catch_warnings(record=True) as seen:
                warnings.simplefilter("always", RuntimeWarning)
                rt.hints.colorSchemeChanged.emit(Qt.ColorScheme.Unknown)
            check("Unknown notification preserves palette and reports", app.resolved_theme == before and len(seen) == 1)
            app.set_theme("dark")
            dynamic = window.add(Button("Dynamic themed control", on_click=lambda: None))
            QTest.qWait(80)
            check("live inserted control inherits", node(dynamic).appearance["accent"] == app.resolved_theme["accent"])
            if mode == "studio":
                for text in ("Light", "Dark", "System", "Load / reload file", "Python theme", "Replace local style"):
                    click(text)
                check("replace callback", local.style["accent"] == "#874bb5")
                click("Dark")
                check("local persists after UI switch", local.style["accent"] == "#874bb5")
                click("Clear local style")
                check("clear callback", local.style == {})
                for invalid in (":theme { accent: red; }", ":theme { opacity: 2; }",
                                ":theme { nope: 1; }", ":theme { radius: 3px; }"):
                    before = app.resolved_theme
                    reload_path.write_text(invalid, encoding="utf-8")
                    click("Load / reload file")
                    check("invalid reload UI preserves active theme", app.resolved_theme == before)
                    check("invalid reload UI reports source", any(isinstance(n.value, Label) and
                          "Unchanged appearance:" in n.value.text and "reload.theme:1:" in n.value.text for n in rt.nodes))
                reload_path.write_text((root / "examples/lagoon.theme").read_text(encoding="utf-8"), encoding="utf-8")
                click("Load / reload file")
                check("valid reload UI recovers", app.resolved_theme == __import__("pyui_framework.theme", fromlist=["_resolve"])._resolve(studio["CUSTOM"]))
            else:
                click("Save")
                click("Reset")
                click("Add a live action")
            # Preserve the edge-scroll contract at ordinary and minimum client sizes.
            app.set_theme("dark")
            for width, height in ((window.width, window.height), (280, 260)):
                rt.window.resize(width, height)
                QTest.qWait(160)
                check("edge scrollbar", abs(bar.x()+bar.width()-width) < .1 and bar.y() == 0 and bar.height() == height)
                check("viewport margins", viewport.x() == 20 and viewport.width() == width-40)
                check("no scrollbar overlap", bar.x() >= viewport.x()+viewport.width())
                QTest.wheelEvent(rt.window, QPoint(40, 80), QPoint(0, -720))
                QTest.qWait(180)
                if height == 260:
                    check("wheel scroll", viewport.property("contentY") > 0)
                    # Real thumb drag to bottom.
                    thumb = next(c for c in bar.childItems() if c.width() > 0 and c.height() > 0 and c.height() < bar.height())
                    p = thumb.mapToScene(QPointF(thumb.width()/2, thumb.height()/2))
                    QTest.mousePress(rt.window, Qt.MouseButton.LeftButton, pos=QPoint(round(p.x()), round(p.y())))
                    QTest.mouseMove(rt.window, QPoint(round(p.x()), height-5), 60)
                    QTest.mouseRelease(rt.window, Qt.MouseButton.LeftButton, pos=QPoint(round(p.x()), height-5))
                    QTest.qWait(120)
                    check("thumb drag to bottom", abs(viewport.property("contentY") - max(0, viewport.property("contentHeight")-viewport.height())) < 2)
                capture(f"dark-{width}x{height}-scrolled")
            check("no Qt diagnostics", not rt.errors)
            evidence["errors"] = rt.errors
        except Exception:
            evidence["failures"].append(traceback.format_exc())
            traceback.print_exc()
        finally:
            rt.hints.unsetColorScheme()
            qt_app.exit(1 if evidence["failures"] or rt.errors or messages else 0)

    QTimer.singleShot(400, exercise)
    result = app.run()
    # Record diagnostics after the normal public lifecycle tears down QML.
    evidence["errors"] = runtimes[0].errors
    evidence["qt_messages"] = messages
    (output / "probe.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps({"checks": len(evidence["checks"]), "failures": evidence["failures"], "errors": evidence["errors"], "qt_messages": messages}), flush=True)
    qInstallMessageHandler(previous_handler)
    return result or int(bool(messages or evidence["errors"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", choices=("ordinary", "studio"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.app, args.output.resolve()))
