"""Short visible Windows QtTest scenario; it does not replace owner input checks."""

import json
import statistics
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, QTimer, Qt
from PySide6.QtQuick import QQuickItem, QQuickWindow
from PySide6.QtTest import QTest
import shiboken6


def schedule_smoke(qt_app, root, bridge, captures: Path):
    captures.mkdir(parents=True, exist_ok=True)
    failures = []
    observations = {}

    def check(name, actual, expected):
        passed = actual == expected
        observations[name] = {"actual": actual, "expected": expected, "pass": passed}
        print(f"CHECK {name}: {actual!r} == {expected!r}: {passed}", flush=True)
        if not passed:
            failures.append(name)

    def grab(name):
        quick = shiboken6.wrapInstance(shiboken6.getCppPointer(root)[0], QQuickWindow)
        saved = quick.grabWindow().save(str(captures / name))
        check("capture-" + name, saved, True)

    def click_item(item, x=None, y=None):
        point = item.mapToScene(QPointF(item.width() / 2 if x is None else x, item.height() / 2 if y is None else y))
        QTest.mouseClick(root, Qt.MouseButton.LeftButton, pos=QPoint(round(point.x()), round(point.y())))
        qt_app.processEvents()

    def start():
        try:
            check("window-visible", root.isVisible(), True)
            hello = root.findChild(QQuickItem, "helloButton")
            orange = root.findChild(QQuickItem, "orangeButton")
            star = root.findChild(QQuickItem, "starControl")
            check("controls-present", all((hello, orange, star)), True)
            grab("01-controls.png")
            click_item(hello)
            click_item(orange)
            click_item(star, 56, 52)
            click_item(star, 2, 2)
            check("independent-actions", [bridge.counts.get(x, 0) for x in ("hello", "orange", "star")], [1, 1, 1])
            hello.forceActiveFocus()
            QTest.keyClick(root, Qt.Key.Key_Space)
            check("keyboard-space", bridge.counts.get("hello"), 2)
            star.forceActiveFocus()
            QTest.keyClick(root, Qt.Key.Key_Return)
            check("keyboard-enter-star", bridge.counts.get("star"), 2)
            bridge.setTheme("Dark")
            root.showPage(1)
            QTimer.singleShot(280, dark)
        except Exception as exc:
            failures.append("start-exception")
            print(f"PROBE ERROR start: {exc!r}", flush=True)
            finish()

    def dark():
        try:
            check("dark-theme", bridge.theme_mode, "Dark")
            grab("02-dark.png")
            root.showPage(2)
            animated = root.findChild(QQuickItem, "animatedButton")
            observations["animation-scale-a"] = animated.scale()
            QTimer.singleShot(240, animation)
        except Exception as exc:
            failures.append("dark-exception")
            print(f"PROBE ERROR dark: {exc!r}", flush=True)
            finish()

    def animation():
        try:
            animated = root.findChild(QQuickItem, "animatedButton")
            observations["animation-scale-b"] = animated.scale()
            check("animation-changing", abs(observations["animation-scale-a"] - observations["animation-scale-b"]) > 0.01, True)
            bridge.toggleAnimation()
            check("animation-stop", bridge.animation_running, False)
            bridge.replayAnimation()
            root.showPage(3)
            old = len(bridge.dynamic_ids)
            bridge.addDynamic()
            qt_app.processEvents()
            check("dynamic-added", len(bridge.dynamic_ids), old + 1)
            check("qml-dynamic-count", root.dynamicCount(), old + 1)
            bridge.activate(bridge.dynamic_ids[-1])
            bridge.removeDynamic()
            check("dynamic-removed", len(bridge.dynamic_ids), old)
            bridge.toggleSecond()
            qt_app.processEvents()
            check("second-window", root.secondWindowVisible(), True)
            grab("03-dynamic.png")
            bridge.toggleSecond()
            root.showPage(5)
            root.playSampleMedia()
            QTimer.singleShot(1200, media)
        except Exception as exc:
            failures.append("animation-exception")
            print(f"PROBE ERROR animation: {exc!r}", flush=True)
            finish()

    def media():
        try:
            observations["media-states"] = root.mediaStates().toVariant()
            check("media-playing", observations["media-states"][0] == 1 and observations["media-states"][2] == 1, True)
            check("video-source", bool(bridge.video), True)
            check("audio-source", bridge.wav.exists(), True)
            grab("04-media.png")
            root.stopSampleMedia()
            root.showPage(6)
            bridge.setLoad(50)
            QTimer.singleShot(1500, light_load)
        except Exception as exc:
            failures.append("media-exception")
            print(f"PROBE ERROR media: {exc!r}", flush=True)
            finish()

    def light_load():
        observations["load-50"] = summarize(bridge.swap_times)
        observations["status-50"] = bridge.stats
        check("load-50-count", bridge.particle_count, 50)
        bridge.setLoad(400)
        QTimer.singleShot(1800, heavy_load)

    def heavy_load():
        try:
            observations["load-400"] = summarize(bridge.swap_times)
            observations["status-400"] = bridge.stats
            check("load-400-count", bridge.particle_count, 400)
            grab("05-performance.png")
            bridge.setLoad(0)
            root.showPage(7)
            grab("06-diagnostics.png")
            observations["devices"] = bridge.devices
            observations["errors"] = bridge.failures
            observations["backend_log"] = [m for m in bridge.messages if "Graphics backend" in m]
            check("qml-errors", len([x for x in bridge.failures if x.startswith("QML:")]), 0)
            finish()
        except Exception as exc:
            failures.append("heavy-exception")
            print(f"PROBE ERROR heavy: {exc!r}", flush=True)
            finish()

    def finish():
        observations["failures"] = failures
        report = captures / "smoke-results.json"
        report.write_text(json.dumps(observations, indent=2, default=str), encoding="utf-8")
        print(f"RESULT failures={failures} report={report}", flush=True)
        root.close()
        qt_app.exit(1 if failures else 0)

    QTimer.singleShot(500, start)


def summarize(samples):
    if not samples:
        return {"samples": 0}
    ordered = sorted(samples)
    return {"samples": len(ordered), "median_ms": round(statistics.median(ordered), 2), "p95_ms": round(ordered[int(0.95 * (len(ordered) - 1))], 2), "max_ms": round(max(ordered), 2)}
