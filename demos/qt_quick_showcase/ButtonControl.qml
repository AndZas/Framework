import QtQuick
import QtQuick.Controls

Button {
    id: control
    property string controlId: ""
    property string overrideFill: ""
    property bool outlined: false
    property bool animated: false
    property bool animationEnabled: true
    activeFocusOnTab: true
    implicitHeight: 52
    implicitWidth: 190
    hoverEnabled: true
    padding: 12
    onClicked: bridge.activate(controlId)
    onActiveFocusChanged: if (activeFocus) bridge.setFocus(controlId)

    contentItem: Text {
        text: control.text
        color: control.outlined ? bridge.ink : "#ffffff"
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
        border.width: control.activeFocus ? 3 : (control.outlined ? 1 : 0)
        border.color: control.activeFocus ? bridge.focusColor : bridge.border
        gradient: Gradient {
            GradientStop { position: 0; color: control.outlined ? bridge.card : (control.overrideFill.length ? control.overrideFill : bridge.accent) }
            GradientStop { position: 1; color: control.outlined ? bridge.card : (control.overrideFill.length ? control.overrideFill : bridge.accentDeep) }
        }
        opacity: control.down ? 0.72 : (control.hovered ? 0.88 : 1.0)
        scale: control.down ? 0.97 : 1.0
        Behavior on scale { NumberAnimation { duration: 90 } }
    }
    SequentialAnimation on scale {
        running: control.animated && control.animationEnabled
        loops: Animation.Infinite
        NumberAnimation { from: 1; to: 1.10; duration: 450; easing.type: Easing.InOutSine }
        NumberAnimation { from: 1.10; to: 1; duration: 450; easing.type: Easing.InOutSine }
    }
}
