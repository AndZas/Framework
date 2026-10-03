import QtQuick
import QtQuick.Layouts

ColumnLayout {
    property var node
    spacing: 12
    Repeater {
        model: node ? node.childrenModel : null
        NodeView {
            required property var nodeData
            node: nodeData
        }
    }
}
