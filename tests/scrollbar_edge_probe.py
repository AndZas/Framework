"""Visible Windows QtTest regression for both shells; no physical input claims."""
import argparse
import json
import platform
import runpy
import sys
from pathlib import Path

import PySide6
import shiboken6
from PySide6.QtCore import QPoint, QPointF, Qt, qInstallMessageHandler, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest

ROOT = Path(__file__).resolve().parents[1]


def find(root, name):
    if root.objectName() == name:
        return root
    for child in root.childItems():
        result = find(child, name)
        if result is not None:
            return result
    return None


def rect(item):
    p = item.mapToScene(QPointF())
    return [p.x(), p.y(), item.width(), item.height()]


def run(kind, output):
    output.mkdir(parents=True, exist_ok=True)
    messages = []
    previous = qInstallMessageHandler(lambda typ, context, message: messages.append(message))
    qt = QGuiApplication([])
    report = dict(app=kind, environment=dict(windows=platform.platform(), python=sys.version,
                  pyside=PySide6.__version__, qt=qVersion()), physical_input=False, sizes=[])
    callbacks = [0]
    if kind == "production":
        from pyui_framework import Label
        from pyui_framework._runtime import Runtime
        model = runpy.run_path(str(ROOT / "examples/hello.py"))["build"]()
        runtime = Runtime(model)
        window = runtime.quick
        engine = runtime.engine
        action = next(n.value for n in runtime.nodes if getattr(n.value, "text", "") == "Add a live action")
        original = action.on_click

        def counted_action():
            callbacks[0] += 1
            original()
        action.on_click = counted_action

        def target():
            node = next(n for n in runtime.nodes if getattr(n.value, "text", "") == "Add a live action")
            return find(window.contentItem(), node.nodeId)

        def verify_action():
            assert sum(getattr(n.value, "text", "") == "Added after startup" for n in runtime.nodes) == 1
            assert any(getattr(n.value, "text", "") == "Ready. Each action has its own counter." for n in runtime.nodes)

        def cleanup():
            runtime.close()
    else:
        sys.path.insert(0, str(ROOT / "prototypes/theme_api_spike"))
        from app import build, delete
        qt, engine, lab = build()
        window = engine.rootObjects()[0]
        # Successful load emits changed once from the actual Python slot.
        lab.changed.connect(lambda: callbacks.__setitem__(0, callbacks[0]+1))
        original_local = lab.local.appearance.copy()
        original_method = lab.method.appearance.copy()

        def target():
            return find(window.contentItem(), "loadFile")

        def verify_action():
            assert lab.mode == "CSS file", lab.mode
            for token in ("accent", "accent_text", "radius", "opacity"):
                assert lab.local.appearance[token] == original_local[token]
                assert lab.method.appearance[token] == original_method[token]

        def cleanup():
            window.close()
            delete(engine)

    try:
        QTest.qWait(400)
        assert window.isVisible()
        viewport = find(window.contentItem(), "viewport")
        bar = find(window.contentItem(), "verticalScrollBar")
        margin = 20 if kind == "production" else 28
        normal = (640, 520) if kind == "production" else (1040, 820)
        sizes = [normal, (280, 260)] if kind == "production" else [normal, (620, 420)]

        def geometry():
            vr, br = rect(viewport), rect(bar)
            assert shiboken6.getCppPointer(bar.parentItem())[0] == shiboken6.getCppPointer(window.property("contentItem"))[0]
            assert viewport.property("clip")
            assert viewport.property("acceptedButtons") == Qt.NoButton
            assert abs(br[0] + br[2] - window.width()) < .1, br
            assert abs(br[1]) < .1 and abs(br[3] - window.height()) < .1, br
            assert vr == [margin, margin, window.width()-2*margin, window.height()-2*margin], vr
            assert br[2] > 0 and vr[0]+vr[2] <= br[0], (vr, br)
            # Every painted content descendant is clipped by this disjoint viewport.
            return dict(window=[window.width(), window.height()], viewport=vr, scrollbar=br,
                        gap=br[0]-vr[0]-vr[2], content_height=viewport.property("contentHeight"))

        def capture(name):
            assert window.grabWindow().save(str(output / (name + ".png")))

        def drag(bottom):
            thumb_obj = bar.property("contentItem")
            thumb = shiboken6.wrapInstance(shiboken6.getCppPointer(thumb_obj)[0], QQuickItem)
            start = thumb.mapToScene(thumb.boundingRect().center()).toPoint()
            end = bar.mapToScene(QPointF(bar.width()/2, bar.height()-2 if bottom else 2)).toPoint()
            QTest.mousePress(window, Qt.LeftButton, pos=start, delay=1)
            assert bar.property("pressed"), "thumb did not accept press"
            for step in range(1, 9):
                QTest.mouseMove(window, start + (end-start)*step/8, delay=1)
            QTest.mouseRelease(window, Qt.LeftButton, pos=end, delay=1)
            QTest.qWait(200)

        for index, (width, height) in enumerate(sizes):
            window.resize(width, height)
            QTest.qWait(400)
            entry = geometry()
            QTest.mouseMove(window, bar.mapToScene(bar.boundingRect().center()).toPoint())
            QTest.qWait(150)
            capture("default" if index == 0 else "narrow")
            if kind == "production" and index == 0:
                window.resize(*sizes[-1])
                QTest.qWait(300)
                geometry()
                capture("example-narrow")
                drag(True)
                capture("example-narrow-scrolled")
                window.resize(*normal)
                QTest.qWait(300)
                # The real hello example fits at default size. Also test normal-size
                # overflow without changing its screenshot or application source.
                for i in range(14):
                    model.add(Label(f"Regression overflow paragraph {i}"))
                QTest.qWait(300)
            maximum = viewport.property("contentHeight") - viewport.height()
            entry["overflow_content_height"] = viewport.property("contentHeight")
            assert maximum > 0
            before_scroll_callbacks = callbacks[0]
            drag(False)
            assert viewport.property("contentY") < 1
            assert callbacks[0] == before_scroll_callbacks, "scroll input activated an action"
            wheel_pos = QPoint(width//2, height//2)
            QTest.wheelEvent(window, wheel_pos, QPoint(0, -120))
            QTest.qWait(40)
            assert viewport.property("contentY") > 0
            assert bar.property("visible") and bar.property("size") < 1
            thumb_obj = bar.property("contentItem")
            assert thumb_obj.property("opacity") > 0, "overflow thumb invisible"
            entry["wheel_content_y"] = viewport.property("contentY")
            QTest.qWait(500)
            drag(False)
            # Click the exposed track below the thumb, then drag to the end.
            track = bar.mapToScene(QPointF(bar.width()/2, bar.height()-3)).toPoint()
            QTest.mouseClick(window, Qt.LeftButton, pos=track, delay=1)
            QTest.qWait(200)
            assert viewport.property("contentY") > 0, "track did not scroll"
            entry["track_content_y"] = viewport.property("contentY")
            drag(True)
            assert abs(viewport.property("contentY")-maximum) < 1
            entry["thumb_bottom_content_y"] = viewport.property("contentY")
            capture("normal-overflow-scrolled" if index == 0 else "narrow-scrolled")
            drag(False)
            assert viewport.property("contentY") < 1
            # Reach the real action with wheel input; click immediately while scrolling.
            assert callbacks[0] == before_scroll_callbacks, "scroll input activated an action"
            for _ in range(50):
                item = target()
                r = rect(item)
                if margin <= r[1] and r[1]+r[3] <= height-margin:
                    break
                QTest.wheelEvent(window, wheel_pos, QPoint(0, -120))
                QTest.qWait(10)
            else:
                raise AssertionError("action never fully visible")
            prior_callbacks = callbacks[0]
            for click_index in range(5):
                point = item.mapToScene(item.boundingRect().center()).toPoint()
                QTest.mouseClick(window, Qt.LeftButton, pos=point, delay=1)
                verify_action()
                assert callbacks[0] == prior_callbacks+click_index+1
            QTest.qWait(500)
            QTest.mouseClick(window, Qt.LeftButton, pos=item.mapToScene(item.boundingRect().center()).toPoint())
            verify_action()
            assert callbacks[0] == prior_callbacks+6
            entry["action_clicks"] = 6
            geometry()
            # A mouse drag on blank inset content must remain disabled.
            QTest.qWait(300)
            before = viewport.property("contentY")
            start = QPoint(margin+2, height-margin-5)
            QTest.mousePress(window, Qt.LeftButton, pos=start)
            QTest.mouseMove(window, QPoint(start.x(), margin+5), delay=20)
            QTest.mouseRelease(window, Qt.LeftButton, pos=QPoint(start.x(), margin+5))
            QTest.qWait(100)
            assert abs(viewport.property("contentY")-before) < .1
            report["sizes"].append(entry)
        # Exercise overflow disappearance and renewed overflow after resizing.
        window.resize(normal[0], 1200)
        QTest.qWait(700)
        geometry()
        assert viewport.property("contentHeight") <= viewport.height()
        assert bar.property("size") == 1
        thumb_obj = bar.property("contentItem")
        assert thumb_obj.property("opacity") == 0
        window.resize(*sizes[-1])
        QTest.qWait(300)
        geometry()
        assert bar.property("size") < 1
        report["overflow_resize_transition"] = True
    finally:
        cleanup()
        qt.processEvents()
        report["messages"] = messages
        (output / "probe.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        qInstallMessageHandler(previous)
    assert not messages, messages
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", choices=("production", "theme"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.app, args.output.resolve())
