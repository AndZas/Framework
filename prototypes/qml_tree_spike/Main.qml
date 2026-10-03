import QtQuick
import QtQuick.Window

Window {
    id: root
    width: bridge.initialWidth
    height: bridge.initialHeight
    visible: true
    title: bridge.title
    color: bridge.surface

    function controlAt(index) {
        var row = repeated.itemAt(index)
        return row ? row.control : null
    }
    function scrollTo(index) {
        var row = repeated.itemAt(index)
        if (row) list.contentY = Math.max(0, Math.min(row.y - 12, list.contentHeight - list.height))
    }
    Flickable {
        id: list
        anchors.fill: parent
        anchors.margins: 16
        clip: true
        contentWidth: width
        contentHeight: stack.implicitHeight
        Column {
            id: stack
            width: list.width
            spacing: 10
            Text {
                width: stack.width
                height: 34
                text: "Python-authored dynamic tree"
                color: bridge.ink
                font.pixelSize: 20
                elide: Text.ElideRight
            }
            Repeater {
                id: repeated
                model: controlsModel
                delegate: Item {
                    id: row
                    required property string controlId
                    required property string kind
                    required property string label
                    required property string fill
                    required property int pulseDuration
                    required property real pulsePeak
                    width: stack.width
                    height: kind === "star" ? 100 : 60
                    property var control: controlLoader.item
                    Loader {
                        id: controlLoader
                        width: row.width
                        height: row.height
                        sourceComponent: row.kind === "star" ? starComponent : buttonComponent
                    }
                    Component {
                        id: buttonComponent
                        ButtonControl {
                            controlId: row.controlId
                            text: row.label
                            customFill: row.fill
                            pulseDuration: row.pulseDuration
                            pulsePeak: row.pulsePeak
                        }
                    }
                    Component {
                        id: starComponent
                        StarControl {
                            controlId: row.controlId
                            customFill: row.fill
                            pulseDuration: row.pulseDuration
                            pulsePeak: row.pulsePeak
                        }
                    }
                }
            }
        }
    }
}
