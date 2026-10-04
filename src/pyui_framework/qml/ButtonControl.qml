import QtQuick
import QtQuick.Controls

Button {
    id: button
    Style { id: tokens }
    property var node
    objectName: node ? node.nodeId : ""
    text: node ? node.text : ""
    opacity: node ? node.appearance.opacity : 1
    padding: tokens.spacing
    implicitHeight: Math.max(48, contentItem.implicitHeight + topPadding + bottomPadding)
    activeFocusOnTab: true
    contentItem: Text {
        text: button.text
        color: button.node ? button.node.appearance.accent_text : "transparent"
        font.family: tokens.family
        font.pixelSize: tokens.bodySize
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: button.node ? button.node.appearance.radius : 0
        color: button.node ? button.node.appearance.accent : "transparent"
        gradient: button.node && button.node.appearance.hasGradient ? fillGradient : null
        Gradient {
            id: fillGradient
            orientation: Gradient.Horizontal
            GradientStop { position: 0; color: button.node ? button.node.appearance.gradientStart : "transparent" }
            GradientStop { position: 1; color: button.node ? button.node.appearance.gradientEnd : "transparent" }
        }
        border.width: button.activeFocus ? 2 : 0
        border.color: button.node ? button.node.appearance.accent_text : "transparent"
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: button.down ? "#25000000" : button.hovered ? "#18ffffff" : "transparent"
        }
    }
    onClicked: bridge.activate(node.nodeId)
}
