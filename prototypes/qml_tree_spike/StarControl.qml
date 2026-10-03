import QtQuick
import QtQuick.Shapes

Item {
    id: star
    property string controlId: ""
    property string customFill: ""
    property int pulseDuration: 0
    property real pulsePeak: 1.0
    width: 100
    height: 100

    // The hit polygon uses exactly the ShapePath's vertices (50,4; 61,36; ...).
    readonly property var vertices: [[50,4], [61,36], [96,36], [68,57], [79,92],
                                     [50,70], [21,92], [32,57], [4,36], [39,36]]
    function containsPoint(x, y) {
        var inside = false
        for (var i = 0, j = vertices.length - 1; i < vertices.length; j = i++) {
            var a = vertices[i], b = vertices[j]
            if ((a[1] > y) !== (b[1] > y) &&
                x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0])
                inside = !inside
        }
        return inside
    }
    Shape {
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeWidth: 2
            strokeColor: bridge.ink
            fillGradient: LinearGradient {
                x1: 8; y1: 8; x2: 92; y2: 92
                GradientStop { position: 0; color: star.customFill.length ? star.customFill : bridge.star }
                GradientStop { position: 1; color: bridge.accent }
            }
            startX: 50; startY: 4
            PathLine { x: 61; y: 36 }
            PathLine { x: 96; y: 36 }
            PathLine { x: 68; y: 57 }
            PathLine { x: 79; y: 92 }
            PathLine { x: 50; y: 70 }
            PathLine { x: 21; y: 92 }
            PathLine { x: 32; y: 57 }
            PathLine { x: 4; y: 36 }
            PathLine { x: 39; y: 36 }
            PathLine { x: 50; y: 4 }
        }
    }
    MouseArea {
        anchors.fill: parent
        onClicked: function(mouse) {
            if (star.containsPoint(mouse.x, mouse.y)) bridge.activate(star.controlId)
        }
    }
    SequentialAnimation on scale {
        running: star.pulseDuration > 0
        loops: Animation.Infinite
        NumberAnimation { from: 1; to: star.pulsePeak; duration: star.pulseDuration / 2 }
        NumberAnimation { from: star.pulsePeak; to: 1; duration: star.pulseDuration / 2 }
    }
}
