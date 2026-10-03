import QtQuick
import QtQuick.Layouts

Item {
    id: host
    required property var node
    Layout.fillWidth: true
    Layout.minimumWidth: 0
    Layout.preferredWidth: 1
    implicitHeight: loader.item ? loader.item.implicitHeight : 0
    height: implicitHeight
    Loader {
        id: loader
        anchors.fill: parent
        source: host.node.kind === "column" ? "ColumnControl.qml"
              : host.node.kind === "row" ? "RowControl.qml"
              : host.node.kind === "button" ? "ButtonControl.qml" : "LabelControl.qml"
        onLoaded: item.node = Qt.binding(function() { return host.node })
    }
}
