import QtQuick

Text {
    id: label
    Style { id: tokens }
    property var node
    AnimatedAppearance { id: motion; node: label.node }
    objectName: node ? node.nodeId : ""
    text: node ? node.text : ""
    color: motion.value("foreground", node ? node.appearance.foreground : "transparent")
    opacity: motion.value("opacity", node ? node.appearance.opacity : 1)
    scale: motion.value("scale", 1)
    font.family: tokens.family
    font.pixelSize: node && node.heading ? tokens.headingSize : tokens.bodySize
    font.bold: node && node.heading
    wrapMode: Text.Wrap
    Rectangle {
        anchors.fill: parent
        z: -1
        color: motion.value("panel", node ? node.appearance.panel : "transparent")
        radius: motion.value("radius", node ? node.appearance.radius : 0)
    }
}
