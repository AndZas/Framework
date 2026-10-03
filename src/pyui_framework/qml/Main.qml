import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: window
    Style { id: tokens }
    width: initialWidth
    height: initialHeight
    minimumWidth: 280
    minimumHeight: 260
    title: windowTitle
    visible: true
    color: tokens.surface

    Flickable {
        id: viewport
        objectName: "viewport"
        anchors.fill: parent
        anchors.margins: tokens.margin
        clip: true
        contentWidth: width
        contentHeight: body.height
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar {}
        NodeView {
            id: body
            width: viewport.width
            node: rootNode
        }
    }
}
