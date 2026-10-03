import QtQuick

Text {
    Style { id: tokens }
    property var node
    objectName: node ? node.nodeId : ""
    text: node ? node.text : ""
    color: tokens.ink
    font.family: tokens.family
    font.pixelSize: node && node.heading ? tokens.headingSize : tokens.bodySize
    font.bold: node && node.heading
    wrapMode: Text.Wrap
}
