import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1040
    height: 820
    minimumWidth: 620
    minimumHeight: 420
    visible: true
    title: "Theme studio · TASK-0008"
    color: lab.palette.background
    component Copy: Text {
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        color: lab.palette.foreground
        font.family: "Segoe UI"
        font.pixelSize: 15
        wrapMode: Text.Wrap
    }
    component Card: Rectangle {
        color: lab.palette.panel
        radius: lab.palette.radius
        Layout.fillWidth: true
        border.color: lab.palette.accent
        border.width: 1
    }
    Flickable {
        id: viewport
        anchors.fill: parent
        anchors.margins: 28
        contentWidth: width
        contentHeight: body.implicitHeight
        clip: true
        acceptedButtons: Qt.NoButton
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar {}
        ColumnLayout {
            id: body
            width: viewport.width
            spacing: 18
            Copy { text: "EXPERIMENT  /  0008"; font.pixelSize: 12; font.letterSpacing: 2 }
            Copy { text: "One palette. Two ways to write it."; font.pixelSize: 32; font.bold: true }
            Copy { text: "Reusable themes meet independent widget styling. Switch the source and watch the same controls resolve their appearance live." }
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                Repeater {
                    model: ["Light", "Dark", "System", "CSS", "Python"]
                    LabButton {
                        required property string modelData
                        objectName: "select" + modelData
                        text: modelData
                        Layout.fillWidth: true
                        onClicked: lab.select(modelData)
                    }
                }
            }
            Copy { text: lab.system; font.pixelSize: 12 }
            Card {
                implicitHeight: hero.implicitHeight + 40
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0; color: lab.gradientStart }
                    GradientStop { position: 1; color: lab.gradientEnd }
                }
                ColumnLayout {
                    id: hero
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 8
                    Copy { text: "A shared visual language"; color: "#ffffff"; font.pixelSize: 23; font.bold: true }
                    Copy { text: "Background · foreground · accent · radius · opacity · linear gradient"; color: "#ffffff" }
                }
            }
            Card {
                implicitHeight: samples.implicitHeight + 40
                ColumnLayout {
                    id: samples
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 12
                    Copy { text: "Global theme → local intent"; font.pixelSize: 21; font.bold: true }
                    Copy { text: "Built-in defaults < theme tokens < explicit widget style. Amber widgets start equivalent; update only the constructor example, or clear its override." }
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        LabButton { objectName: "globalSample"; text: "Global style"; Layout.fillWidth: true; onClicked: lab.select("Python") }
                        LabButton { objectName: "localSample"; text: "Constructor style"; tokens: localWidget.appearance; Layout.fillWidth: true; onClicked: lab.update_local() }
                        LabButton { objectName: "methodSample"; text: "Method style"; tokens: methodWidget.appearance; Layout.fillWidth: true; onClicked: lab.update_local() }
                    }
                    Copy {
                        text: "Global radius " + lab.palette.radius + " / opacity " + lab.palette.opacity
                            + "    ·    Local accent " + localWidget.appearance.accent
                            + " / radius " + localWidget.appearance.radius + " / opacity " + localWidget.appearance.opacity
                        font.pixelSize: 13
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        LabButton { objectName: "updateLocal"; text: "Update local style from Python"; Layout.fillWidth: true; onClicked: lab.update_local() }
                        LabButton { objectName: "clearLocal"; text: "Clear local override"; Layout.fillWidth: true; onClicked: lab.clear_local() }
                    }
                }
            }
            Card {
                implicitHeight: files.implicitHeight + 40
                ColumnLayout {
                    id: files
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10
                    Copy { text: "Try your own theme file"; font.pixelSize: 21; font.bold: true }
                    Copy { text: "Edit lagoon.theme and reload, or paste another path. Invalid input retains the current theme and local styles." }
                    RowLayout {
                        Layout.fillWidth: true
                        TextField {
                            id: path
                            objectName: "themePath"
                            text: lab.defaultPath
                            Layout.fillWidth: true
                            Layout.minimumWidth: 0
                            selectByMouse: true
                            color: lab.palette.foreground
                            selectionColor: lab.palette.accent
                            selectedTextColor: lab.palette.accent_text
                            padding: 12
                            background: Rectangle {
                                color: lab.palette.background
                                radius: 8
                                border.width: path.activeFocus ? 2 : 1
                                border.color: lab.palette.accent
                            }
                        }
                        LabButton { objectName: "loadFile"; text: "Load / reload"; onClicked: lab.load(path.text) }
                    }
                }
            }
            Copy { objectName: "status"; text: lab.status; font.pixelSize: 13 }
            Copy { text: "Prototype grammar: one :theme block, eight tokens, no browser CSS promise.\nCSS and Python are equivalent for Lagoon. API names remain proposals for owner review."; font.pixelSize: 12 }
        }
    }
}
