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
        // Desktop actions use left clicks, even while wheel scrolling moves
        // the view. Do not let Flickable filter them as drag/flick gestures.
        // Wheel and the scrollbar still scroll; touch policy is unchanged.
        acceptedButtons: Qt.NoButton
        ScrollBar.vertical: ScrollBar {
            objectName: "verticalScrollBar"
            // Keep the attached scroll behavior, but escape the clipped inset.
            parent: window.contentItem
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }
        NodeView {
            id: body
            width: viewport.width
            node: rootNode
        }
    }
}
