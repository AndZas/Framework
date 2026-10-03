import QtQuick
import QtQuick.Controls

Button {
    id: button
    property string controlId: ""
    property string customFill: ""
    property int pulseDuration: 0
    property real pulsePeak: 1.0

    width: Math.min(440, parent ? parent.width : 440)
    height: 60
    text: ""
    padding: 10
    activeFocusOnTab: true

    contentItem: Text {
        text: button.text
        color: "white"
        font.family: "Segoe UI"
        font.pixelSize: 15
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WordWrap
        maximumLineCount: 2
        elide: Text.ElideRight
    }
    background: Rectangle {
        radius: 16
        color: button.customFill.length ? button.customFill : bridge.accent
        border.width: button.activeFocus ? 2 : 0
        border.color: bridge.ink
        opacity: button.down ? 0.84 : 1.0
    }
    onClicked: bridge.activate(controlId)
    SequentialAnimation on scale {
        running: button.pulseDuration > 0
        loops: Animation.Infinite
        NumberAnimation { from: 1; to: button.pulsePeak; duration: button.pulseDuration / 2; easing.type: Easing.InOutSine }
        NumberAnimation { from: button.pulsePeak; to: 1; duration: button.pulseDuration / 2; easing.type: Easing.InOutSine }
    }
}
