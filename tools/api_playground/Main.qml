import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    objectName: "playgroundWindow"
    visible: true
    width: 1000
    height: 760
    minimumWidth: 560
    minimumHeight: 440
    title: "API Playground — " + (views.currentIndex === 2 ? themeEditor.fileLabel : editor.fileLabel)
    color: "#f1f4f9"

    function openActiveFile() {
        if (views.currentIndex === 2) themeEditor.openFile()
        else editor.openFile()
    }
    function saveActiveFile() {
        if (views.currentIndex === 2) themeEditor.save()
        else editor.save()
    }
    function saveActiveFileAs() {
        if (views.currentIndex === 2) themeEditor.saveAs()
        else editor.saveAs()
    }

    onClosing: function(close) {
        close.accepted = editor.canClose
        if (!close.accepted)
            Qt.callLater(editor.requestClose)
    }

    Connections {
        target: editor
        function onCloseReady() { window.close() }
    }

    Shortcut { sequence: "F5"; enabled: !editor.closing; onActivated: editor.run() }
    Shortcut { sequence: "Shift+F5"; onActivated: runner.stop() }
    Shortcut { sequences: [StandardKey.Open]; enabled: !editor.closing; onActivated: window.openActiveFile() }
    Shortcut { sequences: [StandardKey.Save]; enabled: !editor.closing; onActivated: window.saveActiveFile() }
    Shortcut { sequence: "Ctrl+Shift+S"; enabled: !editor.closing; onActivated: window.saveActiveFileAs() }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8
        enabled: !editor.closing

        RowLayout {
            Button { objectName: "runButton"; text: "Run (F5)"; onClicked: editor.run() }
            Button { objectName: "stopButton"; text: "Stop"; enabled: runner.active; onClicked: runner.stop() }
            Button { objectName: "openButton"; text: views.currentIndex === 2 ? "Open Theme" : "Open"; onClicked: window.openActiveFile() }
            Button { objectName: "saveButton"; text: "Save"; onClicked: window.saveActiveFile() }
            Button { objectName: "saveAsButton"; text: "Save As"; onClicked: window.saveActiveFileAs() }
            Item { Layout.fillWidth: true }
        }
        Label {
            Layout.fillWidth: true
            text: views.currentIndex === 2 ? themeEditor.fileLabel : editor.fileLabel
            elide: Text.ElideMiddle
            color: "#23324d"
        }

        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Vertical

            ColumnLayout {
                SplitView.fillHeight: true
                SplitView.minimumHeight: views.currentIndex === 0 ? 120 : 228
                TabBar {
                    id: views
                    Layout.fillWidth: true
                    TabButton { objectName: "sourceTab"; text: "Python source" + (editor.fileLabel.endsWith(" *") ? " *" : "") }
                    TabButton { objectName: "docsTab"; text: "API Docs" }
                    TabButton { objectName: "themeTab"; text: "Theme" + (themeEditor.fileLabel.endsWith(" *") ? " *" : "") }
                }
                StackLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: views.currentIndex
                    ScrollView {
                        clip: true
                        TextArea {
                            id: source
                            objectName: "sourceEditor"
                            text: editor.source
                            onTextChanged: editor.source = text
                            font.family: codeFont.family
                            font.pointSize: 11
                            textFormat: TextEdit.PlainText
                            wrapMode: TextEdit.NoWrap
                            selectByMouse: true
                            persistentSelection: true
                            color: "#23324d"
                            background: Rectangle { color: "white"; border.color: "#c7d1e1" }
                            Keys.onPressed: function(event) {
                                if (event.key === Qt.Key_Tab && event.modifiers === Qt.NoModifier) {
                                    source.insert(source.cursorPosition, "    ")
                                    event.accepted = true
                                }
                            }
                        }
                    }
                    ApiDocs {}
                    ThemePane {}
                }
            }

            ColumnLayout {
                SplitView.preferredHeight: Math.min(200, window.height / 4)
                SplitView.minimumHeight: 90
                Label { text: "Output · " + runner.status; color: "#23324d" }
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    TextArea {
                        objectName: "outputPanel"
                        text: editor.output
                        onTextChanged: cursorPosition = length
                        readOnly: true
                        selectByMouse: true
                        font.family: codeFont.family
                        font.pointSize: 10
                        textFormat: TextEdit.PlainText
                        wrapMode: TextEdit.Wrap
                        color: "#23324d"
                        background: Rectangle { color: "#e8edf5" }
                    }
                }
            }
        }
    }
}
