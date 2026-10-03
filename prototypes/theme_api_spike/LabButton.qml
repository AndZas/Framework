import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property var tokens: lab.palette
    Layout.minimumWidth: 0
    padding: 14
    implicitHeight: Math.max(48, contentItem.implicitHeight + 24)
    activeFocusOnTab: true
    opacity: tokens.opacity
    contentItem: Text {
        text: control.text
        color: control.tokens.accent_text
        font.family: "Segoe UI"
        font.pixelSize: 14
        font.bold: true
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        color: control.tokens.accent
        radius: control.tokens.radius
        border.width: control.activeFocus || control.hovered ? 2 : 0
        border.color: control.tokens.foreground
        scale: control.down ? 0.98 : 1
    }
}
