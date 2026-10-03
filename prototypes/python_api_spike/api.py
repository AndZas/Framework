"""Small, experimental Python authoring surface backed by Qt Quick items."""

from dataclasses import dataclass
from math import cos, pi, sin
from typing import Callable

from PySide6.QtCore import QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtQuick import QQuickPaintedItem, QQuickWindow
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class Theme:
    surface: str = "#f4f1fa"
    ink: str = "#29243a"
    accent: str = "#7756d8"
    accent_end: str = "#ab73e8"
    star: str = "#ffc857"


@dataclass(frozen=True)
class Pulse:
    duration_ms: int = 420
    peak_scale: float = 1.08


class Control(QQuickPaintedItem):
    def __init__(self, on_click: Callable[[], None] | None = None):
        super().__init__()
        self.on_click = on_click
        self.app = None
        self.clicks = 0
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setAntialiasing(True)

    def mousePressEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        if self.contains(event.position()):
            self.clicks += 1
            if self.on_click:
                self.on_click()
        event.accept()

    def theme(self):
        return self.app.theme


class Button(Control):
    def __init__(self, text: str, on_click=None, *, fill: str | None = None, pulse: Pulse | None = None):
        super().__init__(on_click)
        self.text = text
        self.fill = fill
        self.pulse = pulse
        self.setWidth(220)
        self.setHeight(48)

    def contains(self, point):
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        return path.contains(point)

    def paint(self, painter: QPainter):
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        color = self.fill or self.theme().accent
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(color))
        gradient.setColorAt(1, QColor(color if self.fill else self.theme().accent_end))
        painter.setPen(QPen(QColor("#4c3a7e"), 1.5))
        painter.setBrush(gradient)
        painter.drawPath(path)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 11))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.text)


class Star(Control):
    def __init__(self, on_click=None):
        super().__init__(on_click)
        self.setWidth(120)
        self.setHeight(120)
        self._path = QPainterPath()
        for index in range(10):
            angle = -pi / 2 + index * pi / 5
            radius = 55 if index % 2 == 0 else 23
            x, y = 60 + radius * cos(angle), 60 + radius * sin(angle)
            if index == 0:
                self._path.moveTo(x, y)
            else:
                self._path.lineTo(x, y)
        self._path.closeSubpath()

    def contains(self, point):
        return self._path.contains(point)

    def paint(self, painter: QPainter):
        gradient = QLinearGradient(0, 0, 120, 120)
        gradient.setColorAt(0, QColor(self.theme().star))
        gradient.setColorAt(1, QColor("#e87578"))
        painter.setPen(QPen(QColor("#744068"), 2))
        painter.setBrush(gradient)
        painter.drawPath(self._path)


class Window:
    def __init__(self, title: str, *, width: int = 420, height: int = 390):
        self.title, self.width, self.height = title, width, height
        self.controls: list[Control] = []
        self.native: QQuickWindow | None = None

    def add(self, control: Control):
        self.controls.append(control)
        return control


class App:
    def __init__(self, theme: Theme | None = None):
        self.theme = theme or Theme()
        self.windows: list[Window] = []
        self.qt_app: QApplication | None = None
        self._animations: list[QPropertyAnimation] = []

    def add(self, window: Window):
        self.windows.append(window)
        return window

    def set_theme(self, theme: Theme):
        self.theme = theme
        for window in self.windows:
            if window.native:
                window.native.setColor(QColor(theme.surface))
                for control in window.controls:
                    control.update()

    def start(self):
        self.qt_app = QApplication.instance() or QApplication([])
        for window in self.windows:
            native = QQuickWindow()
            native.setTitle(window.title)
            native.setWidth(window.width)
            native.setHeight(window.height)
            native.setColor(QColor(self.theme.surface))
            window.native = native
            y = 24
            for control in window.controls:
                control.app = self
                control.setParentItem(native.contentItem())
                control.setX(24)
                control.setY(y)
                y += control.height() + 18
                if isinstance(control, Button) and control.pulse:
                    animation = QPropertyAnimation(control, b"scale")
                    animation.setStartValue(1.0)
                    animation.setKeyValueAt(0.5, control.pulse.peak_scale)
                    animation.setEndValue(1.0)
                    animation.setDuration(control.pulse.duration_ms)
                    animation.setLoopCount(-1)
                    self._animations.append(animation)
                    animation.start()
            native.show()

    def run(self):
        self.start()
        return self.qt_app.exec()
