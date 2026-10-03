"""Direct QQuickPaintedItem backend; no QML or generated QML."""

from math import cos, pi, sin

from PySide6.QtCore import QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtQuick import QQuickPaintedItem, QQuickWindow

from model import Button, Label, Star


class Painted(QQuickPaintedItem):
    def __init__(self, spec, app):
        super().__init__()
        self.spec, self.app = spec, app
        self.setAntialiasing(True)
        self.setObjectName(type(spec).__name__.lower())
        self.setHeight(120 if isinstance(spec, Star) else 52)
        if not isinstance(spec, Label):
            self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        if isinstance(spec, Button):
            self.setFlag(self.Flag.ItemIsFocusScope, True)
            self.setFocus(True)

    def shape(self):
        path = QPainterPath()
        if isinstance(self.spec, Star):
            for i in range(10):
                angle = -pi / 2 + i * pi / 5
                radius = 55 if i % 2 == 0 else 23
                x, y = 60 + radius * cos(angle), 60 + radius * sin(angle)
                (path.moveTo if i == 0 else path.lineTo)(x, y)
            path.closeSubpath()
        else:
            path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        return path

    def contains(self, point):
        return self.shape().contains(point)

    def mousePressEvent(self, event):
        self._pressed = self.contains(event.position())
        event.accept()

    def mouseReleaseEvent(self, event):
        if getattr(self, "_pressed", False) and self.contains(event.position()):
            self.spec.on_click()
        self._pressed = False
        event.accept()

    def keyPressEvent(self, event):
        if isinstance(self.spec, Button) and event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.spec.on_click()
            event.accept()
        else:
            super().keyPressEvent(event)

    def paint(self, painter: QPainter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if isinstance(self.spec, Label):
            painter.setPen(QColor(self.app.theme.ink))
            painter.setFont(QFont("Segoe UI", 15))
            painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.spec.text)
            return
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.app.theme.star if isinstance(self.spec, Star) else self.spec.fill or self.app.theme.accent))
        painter.drawPath(self.shape())
        if isinstance(self.spec, Button):
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.spec.text)


class Backend:
    def __init__(self, app):
        self.app = app
        self.window = QQuickWindow()
        self.window.setTitle(app.window.title)
        self.window.resize(app.window.width, app.window.height)
        self.window.setColor(QColor(app.theme.surface))
        self.items = {}
        self.animations = []
        for spec in app.window.children:
            item = Painted(spec, app)
            item.setParentItem(self.window.contentItem())
            self.items[type(spec).__name__.lower()] = item
            if isinstance(spec, Button) and spec.pulse:
                animation = QPropertyAnimation(item, b"scale")
                animation.setDuration(spec.pulse.duration_ms)
                animation.setStartValue(1.0)
                animation.setKeyValueAt(0.5, spec.pulse.peak_scale)
                animation.setEndValue(1.0)
                animation.setLoopCount(-1)
                self.animations.append(animation)
                animation.start()
        self.window.widthChanged.connect(self.layout)
        self.layout()
        self.window.show()
        self.items["button"].forceActiveFocus()

    def layout(self):
        usable = max(1, self.window.width() - 48)
        y = 24
        for spec in self.app.window.children:
            item = self.items[type(spec).__name__.lower()]
            width = min(120 if isinstance(spec, Star) else 300 if isinstance(spec, Button) else usable, usable)
            item.setWidth(width)
            item.setX((self.window.width() - width) / 2 if isinstance(spec, Star) else 24)
            item.setY(y)
            y += item.height() + 18

    def set_theme(self):
        self.window.setColor(QColor(self.app.theme.surface))
        for item in self.items.values():
            item.update()
