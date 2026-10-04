import QtQuick

// A transient overlay. Base style bindings never become animation targets.
Item {
    id: controller
    property var node
    property var owned: ({})
    property var group: null
    onNodeChanged: if (node) node.attachAnimations(controller)

    QtObject {
        id: animated
        property real opacity: 1
        property real scale: 1
        property real radius: 0
        property color background: "transparent"
        property color foreground: "transparent"
        property color panel: "transparent"
        property color accent: "transparent"
        property color accent_text: "transparent"
    }
    function value(name, base) {
        return owned[name] ? animated[name] : base
    }
    function release() {
        const old = group
        group = null
        owned = ({})
        if (old) {
            old.stop()
            old.destroy()
        }
    }
    function finish(serial) {
        release()
        node.animationFinished(serial)
    }
    function startPlayback(plan) {
        let next = null
        try {
            next = parallel.createObject(controller, {serial: plan.serial})
            if (!next) throw new Error("cannot create Qt Quick animation group")
            const names = ({})
            for (const track of plan.tracks) {
                const sequence = sequential.createObject(next)
                if (!sequence) throw new Error("cannot create Qt Quick animation track")
                next.animations.push(sequence)
                for (const segment of track.segments) {
                    const factory = track.color ? colorAnimation : numberAnimation
                    const animation = factory.createObject(sequence, {
                        target: animated, property: track.name, duration: segment.duration,
                        from: segment.start, to: segment.end
                    })
                    if (!animation) throw new Error("cannot create Qt Quick property animation")
                    animation.easing.type = easingType(segment.easing)
                    sequence.animations.push(animation)
                }
                if (track.hold > 0) {
                    const hold = pauseAnimation.createObject(sequence, {duration: track.hold})
                    if (!hold) throw new Error("cannot create Qt Quick hold")
                    sequence.animations.push(hold)
                }
                names[track.name] = true
            }
            // Commit only after every object was constructed. A failure leaves
            // the previous run and the base appearance intact.
            release()
            for (const track of plan.tracks) animated[track.name] = track.initial
            owned = names
            group = next
            node.animationReady(plan.serial, "")
            next.start()
        } catch (error) {
            if (next) next.destroy()
            node.animationReady(plan.serial, "Qt Quick playback: " + String(error))
        }
    }
    function easingType(name) {
        switch (name) {
        case "in_quad": return Easing.InQuad
        case "out_quad": return Easing.OutQuad
        case "in_out_quad": return Easing.InOutQuad
        default: return Easing.Linear
        }
    }
    Connections {
        target: controller.node || null
        function onAnimationRequested(plan) { controller.startPlayback(plan) }
        function onAnimationCancelled() { controller.release() }
    }
    Component {
        id: parallel
        ParallelAnimation {
            property int serial
            objectName: "animation-run"
            onFinished: controller.finish(serial)
        }
    }
    Component { id: sequential; SequentialAnimation {} }
    Component { id: numberAnimation; NumberAnimation {} }
    Component { id: colorAnimation; ColorAnimation {} }
    Component { id: pauseAnimation; PauseAnimation {} }
}
