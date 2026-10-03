import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

Window {
    id: root
    objectName: "showcaseWindow"
    width: 1180
    height: 790
    minimumWidth: 930
    minimumHeight: 650
    visible: true
    title: bridge.windowTitle
    color: bridge.surface
    property int pageIndex: 0
    property var pageNames: ["Controls & shapes", "Themes", "Animation", "Dynamic & windows", "Input", "Media & devices", "Performance", "Diagnostics"]
    function showPage(index) { pageIndex = index }
    function controlById(key) {
        if (key === "hello") return helloButton
        if (key === "orange") return orangeButton
        if (key === "star") return starControl
        if (key === "animation") return animatedButton
        if (key === "dynamic-1") return dynamicRepeater.itemAt(0)
        return null
    }
    function playSampleMedia() { videoPlayer.play(); audioPlayer.play() }
    function stopSampleMedia() { videoPlayer.stop(); audioPlayer.stop() }
    function mediaStates() { return [videoPlayer.playbackState, videoPlayer.mediaStatus, audioPlayer.playbackState, audioPlayer.mediaStatus] }
    function dynamicCount() { return dynamicRepeater.count }
    function secondWindowVisible() { return secondWindow.visible }
    function statusPillColor() { return bridge.themeMode === "Dark" ? "#33435c" : "#eaf0fb" }

    Rectangle {
        id: sidebar
        width: 238
        height: parent.height
        color: bridge.card
        border.color: bridge.border
        Column {
            anchors.fill: parent
            anchors.margins: 19
            spacing: 10
            Text { text: "✦   FRAMEWORK LAB"; color: bridge.accent; font.family: "Segoe UI"; font.pixelSize: 16; font.bold: true }
            Text { width: parent.width; text: "Qt Quick candidate\nowner showcase"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 22; font.bold: true; wrapMode: Text.WordWrap }
            Text { width: parent.width; text: "Explore the controls, media and visual load. This is a demo, not an architecture decision."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 12; wrapMode: Text.WordWrap }
            Item { width: 1; height: 12 }
            Repeater {
                model: root.pageNames
                delegate: Button {
                    required property string modelData
                    required property int index
                    width: sidebar.width - 38
                    height: 43
                    text: modelData
                    hoverEnabled: true
                    activeFocusOnTab: true
                    onClicked: root.showPage(index)
                    contentItem: Text { text: parent.text; color: root.pageIndex === index ? "#ffffff" : bridge.ink; font.family: "Segoe UI"; font.pixelSize: 14; font.bold: root.pageIndex === index; verticalAlignment: Text.AlignVCenter; leftPadding: 15 }
                    background: Rectangle { radius: 11; color: root.pageIndex === index ? bridge.accent : (parent.hovered ? bridge.surface : bridge.card); border.color: parent.activeFocus ? bridge.focusColor : "transparent"; border.width: parent.activeFocus ? 2 : 0 }
                }
            }
            Item { width: 1; height: 10 }
            Rectangle { width: parent.width; height: 1; color: bridge.border }
            Text { width: parent.width; text: "FOCUS  " + bridge.focused; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 12; wrapMode: Text.WordWrap }
        }
    }

    Item {
        id: content
        anchors.left: sidebar.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 28
        Column {
            width: parent.width
            spacing: 8
            Text { text: root.pageNames[root.pageIndex]; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 30; font.bold: true }
            Text { width: parent.width; text: ["Native-feeling interaction with Python callbacks and a polygon-aware star.", "Switch all shared colors at runtime; the orange button keeps its own fill.", "Start, stop and replay a repeatable scale pulse.", "Independent IDs, runtime changes and another top-level window.", "Try the physical mouse and Tab, Space, Enter. Current focus appears in the sidebar.", "Bundled synthetic media plus this computer’s current device list.", "Compare 50 and 400 animated items with a large image; judge responsiveness yourself.", "Runtime versions, graphics backend and initialization messages."][root.pageIndex]; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
        }
        Rectangle {
            id: bodyCard
            anchors.top: parent.top
            anchors.topMargin: 106
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: statusCard.top
            anchors.bottomMargin: 14
            radius: 20
            color: bridge.card
            border.color: bridge.border
            clip: true

            Flickable {
                id: scroll
                anchors.fill: parent
                anchors.margins: 25
                contentWidth: width
                contentHeight: pages.implicitHeight
                clip: true
                ScrollBar.vertical: ScrollBar { }
                Column {
                    id: pages
                    width: scroll.width
                    spacing: 0

                    Column {
                        visible: root.pageIndex === 0
                        width: parent.width
                        spacing: 18
                        Text { text: "Button states & shape hit testing"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Text { width: parent.width; text: "Hover, press, Tab-focus and activate. Click the star’s transparent corner: it should not fire."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                        Row { spacing: 14
                            ButtonControl { id: helloButton; objectName: "helloButton"; controlId: "hello"; text: "Say hello"; width: 190 }
                            ButtonControl { id: orangeButton; objectName: "orangeButton"; controlId: "orange"; text: "Independent orange"; overrideFill: "#ed8757"; width: 230 }
                        }
                        Rectangle { width: parent.width; height: 1; color: bridge.border }
                        Row { spacing: 24
                            StarControl { id: starControl; objectName: "starControl"; controlId: "star" }
                            Column { spacing: 8; width: 340
                                Text { text: "Star-shaped control"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 18; font.bold: true }
                                Text { width: parent.width; text: "Gradient, 2 px stroke, partial press opacity and shape-aware activation. Space or Enter activates it when focused."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                                Text { text: "Activations: " + (bridge.status.indexOf("star") >= 0 ? bridge.status : "see status below"); color: bridge.accent; font.family: "Segoe UI"; font.pixelSize: 12 }
                            }
                        }
                    }

                    Column {
                        visible: root.pageIndex === 1
                        width: parent.width
                        spacing: 18
                        Text { text: "Theme modes"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Row { spacing: 12
                            ButtonControl { controlId: "theme-light"; text: "Light"; width: 150; onClicked: bridge.setTheme("Light") }
                            ButtonControl { controlId: "theme-dark"; text: "Dark"; width: 150; onClicked: bridge.setTheme("Dark") }
                            ButtonControl { controlId: "theme-system"; text: "Follow system"; width: 180; onClicked: bridge.setTheme("System") }
                        }
                        Text { text: "Selected: " + bridge.themeMode; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 16 }
                        Rectangle { width: parent.width; height: 130; radius: 16; color: bridge.surface; border.color: bridge.border
                            Row { anchors.centerIn: parent; spacing: 16
                                Rectangle { width: 75; height: 75; radius: 16; color: bridge.accent }
                                Rectangle { width: 75; height: 75; radius: 16; color: bridge.star }
                                Rectangle { width: 75; height: 75; radius: 16; color: "#ed8757" }
                            }
                        }
                        Text { width: parent.width; text: "The orange fill is a per-control override. theme.tokens shows the small CSS-inspired token vocabulary; there is no selector or cascade engine."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                    }

                    Column {
                        visible: root.pageIndex === 2
                        width: parent.width
                        spacing: 18
                        Text { text: "Repeatable property animation"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Text { width: parent.width; text: "This rounded control loops a 900 ms scale pulse configured by Python. Stop it or replay from the beginning."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                        Item { width: parent.width; height: 155
                            ButtonControl { id: animatedButton; objectName: "animatedButton"; anchors.centerIn: parent; controlId: "animation"; text: "Animating control"; width: 235; animated: true; animationEnabled: bridge.animationRunning }
                        }
                        Row { spacing: 12
                            ButtonControl { controlId: "animation-toggle"; text: bridge.animationRunning ? "Stop" : "Start"; width: 140; onClicked: bridge.toggleAnimation() }
                            ButtonControl { controlId: "animation-replay"; text: "Replay"; width: 140; outlined: true; onClicked: bridge.replayAnimation() }
                        }
                        Text { text: "Current scale: " + animatedButton.scale.toFixed(3); color: bridge.accent; font.family: "Segoe UI"; font.pixelSize: 14 }
                    }

                    Column {
                        visible: root.pageIndex === 3
                        width: parent.width
                        spacing: 14
                        Text { text: "Independent controls"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Text { width: parent.width; text: "Every repeated button has a stable ID. Add one after launch, activate it, then remove the last one."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                        Flow { width: parent.width; spacing: 10
                            Repeater { id: dynamicRepeater; model: bridge.dynamicIds
                                delegate: ButtonControl { required property string modelData; width: 160; controlId: modelData; text: modelData }
                            }
                        }
                        Row { spacing: 12
                            ButtonControl { controlId: "dynamic-add"; text: "Add control"; width: 150; onClicked: bridge.addDynamic() }
                            ButtonControl { controlId: "dynamic-remove"; text: "Remove last"; width: 150; outlined: true; onClicked: bridge.removeDynamic() }
                        }
                        Rectangle { width: parent.width; height: 1; color: bridge.border }
                        ButtonControl { controlId: "second-window"; text: bridge.secondVisible ? "Close second window" : "Open second window"; width: 220; onClicked: bridge.toggleSecond() }
                    }

                    Column {
                        visible: root.pageIndex === 4
                        width: parent.width
                        spacing: 18
                        Text { text: "Physical input check"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Text { width: parent.width; text: "Use the mouse, then press Tab through these buttons and the star. Press Space or Enter on a focused control. The focus ring is amber."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                        Row { spacing: 12
                            ButtonControl { controlId: "input-a"; text: "Focus A"; width: 150 }
                            ButtonControl { controlId: "input-b"; text: "Focus B"; width: 150; outlined: true }
                            StarControl { controlId: "input-star" }
                        }
                        Text { text: "Focused control: " + bridge.focused; color: bridge.accent; font.family: "Segoe UI"; font.pixelSize: 17; font.bold: true }
                        Text { width: parent.width; text: "Touch: unverified on this machine unless you have touch hardware. Accessibility and screen reader behavior are outside this demo's verification."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                    }

                    Column {
                        visible: root.pageIndex === 5
                        width: parent.width
                        spacing: 13
                        Text { text: "Bundled synthetic media"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Row { spacing: 12
                            ButtonControl { controlId: "play-video"; text: "Play video"; width: 145; onClicked: { videoPlayer.stop(); videoPlayer.play(); bridge.mediaEvent("video play requested") } }
                            ButtonControl { controlId: "play-audio"; text: "Play tone"; width: 145; onClicked: { audioPlayer.stop(); audioPlayer.play(); bridge.mediaEvent("audio play requested") } }
                            ButtonControl { controlId: "stop-media"; text: "Stop both"; width: 145; outlined: true; onClicked: { videoPlayer.stop(); audioPlayer.stop(); bridge.mediaEvent("stopped") } }
                        }
                        Text { text: "Video: " + videoPlayer.playbackState + " / " + videoPlayer.mediaStatus + " · Audio: " + audioPlayer.playbackState + " / " + audioPlayer.mediaStatus; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 12 }
                        Rectangle { width: 480; height: 270; radius: 12; color: "#121827"; clip: true
                            VideoOutput { id: videoSurface; anchors.fill: parent; fillMode: VideoOutput.PreserveAspectFit }
                        }
                        Text { width: parent.width; text: bridge.devicesText; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 13; wrapMode: Text.WordWrap }
                        Text { width: parent.width; text: "Camera and microphone capture require hardware and permissions; this showcase enumerates devices but does not record from them."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 12; wrapMode: Text.WordWrap }
                    }

                    Column {
                        visible: root.pageIndex === 6
                        width: parent.width
                        spacing: 12
                        Text { text: "Visual load playground"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Row { spacing: 10
                            ButtonControl { controlId: "load-off"; text: "Off"; width: 110; outlined: true; onClicked: bridge.setLoad(0) }
                            ButtonControl { controlId: "load-50"; text: "50 items"; width: 130; onClicked: bridge.setLoad(50) }
                            ButtonControl { controlId: "load-400"; text: "400 items"; width: 140; onClicked: bridge.setLoad(400) }
                        }
                        Text { text: "Selected: " + bridge.particleCount + " animated elements"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 15; font.bold: true }
                        Rectangle { width: Math.min(parent.width, 690); height: 275; radius: 12; color: "#13223b"; clip: true
                            Image { anchors.fill: parent; source: bridge.particleCount ? bridge.imageUrl : ""; fillMode: Image.PreserveAspectCrop; opacity: 0.50; asynchronous: true }
                            Repeater { model: bridge.particleCount
                                delegate: Rectangle {
                                    required property int index
                                    width: 5 + (index % 5); height: width; radius: width / 2
                                    color: index % 3 === 0 ? "#ffd166" : (index % 3 === 1 ? "#7ce4d0" : "#b6a6ff")
                                    x: (index * 97) % 680; y: (index * 43) % 260
                                    NumberAnimation on x { from: (index * 97) % 680; to: ((index * 97) + 160) % 680; duration: 1200 + (index % 7) * 110; loops: Animation.Infinite; running: bridge.particleCount > 0 }
                                    NumberAnimation on y { from: (index * 43) % 260; to: ((index * 43) + 120) % 260; duration: 1350 + (index % 9) * 90; loops: Animation.Infinite; running: bridge.particleCount > 0 }
                                }
                            }
                        }
                        Text { width: parent.width; text: bridge.swapStats; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 13; wrapMode: Text.WordWrap }
                        Text { width: parent.width; text: "These are approximate frameSwapped callback intervals and process CPU observations, not monitor FPS. Results depend on this machine, this scene and other work running on the system."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 12; wrapMode: Text.WordWrap }
                    }

                    Column {
                        visible: root.pageIndex === 7
                        width: parent.width
                        spacing: 14
                        Text { text: "Environment & event log"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 21; font.bold: true }
                        Text { width: parent.width; text: "The log includes Python, PySide6, Qt, graphics backend, device/media errors and recent actions. For the concise author example, open example_app.py beside this demo."; color: bridge.muted; font.family: "Segoe UI"; font.pixelSize: 14; wrapMode: Text.WordWrap }
                        Rectangle { width: parent.width; height: 370; radius: 12; color: bridge.surface; border.color: bridge.border
                            Flickable { anchors.fill: parent; anchors.margins: 14; contentWidth: width; contentHeight: diagnosticText.implicitHeight; clip: true; ScrollBar.vertical: ScrollBar { }
                                Text { id: diagnosticText; width: parent.width; text: bridge.logText; color: bridge.ink; font.family: "Consolas"; font.pixelSize: 12; wrapMode: Text.WrapAnywhere }
                            }
                        }
                    }
                }
            }
        }
        Rectangle {
            id: statusCard
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 58
            radius: 15
            color: root.statusPillColor()
            Text { anchors.fill: parent; anchors.margins: 15; text: bridge.status; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 13; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
        }
    }

    MediaPlayer {
        id: videoPlayer
        source: bridge.videoUrl
        videoOutput: videoSurface
        audioOutput: AudioOutput { volume: 0.35 }
        onErrorOccurred: function(error, errorString) { bridge.mediaEvent("video error: " + errorString) }
        onMediaStatusChanged: if (mediaStatus === MediaPlayer.EndOfMedia) bridge.mediaEvent("video finished")
    }
    MediaPlayer {
        id: audioPlayer
        source: bridge.audioUrl
        audioOutput: AudioOutput { volume: 0.35 }
        onErrorOccurred: function(error, errorString) { bridge.mediaEvent("audio error: " + errorString) }
        onMediaStatusChanged: if (mediaStatus === MediaPlayer.EndOfMedia) bridge.mediaEvent("audio finished")
    }

    Window {
        id: secondWindow
        objectName: "secondWindow"
        width: 440; height: 280
        visible: bridge.secondVisible
        title: "Independent showcase window"
        color: bridge.surface
        onClosing: bridge.toggleSecond()
        Column { anchors.centerIn: parent; spacing: 18
            Text { text: "A second top-level window"; color: bridge.ink; font.family: "Segoe UI"; font.pixelSize: 20; font.bold: true }
            ButtonControl { controlId: "second-action"; text: "Independent action"; width: 220 }
        }
    }
}
