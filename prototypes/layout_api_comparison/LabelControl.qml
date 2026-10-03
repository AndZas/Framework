import QtQuick

Text {
    property var node
    objectName: node ? node.nodeId : ""
    text: node ? node.text : ""
    color: "#23324d"
    font.family: "Segoe UI"
    font.pixelSize: node && node.heading ? 24 : 15
    font.bold: node && node.heading
    wrapMode: Text.Wrap
}
