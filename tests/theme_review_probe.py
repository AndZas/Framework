"""Windows render evidence for TASK-0010 owner follow-up; synthetic Qt input."""
import argparse
import csv
import json
import platform
import runpy
import sys
import traceback
from pathlib import Path

import PySide6
from PySide6.QtCore import QObject, QPoint, QPointF, Qt, QTimer, qInstallMessageHandler, qVersion
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtTest import QTest
from pyui_framework import Button, Label, Theme


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    studio = runpy.run_path(str(root / "examples/themes.py"))
    reload_path = output / "reload.theme"
    reload_path.write_text((root / "examples/lagoon.theme").read_text(encoding="utf-8"), encoding="utf-8")
    messages = []
    previous = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    qt = QApplication([])
    app = studio["build"](reload_path)
    report = dict(environment=dict(platform=platform.platform(), python=sys.version,
                                   PySide6=PySide6.__version__, Qt=qVersion()),
                  checks=[], failures=[], profiles={}, opacity=[], physical_input=False)
    runtimes = []
    # Test-only solid native backdrop; the studio still renders through Qt Quick.
    backdrop = QWidget()
    backdrop.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
    palette = backdrop.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#ff00ff"))
    backdrop.setPalette(palette)
    backdrop.setAutoFillBackground(True)

    def exercise():
        rt = app._runtime
        runtimes.append(rt)
        screen = qt.primaryScreen()
        rt.window.setScreen(screen)
        rt.window.setFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        rt.window.show()
        area = screen.availableGeometry()
        rt.window.setPosition(area.x()+50, area.y()+60)
        backdrop.setGeometry(rt.window.x()-10, rt.window.y()-10, rt.window.width()+20, rt.window.height()+20)
        backdrop.show()
        rt.window.raise_()
        rt.window.requestActivate()
        QTest.qWait(250)
        report["environment"].update(graphics_api=rt.quick.rendererInterface().graphicsApi().name,
                                     window_dpr=rt.window.devicePixelRatio(), screen_depth=screen.depth())

        def check(name, condition):
            report["checks"].append(name)
            assert condition, name

        def node(value):
            return next(n for n in rt.nodes if n.value is value)

        def visual(value):
            name = node(value).nodeId
            def find(parent):
                if parent.objectName() == name:
                    return parent
                for child in parent.childItems():
                    found = find(child)
                    if found is not None:
                        return found
            return find(rt.quick.contentItem())

        sample = next(n.value for n in rt.nodes if isinstance(n.value, Button) and n.value.text == "Inherited sample")
        heading = next(n.value for n in rt.nodes if isinstance(n.value, Label) and n.value.heading)
        original = visual(sample)

        def settle():
            visual(heading).forceActiveFocus()
            QTest.mouseMove(rt.window, QPoint(5, 5))
            QTest.qWait(150)

        def image(name):
            settle()
            result = rt.quick.grabWindow()
            check("capture " + name, result.save(str(output / (name + ".png"))))
            return result

        def rgb(color):
            return [color.red(), color.green(), color.blue()]

        def label_surface(frame):
            item = visual(heading)
            p = item.mapToScene(QPointF(item.width()-30, item.height()/2))
            return frame.pixelColor(round(p.x()*frame.devicePixelRatio()), round(p.y()*frame.devicePixelRatio())).name()

        def click(text):
            value = next(n.value for n in rt.nodes if isinstance(n.value, Button) and n.value.text == text)
            item = visual(value)
            viewport = rt.window.findChild(QObject, "viewport")
            # Studio controls above the sample are visible at 800x760.
            viewport.setProperty("contentY", 0)
            QTest.qWait(50)
            p = item.mapToScene(QPointF(item.width()/2, item.height()/2))
            check("click visible " + text, 20 <= p.y() <= rt.window.height()-20)
            QTest.mouseClick(rt.window, Qt.MouseButton.LeftButton, pos=QPoint(round(p.x()), round(p.y())))
            QTest.qWait(120)

        def profile(name, theme):
            app.set_theme(theme)
            frame = image(name)
            item = visual(sample)
            check("retained gradient control " + name, item is original)
            values = node(sample).appearance
            stops = app.resolved_theme["gradient"]
            check("resolved gradient stops " + name, (values["gradientStart"], values["gradientEnd"]) == stops)
            dpr = frame.devicePixelRatio()
            top_left = item.mapToScene(QPointF())
            left = top_left.x()*dpr
            width = item.width()*dpr
            y = round((top_left.y()+6)*dpr)  # no text, border or rounded-edge antialiasing
            start, end = rgb(QColor(stops[0])), rgb(QColor(stops[1]))
            pixels = []
            rows = []
            for x in range(round(left+30*dpr), round(left+width-30*dpr)):
                actual = rgb(frame.pixelColor(x, y))
                t = (x+.5-left)/width
                expected = [a+(b-a)*t for a, b in zip(start, end)]
                pixels.append(actual)
                rows.append([x, y, t, *actual, *expected])
            max_error = max(abs(row[3+c]-row[6+c]) for row in rows for c in range(3))
            steps = [max(abs(a-b) for a, b in zip(p, q)) for p, q in zip(pixels, pixels[1:])]
            longest = count = 1
            for p, q in zip(pixels, pixels[1:]):
                count = count+1 if p == q else 1
                longest = max(longest, count)
            monotonic = all(all((q[c]-p[c])*(end[c]-start[c]) >= 0 for c in range(3))
                            for p, q in zip(pixels, pixels[1:]))
            with (output / (name + "-profile.csv")).open("w", newline="", encoding="utf-8") as target:
                writer = csv.writer(target)
                writer.writerow(["x", "y", "t", "r", "g", "b", "ideal_r", "ideal_g", "ideal_b"])
                writer.writerows(rows)
            report["profiles"][name] = dict(stops=stops, physical_width=width, sample_count=len(rows),
                image_format=frame.format().name, image_depth=frame.depth(), unique_rgb=len({tuple(p) for p in pixels}),
                max_flat_run=longest, max_neighbor_step=max(steps), max_linear_error=max_error,
                monotonic=monotonic, first=pixels[0], last=pixels[-1])
            # Qt's Rectangle mesh interpolates byte vertex colors, then the
            # framebuffer quantizes again: allow <=2 of 255, not coarse bands.
            check("linear interpolation " + name, max_error <= 2 and max(steps) <= 1 and monotonic)
            return frame

        try:
            for choice in ("light", "dark", "system"):
                app.set_theme(choice)
                frame = image(choice + "-labels")
                check("built-in Label blends " + choice, label_surface(frame) == rt.window.color().name())
            panel = Theme("Explicit panel", **(studio["MIDNIGHT"].tokens | {"gradient": None}))
            app.set_theme(panel)
            frame = image("explicit-panel")
            check("explicit custom panel preserved", label_surface(frame) == "#24263a" and rt.window.color().name() == "#171827")
            heading.set_style(panel="#36495b")
            frame = image("local-panel")
            check("local panel preserved", label_surface(frame) == "#36495b")
            heading.set_style()
            app.set_theme(studio["CUSTOM"])
            check("shipped Lagoon opaque and equivalent", studio["CUSTOM"].tokens == Theme.load(root / "examples/lagoon.theme").tokens and app.resolved_theme["opacity"] == 1)
            for opacity in (.94, 1.):
                for source in ("file", "python"):
                    tokens = studio["CUSTOM"].tokens | {"opacity": opacity}
                    if source == "file":
                        reload_path.write_text((root / "examples/lagoon.theme").read_text(encoding="utf-8").replace("opacity: 1;", f"opacity: {opacity};"), encoding="utf-8")
                        click("Load / reload file")
                    else:
                        app.set_theme(Theme("Lagoon opacity", **tokens))
                    settle()
                    check("explicit theme opacity reaches Window", abs(rt.window.opacity()-opacity) < .001)
                    check("explicit theme opacity reaches Button", abs(visual(sample).opacity()-opacity) < .001)
                    # Limit the desktop read to this application's client rectangle.
                    p = rt.window.mapToGlobal(QPoint())
                    composed = screen.grabWindow(0, p.x(), p.y(), rt.window.width(), rt.window.height()).toImage()
                    check("screen client capture", not composed.isNull())
                    name = f"lagoon-{source}-opacity-{opacity:g}"
                    color = composed.pixelColor(round(10*composed.devicePixelRatio()), round(10*composed.devicePixelRatio()))
                    expected = [a*opacity+b*(1-opacity) for a, b in zip(rgb(QColor("#eaf5f2")), rgb(QColor("#ff00ff")))]
                    report["opacity"].append(dict(source=source, requested=opacity, window=rt.window.opacity(),
                        button=visual(sample).opacity(), composed=rgb(color), ideal_over_magenta=expected))
                    check("desktop compositing " + name, max(abs(a-b) for a, b in zip(rgb(color), expected)) <= 2)
                    check("capture " + name, composed.save(str(output / (name + ".png"))))
            app.set_theme(studio["CUSTOM"])
            for text, expected in (("Window opacity 0.94", .94), ("Window opacity 1.0", 1), ("Clear window opacity", 1)):
                click(text)
                check("window-only opacity callback " + text, abs(rt.window.opacity()-expected) < .001 and visual(sample).opacity() == 1)
            check("window opacity clear callback", app._window.style == {})
            lagoon = profile("lagoon-gradient", Theme.load(root / "examples/lagoon.theme"))
            check("Lagoon file/Python rendering", lagoon == profile("lagoon-python-gradient", studio["CUSTOM"]))
            midnight_path = root / "prototypes/theme_api_spike/midnight.theme"
            midnight = Theme.load(midnight_path)
            check("Midnight file/Python tokens", midnight.tokens == studio["MIDNIGHT"].tokens)
            file_frame = profile("midnight-file", midnight)
            check("Midnight file/Python rendering", file_frame == profile("midnight-python", studio["MIDNIGHT"]))
            profile("midnight-square", Theme("Midnight square comparison", **(midnight.tokens | {"radius": 0})))
            # A shorter button tests whether flat runs scale with spatial sampling.
            rt.window.resize(440, 760)
            QTest.qWait(180)
            profile("midnight-narrow", midnight)
            check("no Qt/QML diagnostics", not messages and not rt.errors)
        except Exception:
            report["failures"].append(traceback.format_exc())
            traceback.print_exc()
        finally:
            backdrop.close()
            qt.exit(1 if report["failures"] else 0)

    QTimer.singleShot(500, exercise)
    result = app.run()
    report["qt_messages"] = messages
    report["qml_errors"] = runtimes[0].errors
    (output / "review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    qInstallMessageHandler(previous)
    print(json.dumps({"checks": len(report["checks"]), "failures": report["failures"],
                      "qt_messages": messages, "profiles": report["profiles"], "opacity": report["opacity"]}), flush=True)
    return result or int(bool(messages or report["qml_errors"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    raise SystemExit(run(parser.parse_args().output.resolve()))
