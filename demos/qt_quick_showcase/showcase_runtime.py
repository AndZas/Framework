"""Qt implementation kept private to the owner-evaluation showcase."""

import argparse
import math
import os
import platform
import sys
import tempfile
import time
import wave
from pathlib import Path

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QObject, Property, QTimer, QUrl, Qt, Signal, Slot, qVersion
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication, QMessageBox


HERE = Path(__file__).resolve().parent
LIGHT = dict(surface="#f5f6fb", card="#ffffff", ink="#19213a", muted="#68738d", accent="#6c5ce7", accentDeep="#5141c9", star="#ffcc66", border="#dbe0eb", focusColor="#ff9e43")
DARK = dict(surface="#141827", card="#242a3c", ink="#f6f7fc", muted="#a8b2c7", accent="#8c7aff", accentDeep="#6253cc", star="#80dfc5", border="#45506b", focusColor="#ffcb6b")


def make_assets(directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    wav = directory / "tone.wav"
    if not wav.exists():
        with wave.open(str(wav), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(22050)
            data = bytearray()
            for i in range(22050 * 3):
                envelope = min(1.0, i / 1200, (66150 - i) / 1200)
                sample = int(8500 * max(0, envelope) * math.sin(2 * math.pi * 440 * i / 22050))
                data.extend(sample.to_bytes(2, "little", signed=True))
            output.writeframes(data)
    large = directory / "large.png"
    if not large.exists():
        image = QImage(2048, 2048, QImage.Format.Format_RGB32)
        painter = QPainter(image)
        for y in range(2048):
            painter.setPen(QColor(35 + y // 22, 65 + y // 24, 120 + y // 38))
            painter.drawLine(0, y, 2047, y)
        painter.end()
        if not image.save(str(large)):
            raise RuntimeError("Could not generate the 2048 × 2048 stress image")
    return wav, large


class Bridge(QObject):
    changed = Signal()

    def __init__(self, spec, assets: Path):
        super().__init__()
        self.spec = spec
        self.theme_mode = "Light"
        self.colors = LIGHT.copy()
        self.colors.update({"accent": spec.theme.accent, "star": spec.theme.star, "surface": spec.theme.surface, "ink": spec.theme.ink})
        self.dynamic_ids = ["dynamic-1", "dynamic-2", "dynamic-3"]
        self.next_dynamic = 4
        self.animation_running = True
        self.particle_count = 0
        self.second_visible = False
        self._focused = "none"
        self.counts: dict[str, int] = {}
        self.messages = ["Ready. Use the sidebar to explore each section."]
        self.failures: list[str] = []
        self.wav, self.large = make_assets(assets)
        video = HERE / "assets" / "sample.mp4"
        self.video = video if video.exists() else None
        self.devices = self._devices()
        try:
            QApplication.styleHints().colorSchemeChanged.connect(self._system_colors_changed)
        except Exception as exc:
            self.error(f"System theme change signal unavailable: {exc}")
        self.swap_times: list[float] = []
        self.last_swap = None
        self.last_cpu = time.process_time()
        self.last_wall = time.perf_counter()
        self.stats = "Waiting for scene swaps"
        self._log(f"Python {sys.version.split()[0]} · PySide6 {pyside_version} · Qt {qVersion()} · {platform.platform()}")
        if not self.video:
            self.error("Bundled video sample is missing")

    def _devices(self):
        try:
            outputs = [x.description() for x in QMediaDevices.audioOutputs()]
            inputs = [x.description() for x in QMediaDevices.audioInputs()]
            cameras = [x.description() for x in QMediaDevices.videoInputs()]
            return "Audio outputs: " + (", ".join(outputs) or "none") + "\nAudio inputs: " + (", ".join(inputs) or "none") + "\nCameras: " + (", ".join(cameras) or "none")
        except Exception as exc:
            self.error(f"Device enumeration: {type(exc).__name__}: {exc}")
            return "Device enumeration failed; see Diagnostics"

    def _log(self, message):
        self.messages.append(message)
        self.messages = self.messages[-80:]
        print("LOG " + message, flush=True)
        self.changed.emit()

    def error(self, message):
        self.failures.append(message)
        self._log("ERROR " + message)

    @Property(str, notify=changed)
    def surface(self): return self.colors["surface"]
    @Property(str, notify=changed)
    def card(self): return self.colors["card"]
    @Property(str, notify=changed)
    def ink(self): return self.colors["ink"]
    @Property(str, notify=changed)
    def muted(self): return self.colors["muted"]
    @Property(str, notify=changed)
    def accent(self): return self.colors["accent"]
    @Property(str, notify=changed)
    def accentDeep(self): return self.colors["accentDeep"]
    @Property(str, notify=changed)
    def star(self): return self.colors["star"]
    @Property(str, notify=changed)
    def border(self): return self.colors["border"]
    @Property(str, notify=changed)
    def focusColor(self): return self.colors["focusColor"]
    @Property(str, notify=changed)
    def themeMode(self): return self.theme_mode
    @Property("QStringList", notify=changed)
    def dynamicIds(self): return self.dynamic_ids
    @Property(bool, notify=changed)
    def animationRunning(self): return self.animation_running
    @Property(int, notify=changed)
    def particleCount(self): return self.particle_count
    @Property(bool, notify=changed)
    def secondVisible(self): return self.second_visible
    @Property(str, notify=changed)
    def focused(self): return self._focused
    @Property(str, notify=changed)
    def status(self): return self.messages[-1]
    @Property(str, notify=changed)
    def logText(self): return "\n".join(self.messages[-28:])
    @Property(str, notify=changed)
    def devicesText(self): return self.devices
    @Property(str, notify=changed)
    def videoUrl(self): return QUrl.fromLocalFile(str(self.video)).toString() if self.video else ""
    @Property(str, notify=changed)
    def audioUrl(self): return QUrl.fromLocalFile(str(self.wav)).toString()
    @Property(str, notify=changed)
    def imageUrl(self): return QUrl.fromLocalFile(str(self.large)).toString()
    @Property(str, notify=changed)
    def swapStats(self): return self.stats
    @Property(str, constant=True)
    def windowTitle(self): return self.spec.windows[0].title

    @Slot(str)
    def activate(self, control_id):
        self.counts[control_id] = self.counts.get(control_id, 0) + 1
        for control in self.spec.windows[0].controls:
            if control.id == control_id:
                try:
                    control.on_click()
                except Exception as exc:
                    self.error(f"Callback {control_id}: {type(exc).__name__}: {exc}")
                break
        self._log(f"Activated {control_id} × {self.counts[control_id]}")

    @Slot(str)
    def setFocus(self, control_id):
        self._focused = control_id
        self.changed.emit()

    @Slot(str)
    def setTheme(self, mode):
        self.theme_mode = mode
        if mode == "System":
            try:
                scheme = QApplication.styleHints().colorScheme()
                self.colors = DARK.copy() if scheme == Qt.ColorScheme.Dark else LIGHT.copy()
            except Exception as exc:
                self.error(f"System theme detection: {exc}")
                self.colors = LIGHT.copy()
        else:
            self.colors = DARK.copy() if mode == "Dark" else LIGHT.copy()
        self._log(f"Theme: {mode}")

    def _system_colors_changed(self, _scheme):
        if self.theme_mode == "System":
            self.setTheme("System")

    @Slot()
    def toggleAnimation(self):
        self.animation_running = not self.animation_running
        self._log("Animation " + ("running" if self.animation_running else "stopped"))

    @Slot()
    def replayAnimation(self):
        self.animation_running = False
        self.changed.emit()
        QTimer.singleShot(40, self._start_animation)

    def _start_animation(self):
        self.animation_running = True
        self._log("Animation replayed")

    @Slot()
    def addDynamic(self):
        key = f"dynamic-{self.next_dynamic}"
        self.next_dynamic += 1
        self.dynamic_ids = [*self.dynamic_ids, key]
        self._log(f"Added {key}")

    @Slot()
    def removeDynamic(self):
        if self.dynamic_ids:
            key = self.dynamic_ids[-1]
            self.dynamic_ids = self.dynamic_ids[:-1]
            self._log(f"Removed {key}")

    @Slot()
    def toggleSecond(self):
        self.second_visible = not self.second_visible
        self._log("Second window " + ("opened" if self.second_visible else "closed"))

    @Slot(int)
    def setLoad(self, count):
        self.particle_count = count
        self.swap_times.clear()
        self.last_swap = None
        self._log(f"Performance scene: {count} animated elements" + (" + 2048 × 2048 image" if count else ""))

    @Slot(str)
    def mediaEvent(self, message):
        self._log("Media: " + message)

    def on_swap(self):
        now = time.perf_counter()
        if self.last_swap is not None and self.particle_count:
            self.swap_times.append((now - self.last_swap) * 1000)
            self.swap_times = self.swap_times[-600:]
        self.last_swap = now

    def update_stats(self):
        now = time.perf_counter()
        cpu = time.process_time()
        wall_delta = max(0.001, now - self.last_wall)
        cpu_percent = 100 * (cpu - self.last_cpu) / wall_delta
        self.last_cpu, self.last_wall = cpu, now
        if self.swap_times:
            ordered = sorted(self.swap_times)
            median = ordered[len(ordered) // 2]
            p95 = ordered[int(0.95 * (len(ordered) - 1))]
            self.stats = f"Approx. frameSwapped interval: median {median:.1f} ms · p95 {p95:.1f} ms · samples {len(ordered)}\nProcess CPU: {cpu_percent:.1f}% of one logical core, over last ~1 s"
        else:
            self.stats = f"Waiting for scene swaps · process CPU {cpu_percent:.1f}% of one logical core"
        self.changed.emit()


def launch(spec, *, probe=False, capture_dir=None):
    QQuickStyle.setStyle("Basic")
    qt_app = QApplication.instance() or QApplication(sys.argv[:1])
    asset_dir = Path(tempfile.gettempdir()) / "qt_quick_showcase_assets"
    bridge = Bridge(spec, asset_dir)
    engine = QQmlApplicationEngine()
    engine.warnings.connect(lambda warnings: [bridge.error("QML: " + w.toString()) for w in warnings])
    engine.rootContext().setContextProperty("bridge", bridge)
    engine.load(str(HERE / "Main.qml"))
    if not engine.rootObjects():
        detail = "\n".join(bridge.failures[-8:]) or "No QML diagnostic was returned."
        QMessageBox.critical(None, "Qt Quick showcase could not start", "The internal QML scene failed to load.\n\n" + detail)
        return 1
    root = engine.rootObjects()[0]
    backend = "unknown"
    try:
        backend = root.rendererInterface().graphicsApi().name
    except Exception as exc:
        bridge.error(f"Graphics backend query: {exc}")
    bridge._log("Graphics backend: " + backend)
    try:
        root.frameSwapped.connect(bridge.on_swap)
    except Exception as exc:
        bridge.error(f"frameSwapped connection: {exc}")
    timer = QTimer()
    timer.timeout.connect(bridge.update_stats)
    timer.start(1000)
    if probe:
        from smoke import schedule_smoke
        schedule_smoke(qt_app, root, bridge, Path(capture_dir) if capture_dir else HERE / "captures")
    return qt_app.exec()


def run(spec):
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--capture-dir")
    args = parser.parse_args()
    return launch(spec, probe=args.probe, capture_dir=args.capture_dir)
