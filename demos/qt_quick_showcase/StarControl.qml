import QtQuick
import QtQuick.Shapes

Item {
    id: control
    property string controlId: "star"
    property bool hovered: false
    property bool pressed: false
    width: 112
    height: 112
    activeFocusOnTab: true
    onActiveFocusChanged: if (activeFocus) bridge.setFocus(controlId)
    Keys.onSpacePressed: function(event) { bridge.activate(controlId); event.accepted = true }
    Keys.onReturnPressed: function(event) { bridge.activate(controlId); event.accepted = true }
    Keys.onEnterPressed: function(event) { bridge.activate(controlId); event.accepted = true }

    // These ten vertices are shared by drawing and the polygon hit test.
    readonly property var vertices: [[56,4], [68,39], [107,39], [76,64], [88,105],
                                     [56,80], [24,105], [36,64], [5,39], [44,39]]
    function containsPoint(x, y) {
        var inside = false
        for (var i = 0, j = vertices.length - 1; i < vertices.length; j = i++) {
            var a = vertices[i], b = vertices[j]
            if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) inside = !inside
        }
        return inside
    }
    Shape {
        anchors.fill: parent
        opacity: control.pressed ? 0.72 : 1.0
        ShapePath {
            strokeWidth: control.activeFocus ? 4 : 2
            strokeColor: control.activeFocus ? bridge.focusColor : bridge.border
            fillGradient: LinearGradient {
                x1: 0; y1: 0; x2: 112; y2: 112
                GradientStop { position: 0; color: bridge.star }
                GradientStop { position: 1; color: bridge.accent }
            }
            startX: 56; startY: 4
            PathLine { x: 68; y: 39 }
            PathLine { x: 107; y: 39 }
            PathLine { x: 76; y: 64 }
            PathLine { x: 88; y: 105 }
            PathLine { x: 56; y: 80 }
            PathLine { x: 24; y: 105 }
            PathLine { x: 36; y: 64 }
            PathLine { x: 5; y: 39 }
            PathLine { x: 44; y: 39 }
            PathLine { x: 56; y: 4 }
        }
    }
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onPositionChanged: function(mouse) { control.hovered = control.containsPoint(mouse.x, mouse.y) }
        onExited: control.hovered = false
        onPressed: function(mouse) { control.pressed = control.containsPoint(mouse.x, mouse.y); if (control.pressed) control.forceActiveFocus() }
        onReleased: control.pressed = false
        onClicked: function(mouse) { if (control.containsPoint(mouse.x, mouse.y)) bridge.activate(control.controlId) }
    }
    scale: pressed ? 0.90 : (hovered ? 1.07 : 1.0)
    Behavior on scale { NumberAnimation { duration: 120 } }
}
