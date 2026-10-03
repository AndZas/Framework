import QtQuick
import QtQuick.Window

Window {
    width: 360
    height: 240
    x: 780
    y: 100
    visible: true
    title: "Qt Quick spike: independent window"
    color: "#202c40"

    Text {
        anchors.centerIn: parent
        color: "white"
        text: "Second top-level window"
        font.pixelSize: 20
    }
}
