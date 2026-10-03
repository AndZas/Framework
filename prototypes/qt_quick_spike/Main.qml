import QtQuick
import QtQuick.Window
import QtMultimedia

Window {
    id: root
    objectName: "mainWindow"
    width: 760
    height: 650
    x: 20
    y: 80
    visible: true
    title: "Qt Quick feasibility spike"
    property bool dark: false
    property int roundedClicks: 0
    property int starClicks: 0
    property int keyCount: 0
    property int pointerCount: 0
    property bool stressEnabled: false
    property color surface: dark ? "#182538" : "#edf3fc"
    property color ink: dark ? "#f4f8ff" : "#182538"
    property color accent: dark ? "#48d8c1" : "#3868d9"
    color: surface

    function starPoints(cx, cy, outer, inner) {
        let points = []
        for (let i = 0; i < 10; ++i) {
            let angle = -Math.PI / 2 + i * Math.PI / 5
            let radius = i % 2 === 0 ? outer : inner
            points.push([cx + Math.cos(angle) * radius,
                         cy + Math.sin(angle) * radius])
        }
        return points
    }
    function insideStar(x, y) {
        let p = starPoints(60, 60, 55, 23)
        let inside = false
        for (let i = 0, j = p.length - 1; i < p.length; j = i++) {
            if ((p[i][1] > y) !== (p[j][1] > y) &&
                x < (p[j][0] - p[i][0]) * (y - p[i][1]) /
                    (p[j][1] - p[i][1]) + p[i][0])
                inside = !inside
        }
        return inside
    }
    function insideRounded(x, y) {
        let r = 15
        if (x >= r && x <= 155 - r) return y >= 0 && y <= 42
        if (y >= r && y <= 42 - r) return x >= 0 && x <= 155
        let cx = x < r ? r : 155 - r
        let cy = y < r ? r : 42 - r
        return (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r
    }

    Item {
        id: inputItem
        objectName: "inputItem"
        anchors.fill: parent
        focus: true
        Keys.onPressed: (event) => { root.keyCount++; keyReadout.text = "Keys: " + root.keyCount + " (" + event.text + ")" }
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onPressed: root.pointerCount++
        }
    }

    Text {
        x: 24; y: 16
        text: "Theme, shape, input, animation, media, stress"
        color: root.ink
        font.pixelSize: 20
    }
    Rectangle {
        id: themeButton
        objectName: "themeButton"
        x: 24; y: 55; width: 155; height: 42; radius: 15
        color: root.accent
        border.width: 2
        border.color: root.dark ? "white" : "#193c91"
        opacity: 0.85
        Text { anchors.centerIn: parent; text: root.dark ? "Light theme" : "Dark theme"; color: "white" }
        MouseArea { anchors.fill: parent; onClicked: root.dark = !root.dark }
    }
    Rectangle {
        id: rounded
        objectName: "roundedControl"
        x: 198; y: 55; width: 155; height: 42; radius: 15
        gradient: Gradient {
            GradientStop { position: 0; color: root.accent }
            GradientStop { position: 1; color: root.dark ? "#28617e" : "#8548d4" }
        }
        border.width: 2; border.color: "#ffffff"
        opacity: 0.82
        Text { anchors.centerIn: parent; text: "Rounded: " + root.roundedClicks; color: "white" }
        MouseArea {
            anchors.fill: parent
            onPressed: (mouse) => { if (!root.insideRounded(mouse.x, mouse.y)) mouse.accepted = false }
            onClicked: (mouse) => { if (root.insideRounded(mouse.x, mouse.y)) root.roundedClicks++ }
        }
    }
    Rectangle {
        x: 372; y: 55; width: 155; height: 42; radius: 15
        color: "#d86642" // per-control override; independent of theme
        Text { anchors.centerIn: parent; text: "Override color"; color: "white" }
    }
    Text { id: keyReadout; x: 24; y: 112; text: "Keys: 0"; color: root.ink }
    Text { x: 200; y: 112; text: "Pointer presses: " + root.pointerCount; color: root.ink }

    Canvas {
        id: star
        objectName: "starControl"
        x: 35; y: 145; width: 120; height: 120
        opacity: 0.8
        onPaint: {
            let ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            let p = root.starPoints(60, 60, 55, 23)
            let g = ctx.createLinearGradient(0, 0, 120, 120)
            g.addColorStop(0, "#ffe46b")
            g.addColorStop(1, root.dark ? "#ef697a" : "#d3448d")
            ctx.beginPath()
            ctx.moveTo(p[0][0], p[0][1])
            for (let i = 1; i < p.length; ++i) ctx.lineTo(p[i][0], p[i][1])
            ctx.closePath()
            ctx.fillStyle = g
            ctx.fill()
            ctx.strokeStyle = "#36214e"
            ctx.lineWidth = 3
            ctx.stroke()
        }
        Connections { target: root; function onDarkChanged() { star.requestPaint() } }
        MouseArea {
            anchors.fill: parent
            onPressed: (mouse) => {
                if (!root.insideStar(mouse.x, mouse.y)) mouse.accepted = false
            }
            onClicked: (mouse) => {
                if (root.insideStar(mouse.x, mouse.y)) root.starClicks++
            }
        }
    }
    Text { x: 170; y: 185; text: "Star clicks: " + root.starClicks + "\nClick visible star, then empty corners"; color: root.ink }

    Rectangle {
        id: animated
        objectName: "animatedItem"
        x: 30; y: 290; width: 36; height: 36; radius: 8
        color: root.accent
        SequentialAnimation on x {
            loops: Animation.Infinite
            NumberAnimation { from: 30; to: 610; duration: 1300; easing.type: Easing.InOutQuad }
            NumberAnimation { from: 610; to: 30; duration: 1300; easing.type: Easing.InOutQuad }
        }
        RotationAnimation on rotation { from: 0; to: 360; duration: 1900; loops: Animation.Infinite }
    }
    Text { x: 24; y: 336; text: "Animated x: " + Math.round(animated.x); color: root.ink }

    Rectangle {
        x: 24; y: 370; width: 710; height: 250
        color: root.dark ? "#30445e" : "#d6e1f2"
        clip: true
        Image {
            id: largeImage
            anchors.fill: parent
            source: imageUrl
            opacity: 0.35
            fillMode: Image.PreserveAspectCrop
        }
        Repeater {
            model: root.stressEnabled ? 400 : 0
            Rectangle {
                width: 8; height: 8; radius: 4
                color: Qt.rgba((index % 13) / 13, 0.4, 0.85, 0.8)
                y: Math.floor(index / 40) * 23 + 10
                SequentialAnimation on x {
                    loops: Animation.Infinite
                    NumberAnimation { from: -10; to: 715; duration: 1100 + (index % 17) * 60 }
                    NumberAnimation { from: 715; to: -10; duration: 1100 + (index % 17) * 60 }
                }
            }
        }
        Text {
            anchors.top: parent.top; anchors.left: parent.left
            text: root.stressEnabled ? "Stress: 400 animated items + 2048px image" : "Stress idle (press S)"
            color: "#111111"
        }
        MouseArea { anchors.fill: parent; onClicked: root.stressEnabled = !root.stressEnabled }
    }
    Shortcut { sequence: "S"; onActivated: root.stressEnabled = !root.stressEnabled }

    MediaPlayer {
        id: player
        objectName: "mediaPlayer"
        source: mediaUrl
        audioOutput: AudioOutput { }
        videoOutput: videoOutput
    }
    VideoOutput { id: videoOutput; x: 540; y: 105; width: 190; height: 130 }
    Component.onCompleted: { if (mediaUrl.toString().length > 0) player.play() }
}
