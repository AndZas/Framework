"""Internal QML assembled from the same Python data; app authors write Python only."""

import json

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtQml import QQmlApplicationEngine

from model import Button, Label, Star


class Bridge(QObject):
    themeChanged = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app

    @Property(str, notify=themeChanged)
    def surface(self):
        return self.app.theme.surface

    @Property(str, notify=themeChanged)
    def ink(self):
        return self.app.theme.ink

    @Property(str, notify=themeChanged)
    def accent(self):
        return self.app.theme.accent

    @Property(str, notify=themeChanged)
    def star(self):
        return self.app.theme.star

    @Slot(str)
    def activate(self, name):
        self.app.callbacks[name]()


QML = r'''
import QtQuick
import QtQuick.Window
Window {
    id: root
    width: @WIDTH@
    height: @HEIGHT@
    visible: true
    title: @TITLE@
    color: bridge.surface
    Column {
        id: stack
        anchors.top: parent.top
        anchors.topMargin: 24
        anchors.horizontalCenter: parent.horizontalCenter
        width: Math.max(1, root.width - 48)
        spacing: 18
        Text {
            objectName: "label"
            width: stack.width
            height: 52
            text: @LABEL@
            color: bridge.ink
            font.family: "Segoe UI"
            font.pixelSize: 20
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        Rectangle {
            id: button
            objectName: "button"
            width: Math.min(300, stack.width)
            height: 52
            radius: 16
            color: @FILL@ || bridge.accent
            activeFocusOnTab: true
            focus: true
            scale: 1.0
            Text {
                anchors.fill: parent
                text: @BUTTON@
                color: "white"
                font.family: "Segoe UI"
                font.pixelSize: 15
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            MouseArea {
                anchors.fill: parent
                onClicked: function(mouse) {
                    var r = button.radius, x = mouse.x, y = mouse.y
                    var cx = x < r ? r : x > width - r ? width - r : x
                    var cy = y < r ? r : y > height - r ? height - r : y
                    if ((x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r)
                        bridge.activate("button")
                }
            }
            Keys.onSpacePressed: bridge.activate("button")
            Keys.onReturnPressed: bridge.activate("button")
            SequentialAnimation on scale {
                running: true; loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: @PEAK@; duration: @HALF_DURATION@; easing.type: Easing.InOutSine }
                NumberAnimation { from: @PEAK@; to: 1.0; duration: @HALF_DURATION@; easing.type: Easing.InOutSine }
            }
        }
        Item {
            id: starItem
            objectName: "star"
            width: 120
            height: 120
            anchors.horizontalCenter: parent.horizontalCenter
            function points() {
                var result = []
                for (var i = 0; i < 10; i++) {
                    var angle = -Math.PI / 2 + i * Math.PI / 5
                    var radius = i % 2 === 0 ? 55 : 23
                    result.push([60 + radius * Math.cos(angle), 60 + radius * Math.sin(angle)])
                }
                return result
            }
            function inside(x, y) {
                var p = points(), hit = false
                for (var i = 0, j = p.length - 1; i < p.length; j = i++) {
                    if ((p[i][1] > y) !== (p[j][1] > y) &&
                        x < (p[j][0] - p[i][0]) * (y - p[i][1]) / (p[j][1] - p[i][1]) + p[i][0])
                        hit = !hit
                }
                return hit
            }
            Canvas {
                id: starCanvas
                anchors.fill: parent
                onPaint: {
                    var ctx = getContext("2d"), p = starItem.points()
                    ctx.clearRect(0, 0, width, height)
                    ctx.beginPath()
                    ctx.moveTo(p[0][0], p[0][1])
                    for (var i = 1; i < p.length; i++) ctx.lineTo(p[i][0], p[i][1])
                    ctx.closePath()
                    ctx.fillStyle = bridge.star
                    ctx.fill()
                }
                Connections { target: bridge; function onThemeChanged() { starCanvas.requestPaint() } }
            }
            MouseArea {
                anchors.fill: parent
                onClicked: function(mouse) {
                    if (starItem.inside(mouse.x, mouse.y)) bridge.activate("star")
                }
            }
        }
    }
}
'''


class Backend:
    def __init__(self, app):
        self.app = app
        self.bridge = Bridge(app)
        self.engine = QQmlApplicationEngine()
        self.engine.rootContext().setContextProperty("bridge", self.bridge)
        specs = {type(spec): spec for spec in app.window.children}
        source = QML
        values = {
            "WIDTH": str(app.window.width), "HEIGHT": str(app.window.height),
            "TITLE": json.dumps(app.window.title),
            "LABEL": json.dumps(specs[Label].text),
            "BUTTON": json.dumps(specs[Button].text),
            "FILL": json.dumps(specs[Button].fill or ""),
            "PEAK": str(specs[Button].pulse.peak_scale),
            "HALF_DURATION": str(specs[Button].pulse.duration_ms // 2),
        }
        for key, value in values.items():
            source = source.replace("@" + key + "@", value)
        self.engine.loadData(source.encode("utf-8"))
        if not self.engine.rootObjects():
            raise RuntimeError("Internal QML failed to load")
        self.window = self.engine.rootObjects()[0]
        self.items = {name: self.window.findChild(QObject, name) for name in ("label", "button", "star")}
        if any(item is None for item in self.items.values()):
            raise RuntimeError("Internal QML control mapping failed")

    def set_theme(self):
        self.bridge.themeChanged.emit()
