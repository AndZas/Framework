"""Real scroll inputs followed immediately by a stationary-pointer click burst.

Signal instrumentation is passive: do not connect doubleClicked, since Qt's
AbstractButton changes click behavior when that signal has a receiver.
"""
import argparse
import json
import platform
import sys
import traceback
from pathlib import Path

import PySide6
from PySide6.QtCore import QEvent, QObject, QPoint, QPointF, Qt, QTimer, SIGNAL, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest

from pyui_framework import App, Button, Label, Window
import pyui_framework


def run(route, output):
    qt_app = QGuiApplication([])
    counts = [0, 0]
    def hit(index):
        counts[index] += 1

    window = Window("Rapid clicks after scrolling", width=300, height=260)
    for index in range(6):
        window.add(Label(f"Paragraph {index}: A little text that takes up space in this narrow window."))
    target = window.add(Button("Target", on_click=lambda: hit(0)))
    window.add(Button("Neighbor", on_click=lambda: hit(1)))
    app = App(window)
    report = {"route": route, "environment": {"Windows": platform.platform(),
              "Python": sys.version, "PySide6": PySide6.__version__, "Qt": qVersion()},
              "package": pyui_framework.__file__, "trace": [], "failures": []}

    def exercise():
        runtime = app._runtime
        quick = runtime.quick
        viewport = runtime.window.findChild(QObject, "viewport")
        node = next(n for n in runtime.nodes if n.value is target)
        def find(root):
            if root.objectName() == node.nodeId:
                return root
            for child in root.childItems():
                match = find(child)
                if match is not None:
                    return match
        visual = find(quick.contentItem())

        def state():
            return {p: viewport.property(p) for p in
                    ("contentY", "moving", "flicking", "dragging", "verticalVelocity")}

        def log(**event):
            report["trace"].append(dict(event, state=state()))

        class Observer(QObject):
            def eventFilter(self, obj, event):
                if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease,
                                    QEvent.MouseButtonDblClick, QEvent.Wheel):
                    log(event=event.type().name, position=[event.position().x(), event.position().y()],
                        timestamp=event.timestamp())
                return False
        observer = Observer(quick)
        quick.installEventFilter(observer)
        for signal in ("pressed", "released", "canceled", "clicked"):
            QObject.connect(visual, SIGNAL(signal + "()"), lambda signal=signal: log(signal=signal))

        def check(name, passed):
            print(f"CHECK {route}/{name}: {bool(passed)}", flush=True)
            if not passed:
                report["failures"].append(name)

        def center():
            p = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
            return QPoint(round(p.x()), round(p.y()))

        try:
            report["initial"] = state()
            report["accepted_buttons"] = viewport.property("acceptedButtons").value
            check("target-initially-hidden", center().y() > quick.height())
            if route == "wheel":
                # Pump only while the real gesture is revealing the target.
                # Stop as soon as its whole button is visible, while moving.
                for _ in range(40):
                    QTest.wheelEvent(quick, QPoint(140, 200), QPoint(0, -120))
                    QTest.qWait(10)
                    if center().y() <= 200:
                        break
                check("wheel-still-moving", viewport.property("moving"))
            elif route == "scrollbar":
                bar = next(obj for obj in quick.findChildren(QObject)
                           if obj.metaObject().className().startswith("ScrollBar_")
                           and obj.property("orientation") == Qt.Vertical)
                # Drag the actual thumb, not the position/contentY property.
                size = bar.property("size")
                position = bar.property("position")
                start = bar.mapToScene(QPointF(bar.width()/2, (position + size/2) * bar.height()))
                end = bar.mapToScene(QPointF(bar.width()/2, bar.height()-2))
                QTest.mousePress(quick, Qt.LeftButton, pos=start.toPoint(), delay=1)
                for step in range(1, 5):
                    p = start + (end-start) * (step/4)
                    QTest.mouseMove(quick, p.toPoint(), delay=1)
                QTest.mouseRelease(quick, Qt.LeftButton, pos=end.toPoint(), delay=1)
            else:
                QTest.mousePress(quick, Qt.LeftButton, pos=QPoint(100, 210), delay=1)
                for y in range(200, 19, -10):
                    QTest.mouseMove(quick, QPoint(100, y), delay=1)
                    if center().y() <= 200:
                        break
                QTest.mouseRelease(quick, Qt.LeftButton, pos=QPoint(100, y), delay=1)
                if report["accepted_buttons"] == 0:
                    check("desktop-content-drag-disabled", viewport.property("contentY") == 0
                          and not viewport.property("moving") and counts == [0, 0])
                    report["burst"] = "Not applicable: mouse content dragging is disabled"
                    return

            report["before_burst"] = state()
            check("scrolled-with-input", viewport.property("contentY") > 0)
            pointer = center()
            report["pointer"] = [pointer.x(), pointer.y()]
            check("target-fully-visible", 44 <= pointer.y() <= quick.height()-44)
            for index in range(10):
                # No idle pause after scrolling or between clicks. QtTest still
                # pumps delivery; these are paired presses/releases, not holds.
                local = visual.mapFromScene(QPointF(pointer))
                check("pointer-still-on-target", 0 <= local.x() < visual.width()
                      and 0 <= local.y() < visual.height())
                log(intended_click=index+1)
                QTest.mousePress(quick, Qt.LeftButton, pos=pointer, delay=1)
                QTest.mouseRelease(quick, Qt.LeftButton, pos=pointer, delay=1)
                check("each-click-delivered", counts == [index+1, 0])
            report["after_burst"] = state()
            report["burst_counts"] = list(counts)
            # Separate recovery diagnostic, never a delay in the regression.
            QTest.qWait(500)
            pointer = center()
            QTest.mouseClick(quick, Qt.LeftButton, pos=pointer, delay=1)
            report["after_pause_counts"] = list(counts)
            check("click-after-pause", counts == [report["burst_counts"][0]+1, 0])
            check("neighbor-untouched", counts[1] == 0)
        except Exception:
            report["failures"].append("exception")
            traceback.print_exc()
        finally:
            check("no-qml-errors", not runtime.errors)
            report["counts"] = counts
            report["qml_errors"] = runtime.errors
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"RESULT {route}: {report['failures']}", flush=True)
            qt_app.exit(1 if report["failures"] else 0)
    QTimer.singleShot(300, exercise)
    return app.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route", choices=("wheel", "scrollbar", "drag"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.route, args.output))
