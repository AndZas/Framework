import QtQuick
import QtQuick.Controls

Button {
    id: button
    property var node
    objectName: node ? node.nodeId : ""
    text: node ? node.text : ""
    padding: 12
    implicitHeight: Math.max(48, contentItem.implicitHeight + topPadding + bottomPadding)
    activeFocusOnTab: true
    contentItem: Text {
        text: button.text
        color: "white"
        font.family: "Segoe UI"
        font.pixelSize: 15
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        radius: 10
        color: button.down ? "#294475" : button.hovered ? "#4468a3" : "#365a94"
        border.width: button.activeFocus ? 2 : 0
        border.color: "#e0aa35"
    }
    onClicked: bridge.activate(node.nodeId)
}
