import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    spacing: 6
    RowLayout {
        Button { objectName: "validateThemeButton"; text: "Validate"; onClicked: themeEditor.validate() }
        Button { objectName: "previewThemeButton"; text: "Preview Theme"; onClicked: editor.previewTheme() }
        Item { Layout.fillWidth: true }
    }
    Label {
        Layout.fillWidth: true
        text: "Preview replaces the running child. Run (F5) relaunches Python source."
        wrapMode: Text.Wrap
        color: "#23324d"
    }
    ScrollView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.minimumHeight: 55
        clip: true
        TextArea {
            id: theme
            objectName: "themeSourceEditor"
            text: themeEditor.source
            onTextChanged: themeEditor.source = text
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
                    theme.insert(theme.cursorPosition, "    ")
                    event.accepted = true
                }
            }
        }
    }
    ScrollView {
        Layout.fillWidth: true
        Layout.preferredHeight: Math.min(65, themeDiagnostic.implicitHeight)
        clip: true
        TextArea {
            id: themeDiagnostic
            objectName: "themeDiagnostic"
            text: themeEditor.validation
            readOnly: true
            selectByMouse: true
            textFormat: TextEdit.PlainText
            wrapMode: TextEdit.Wrap
            color: themeEditor.valid ? "#126e67" : "#23324d"
            background: Rectangle { color: "#e8edf5" }
        }
    }
}
