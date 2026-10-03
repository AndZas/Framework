"""Windows-only evaluation harness; no framework API is defined here."""

import argparse
import math
from pathlib import Path
import platform
import sys
import tempfile
import time
import wave

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QObject, QPoint, QTimer, QUrl, Qt, qVersion
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow, QSGRendererInterface
from PySide6.QtTest import QTest


HERE = Path(__file__).resolve().parent


def make_image(path: Path) -> None:
    image = QImage(2048, 2048, QImage.Format_RGB32)
    painter = QPainter(image)
    for n in range(128):
        painter.fillRect(0, n * 16, 2048, 16, QColor.fromHsv(n * 2, 110, 170))
    painter.end()
    if not image.save(str(path)):
        raise RuntimeError("Could not create stress image")


def make_audio(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        frames = bytearray()
        for i in range(22050):
            envelope = min(1.0, i / 1000) * min(1.0, (22050 - i) / 3000)
            sample = int(6000 * envelope * math.sin(2 * math.pi * 440 * i / 22050))
            frames.extend(sample.to_bytes(2, "little", signed=True))
        wav.writeframes(frames)


def device_names(devices) -> list[str]:
    return [device.description() for device in devices]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true", help="exercise controls, stress, save screenshots, then exit")
    parser.add_argument("--media", type=Path, help="optional local audio or video file")
    parser.add_argument("--vulkan", action="store_true", help="optional Vulkan diagnostic")
    args = parser.parse_args()
    if args.vulkan:
        QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.Vulkan)

    app = QGuiApplication(sys.argv)
    print(f"Python={platform.python_version()} PySide6={pyside_version} Qt={qVersion()}", flush=True)
    print(f"Windows={platform.platform()} OS={platform.version()}", flush=True)
    print(f"Audio outputs={device_names(QMediaDevices.audioOutputs())}", flush=True)
    print(f"Audio inputs={device_names(QMediaDevices.audioInputs())}", flush=True)
    print(f"Cameras={device_names(QMediaDevices.videoInputs())}", flush=True)

    with tempfile.TemporaryDirectory(prefix="qt_quick_spike_", ignore_cleanup_errors=True) as temp:
        temp_path = Path(temp)
        image_path = temp_path / "large.png"
        make_image(image_path)
        media_path = args.media.resolve() if args.media else temp_path / "tone.wav"
        if not args.media:
            make_audio(media_path)
        if args.media and not media_path.is_file():
            parser.error(f"media file not found: {media_path}")

        engine = QQmlEngine()
        context = engine.rootContext()
        context.setContextProperty("imageUrl", QUrl.fromLocalFile(str(image_path)))
        context.setContextProperty("mediaUrl", QUrl.fromLocalFile(str(media_path)))

        windows = []
        components = []
        for filename in ("Main.qml", "Secondary.qml"):
            component = QQmlComponent(engine, QUrl.fromLocalFile(str(HERE / filename)))
            if component.isError():
                raise RuntimeError("\n".join(str(e) for e in component.errors()))
            window = component.create()
            if window is None:
                raise RuntimeError("\n".join(str(e) for e in component.errors()))
            QQmlEngine.setObjectOwnership(window, QQmlEngine.ObjectOwnership.CppOwnership)
            windows.append(window)
            components.append(component)
        main_window, second_window = windows
        main_window.show()
        second_window.show()
        print(f"Windows created={len(windows)} distinct={main_window is not second_window}", flush=True)

        frames = []
        main_window.frameSwapped.connect(lambda: frames.append(time.perf_counter()))

        def backend():
            try:
                api = main_window.rendererInterface().graphicsApi()
                print(f"Graphics API={api.name}", flush=True)
            except Exception as exc:
                print(f"Graphics API query failed={exc}", flush=True)

        QTimer.singleShot(1000, backend)
        player = main_window.findChild(QObject, "mediaPlayer")
        QTimer.singleShot(500, lambda: print(f"Media playback state at 0.5s={player.property('playbackState')}", flush=True))

        if args.probe:
            capture_name = "vulkan" if args.vulkan else "default"
            def test_controls():
                rounded = main_window.findChild(QObject, "roundedControl")
                star = main_window.findChild(QObject, "starControl")
                animated = main_window.findChild(QObject, "animatedItem")
                theme = main_window.findChild(QObject, "themeButton")
                input_item = main_window.findChild(QQuickItem, "inputItem")
                # Coordinates are in the window's content item.
                QTest.mouseClick(main_window, Qt.LeftButton, pos=QPoint(rounded.x() + 75, rounded.y() + 20))
                rounded_inside = main_window.property("roundedClicks")
                QTest.mouseClick(main_window, Qt.LeftButton, pos=QPoint(rounded.x() + 2, rounded.y() + 2))
                rounded_outside = main_window.property("roundedClicks")
                QTest.mouseClick(main_window, Qt.LeftButton, pos=QPoint(star.x() + 60, star.y() + 30))
                inside_count = main_window.property("starClicks")
                QTest.mouseClick(main_window, Qt.LeftButton, pos=QPoint(star.x() + 10, star.y() + 10))
                outside_count = main_window.property("starClicks")
                QTest.mouseClick(main_window, Qt.LeftButton, pos=QPoint(theme.x() + 75, theme.y() + 20))
                main_window.requestActivate()
                input_item.forceActiveFocus()
                def key_check():
                    QTest.keyClick(main_window, Qt.Key_A)
                    focus = main_window.activeFocusItem()
                    print(f"Keyboard active_window={main_window.isActive()} focus={focus.objectName() if focus else None} keys={main_window.property('keyCount')}", flush=True)
                QTimer.singleShot(100, key_check)
                print(f"Controls rounded_inside={rounded_inside} rounded_after_outside={rounded_outside} star_inside={inside_count} star_after_outside={outside_count} dark={main_window.property('dark')} pointer={main_window.property('pointerCount')}", flush=True)
                print(f"Animation x={animated.x():.1f}", flush=True)
                image = main_window.grabWindow()
                print(f"Screenshot idle={image.save(str(HERE / f'probe-{capture_name}-idle.png'))}", flush=True)
                main_window.setProperty("stressEnabled", True)
                frames.clear()
                test_controls.wall_start = time.perf_counter()
                test_controls.cpu_start = time.process_time()

            def finish():
                elapsed = time.perf_counter() - test_controls.wall_start
                cpu = time.process_time() - test_controls.cpu_start
                intervals = [(b - a) * 1000 for a, b in zip(frames, frames[1:])]
                if intervals:
                    intervals.sort()
                    print(f"Stress frames={len(frames)} wall_s={elapsed:.2f} fps={len(frames)/elapsed:.1f} frame_ms_median={intervals[len(intervals)//2]:.1f} frame_ms_p95={intervals[int(len(intervals)*0.95)]:.1f} max={intervals[-1]:.1f} process_cpu_percent_one_core={cpu/elapsed*100:.1f}", flush=True)
                else:
                    print("Stress no frameSwapped samples", flush=True)
                image = main_window.grabWindow()
                print(f"Screenshot stress={image.save(str(HERE / f'probe-{capture_name}-stress.png'))}", flush=True)
                app.quit()

            QTimer.singleShot(1500, test_controls)
            QTimer.singleShot(11500, finish)

        result = app.exec()
        player.setProperty("source", QUrl())
        for window in windows:
            window.close()
        app.processEvents()
        return result


if __name__ == "__main__":
    raise SystemExit(main())
