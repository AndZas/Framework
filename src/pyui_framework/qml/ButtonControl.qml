import QtQuick
import QtQuick.Controls

Button {
    id: button
    Style { id: tokens }
    property var node
    objectName: node ? node.nodeId : ""
    text: node ? node.text : ""
    padding: tokens.spacing
    implicitHeight: Math.max(48, contentItem.implicitHeight + topPadding + bottomPadding)
    activeFocusOnTab: true
    contentItem: Text {
        text: button.text
        color: tokens.accentText
        font.family: tokens.family
        font.pixelSize: tokens.bodySize
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: tokens.radius
        color: button.down ? tokens.pressed : button.hovered ? tokens.hover : tokens.accent
        border.width: button.activeFocus ? 2 : 0
        border.color: tokens.focus
    }
    onClicked: bridge.activate(node.nodeId)
}
