import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: window
    width: initialWidth
    height: initialHeight
    minimumWidth: 280
    minimumHeight: 260
    title: windowTitle
    visible: true
    color: "#f1f4f9"

    Flickable {
        id: viewport
        objectName: "viewport"
        anchors.fill: parent
        anchors.margins: 20
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
