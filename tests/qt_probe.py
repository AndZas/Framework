"""Visible synthetic probe; also runs against the installed wheel."""
import json
import platform
import sys
import traceback
from pathlib import Path

import PySide6
from PySide6.QtCore import QObject, QPoint, QPointF, Qt, QTimer, qVersion
from PySide6.QtTest import QTest
from PySide6.QtGui import QGuiApplication
from pyui_framework import App, Button, Column, Label, Row, Window
import pyui_framework


def main(output):
    qt_app = QGuiApplication([])
    output.mkdir(parents=True, exist_ok=True)
    counts = [0, 0, 0]
    def count(index):
        counts[index] += 1
    long = Label("A longer explanation demonstrates responsive word wrapping as the available window width changes. Controls should remain readable and usable in narrow windows.")
    first = Button("Save", on_click=lambda: count(0))
    second = Button("Reset", on_click=lambda: count(1))
    body = Column(Label("Live controls"))
    window = Window("Core slice Qt verification", Label("Python UI", heading=True), long, Row(first, second), body)
    app = App(window)
    evidence = {"environment": {"platform": platform.platform(), "python": sys.version,
                "PySide6": PySide6.__version__, "Qt": qVersion()},
                "package": pyui_framework.__file__, "layouts": {}, "failures": []}
    def check(name, condition):
        if not condition:
            evidence["failures"].append(name)
        print(f"CHECK {name}: {bool(condition)}", flush=True)

    def exercise():
        runtime = app._runtime
        def item(value):
            node = next(n for n in runtime.nodes if n.value is value)
            def find(root):
                if root.objectName() == node.nodeId:
                    return root
                for child in root.childItems():
                    match = find(child)
                    if match is not None:
                        return match
            result = find(runtime.quick.contentItem())
            assert result is not None
            return result

        def click(value):
            visual = item(value)
            viewport = runtime.window.findChild(QObject, "viewport")
            viewport.setProperty("contentY", 0)
            QTest.qWait(30)
            point = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
            maximum = max(0, viewport.property("contentHeight") - viewport.property("height"))
            viewport.setProperty("contentY", min(maximum, max(0, point.y() - runtime.window.height() + 70)))
            QTest.qWait(30)
            point = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
            check("click-in-viewport", 20 <= point.y() <= runtime.window.height()-20)
            QTest.mouseClick(runtime.window, Qt.MouseButton.LeftButton, pos=QPoint(round(point.x()), round(point.y())))
            QTest.qWait(40)

        def layout(name):
            rectangles = []
            for node in runtime.nodes:
                if isinstance(node.value, (Label, Button)):
                    visual = item(node.value)
                    p = visual.mapToScene(QPointF(0, 0))
                    r = [p.x(), p.y(), visual.width(), visual.height()]
                    rectangles.append({"text": node.value.text, "rect": r})
                    check(name+"-width", r[0] >= 19.9 and r[0]+r[2] <= runtime.window.width()-19.9)
                    check(name+"-height", visual.height()+0.1 >= visual.implicitHeight())
            for i, first_rect in enumerate(rectangles):
                x,y,w,h = first_rect["rect"]
                for second_rect in rectangles[i+1:]:
                    a,b,c,d = second_rect["rect"]
                    check(name+"-no-overlap", min(x+w,a+c)-max(x,a) <= .1 or min(y+h,b+d)-max(y,b) <= .1)
            check(name+"-row", abs(item(first).y()-item(second).y()) < .1 and item(first).mapToScene(QPointF()).x() < item(second).mapToScene(QPointF()).x())
            evidence["layouts"][name] = rectangles
            check(name+"-capture", runtime.quick.grabWindow().save(str(output / (name+".png"))))
        try:
            check("visible", runtime.window.isVisible())
            check("exports", pyui_framework.__all__ == ["App", "Window", "Label", "Button", "Row", "Column", "Theme", "ThemeError", "Keyframe", "Timeline", "Playback", "AnimationError"])
            click(first)
            click(second)
            check("independent", counts == [1, 1, 0])
            old = item(first)
            dynamic = body.add(Button("Added after startup", on_click=lambda: count(2)))
            QTest.qWait(150)
            click(dynamic)
            check("dynamic-and-identity", counts == [1,1,1] and item(first) is old)
            layout("normal")
            normal_height = item(long).height()
            runtime.window.resize(300,520)
            QTest.qWait(200)
            layout("narrow")
            check("wrapping", item(long).height() > normal_height)
            click(first)
            item(first).forceActiveFocus()
            QTest.keyClick(runtime.window, Qt.Key.Key_Tab)
            check("tab-focus", item(second).hasActiveFocus())
            QTest.keyClick(runtime.window, Qt.Key.Key_Space)
            check("space-activation", counts == [2,2,1])
            QTest.keyClick(runtime.window, Qt.Key.Key_Backtab)
            check("backtab-focus", item(first).hasActiveFocus())
            QTest.keyClick(runtime.window, Qt.Key.Key_Return)
            evidence["enter_activates"] = counts[0] == 3
            check("enter-observed", counts in ([2,2,1], [3,2,1]))
            runtime.window.resize(280,260)
            QTest.qWait(150)
            click(dynamic)
            check("short-scroll", counts[1:] == [2,2] and counts[0] in (2,3))
            check("qml-errors", not runtime.errors)
            evidence["counts"] = counts
            evidence["errors"] = runtime.errors
        except Exception:
            evidence["failures"].append("exception")
            traceback.print_exc()
        finally:
            (output / "probe.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
            print("RESULT", evidence["failures"], flush=True)
            runtime.qt_app.exit(1 if evidence["failures"] else 0)
    QTimer.singleShot(500, exercise)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]).resolve()))
