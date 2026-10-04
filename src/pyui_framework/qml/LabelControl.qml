import QtQuick

Text {
    Style { id: tokens }
    property var node
    objectName: node ? node.nodeId : ""
    text: node ? node.text : ""
    color: node ? node.appearance.foreground : "transparent"
    opacity: node ? node.appearance.opacity : 1
    font.family: tokens.family
    font.pixelSize: node && node.heading ? tokens.headingSize : tokens.bodySize
    font.bold: node && node.heading
    wrapMode: Text.Wrap
    Rectangle {
        anchors.fill: parent
        z: -1
        color: node ? node.appearance.panel : "transparent"
        radius: node ? node.appearance.radius : 0
    }
}
