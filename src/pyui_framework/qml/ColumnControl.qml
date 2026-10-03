import QtQuick
import QtQuick.Layouts

ColumnLayout {
    Style { id: tokens }
    property var node
    spacing: tokens.spacing
    Repeater {
        model: node ? node.childrenModel : null
        NodeView {
            required property var nodeData
            node: nodeData
        }
    }
}
