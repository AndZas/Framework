import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pane
    objectName: "apiDocsPane"
    spacing: 6

    function revealSelection(start, end) {
        if (start < 0) {
            document.deselect()
            return
        }
        document.select(start, end)
        Qt.callLater(function() {
            const rect = document.positionToRectangle(start)
            const flick = scroll.contentItem
            flick.contentY = Math.max(0, Math.min(rect.y + document.y - 24, flick.contentHeight - flick.height))
            flick.contentX = Math.max(0, Math.min(rect.x + document.x - 24, flick.contentWidth - flick.width))
        })
    }

    Shortcut {
        sequences: [StandardKey.Find]
        enabled: pane.visible
        onActivated: { search.forceActiveFocus(); search.selectAll() }
    }
    Shortcut { sequence: "F3"; enabled: pane.visible; onActivated: apiDocs.nextMatch() }
    Shortcut { sequence: "Shift+F3"; enabled: pane.visible; onActivated: apiDocs.previousMatch() }

    RowLayout {
        Layout.fillWidth: true
        Label { text: "docs/api.md"; color: "#23324d" }
        Item { Layout.fillWidth: true }
        Button { objectName: "reloadDocsButton"; text: "Reload"; onClicked: apiDocs.reload() }
    }
    RowLayout {
        Layout.fillWidth: true
        TextField {
            id: search
            objectName: "docsSearch"
            Layout.fillWidth: true
            Layout.minimumWidth: 80
            placeholderText: "Find in API Docs (Ctrl+F)"
            text: apiDocs.query
            onTextChanged: apiDocs.query = text
            onAccepted: apiDocs.nextMatch()
            Keys.onEscapePressed: { text = ""; document.forceActiveFocus() }
        }
        Label { objectName: "docsSearchStatus"; text: apiDocs.searchStatus; color: "#23324d" }
        Button { objectName: "previousDocsMatch"; text: "Previous"; enabled: apiDocs.hasMatches; onClicked: apiDocs.previousMatch() }
        Button { objectName: "nextDocsMatch"; text: "Next"; enabled: apiDocs.hasMatches; onClicked: apiDocs.nextMatch() }
        Button { objectName: "clearDocsSearch"; text: "Clear"; enabled: search.text.length > 0; onClicked: search.text = "" }
    }
    Label {
        objectName: "docsError"
        Layout.fillWidth: true
        visible: apiDocs.error.length > 0
        text: apiDocs.error
        textFormat: Text.PlainText
        wrapMode: Text.WrapAnywhere
        color: "#9c2635"
    }
    ScrollView {
        id: scroll
        objectName: "docsScroll"
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        visible: apiDocs.error.length === 0
        background: Rectangle { color: "white"; border.color: "#c7d1e1" }
        Flickable {
            id: docsFlick
            contentWidth: Math.max(width, document.contentWidth + 32)
            contentHeight: document.height + 32
            boundsBehavior: Flickable.StopAtBounds
            TextEdit {
                id: document
                objectName: "docsDocument"
                x: 16
                y: 16
                width: docsFlick.width - 32
                height: contentHeight
                text: apiDocs.markdown
                baseUrl: apiDocs.baseUrl
                textFormat: TextEdit.MarkdownText
                wrapMode: TextEdit.Wrap
                readOnly: true
                selectByMouse: true
                persistentSelection: true
                font.family: "Segoe UI"
                font.pointSize: 11
                color: "#23324d"
                selectionColor: "#365a94"
                selectedTextColor: "white"
                onLinkActivated: function(link) { apiDocs.followLink(link) }
                Component.onCompleted: apiDocs.attachView(document)
                onContentWidthChanged: Qt.callLater(apiDocs.keepOverflowVisible)
                onContentHeightChanged: Qt.callLater(apiDocs.keepOverflowVisible)
                Keys.onEscapePressed: search.text = ""
            }
        }
    }
    Item { Layout.fillHeight: true; visible: apiDocs.error.length > 0 }
    Label {
        objectName: "docsLinkStatus"
        Layout.fillWidth: true
        visible: apiDocs.linkStatus.length > 0
        text: apiDocs.linkStatus
        textFormat: Text.PlainText
        wrapMode: Text.WrapAnywhere
        color: "#23324d"
    }
    Connections {
        target: apiDocs
        function onSelectionRequested(start, end) { pane.revealSelection(start, end) }
    }
}
