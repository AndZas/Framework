"""Visible Windows Qt Quick evidence. All input here is synthetic QtTest."""
import json
import platform
import runpy
import sys
import traceback
import time
import warnings
from pathlib import Path
from threading import Thread
from unittest.mock import patch

import PySide6
import shiboken6
from PySide6.QtCore import QObject, QPoint, QPointF, Qt, QTimer, qInstallMessageHandler, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
from pyui_framework import AnimationError, Button, Keyframe, Label, Theme, ThemeError, Timeline


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    messages = []
    previous = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
    qt_app = QGuiApplication([])
    example = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/animations.py"))
    app = example["build"]()
    evidence = dict(environment=dict(platform=platform.platform(), python=sys.version,
                                     PySide6=PySide6.__version__, Qt=qVersion()),
                    input="synthetic QtTest; physical input unverified", checks=[], failures=[])
    retained = []

    def check(name, condition):
        evidence["checks"].append(name)
        assert condition, name

    def wait(name, predicate, timeout=5000):
        deadline = time.monotonic() + timeout/1000
        while not predicate() and time.monotonic() < deadline:
            QTest.qWait(20)
        check(name, predicate())

    def exercise():
        rt = app._runtime
        retained.append(rt)
        evidence["environment"].update(graphics_api=rt.quick.rendererInterface().graphicsApi().name,
                                       window_dpr=rt.window.devicePixelRatio())

        def node(widget):
            return next(n for n in rt.nodes if n.value is widget)

        def item(widget):
            name = node(widget).nodeId
            def find(parent):
                if parent.objectName() == name:
                    return parent
                for child in parent.childItems():
                    result = find(child)
                    if result is not None:
                        return result
            return find(rt.quick.contentItem())

        def button(text):
            return next(n.value for n in rt.nodes if isinstance(n.value, Button) and n.value.text == text)

        def click(text):
            visual = item(button(text))
            viewport = rt.window.findChild(QObject, "viewport")
            p = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
            viewport.setProperty("contentY", max(0, viewport.property("contentY") + p.y() - rt.window.height()/2))
            QTest.qWait(35)
            p = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
            QTest.mouseClick(rt.window, Qt.MouseButton.LeftButton, pos=QPoint(round(p.x()), round(p.y())))

        def capture(name):
            check("capture " + name, rt.quick.grabWindow().save(str(output / (name + ".png"))))

        try:
            intro = button("Fade + scale — click to replay")
            morph = button("Color + corners — click to replay")
            label = next(n.value for n in rt.nodes if isinstance(n.value, Label))
            check("visible window", rt.window.isVisible())
            capture("base")
            linear = Timeline(Keyframe(0, opacity=.2, scale=.5, accent="#000000", radius=0),
                              Keyframe(2000, opacity=.8, scale=1, accent="#ffffff", radius=40),
                              Keyframe(2600, opacity=.8))
            run = morph.play(linear)
            check("deterministic t0", run.running and item(morph).opacity() == .2 and item(morph).scale() == .5)
            wait("numeric interpolation", lambda: .35 < item(morph).opacity() < .65)
            opacity = item(morph).opacity()
            fraction = (opacity-.2)/.6
            check("parallel linear scale interpolation", abs(item(morph).scale()-(.5+.5*fraction)) < .015)
            background = item(morph).property("background")
            check("linear radius interpolation", abs(background.property("radius")-40*fraction) < 1)
            color = background.property("color")
            check("Qt ColorAnimation interpolation", abs(color.redF()-fraction) < .025 and
                  abs(color.greenF()-fraction) < .025 and abs(color.blueF()-fraction) < .025)
            evidence["interpolation_sample"] = dict(opacity=opacity, scale=item(morph).scale(),
                radius=background.property("radius"), color=color.name())
            capture("interpolation")
            wait("sparse track holds final value", lambda: run.running and item(morph).opacity() == .8)
            check("scale and radius held", item(morph).scale() == 1 and background.property("radius") == 40)
            wait("completion state", lambda: run.state == "completed")
            check("completion restores base bindings", item(morph).opacity() == 1 and item(morph).scale() == 1 and
                  background.property("radius") == app.resolved_theme["radius"] and
                  background.property("color").name() == app.resolved_theme["accent"])
            wait("completed objects destroyed", lambda: not node(morph)._animation_host.findChildren(QObject, "animation-run"))

            # Relate simultaneous easing tracks to one linear track, independent
            # of frame rate and without asserting a narrow wall-clock deadline.
            for easing in ("in_quad", "out_quad", "in_out_quad"):
                eased = Timeline(Keyframe(0, opacity=0, scale=0), Keyframe(1800, opacity=1),
                                 Keyframe(1801, scale=1, easing=easing))
                run = intro.play(eased)
                wait("easing sample " + easing, lambda: .3 < item(intro).opacity() < .65)
                x = item(intro).opacity() * 1800/1801
                expected = x*x if easing == "in_quad" else 1-(1-x)**2 if easing == "out_quad" else (
                    2*x*x if x < .5 else 1-2*(1-x)**2)
                check("Qt easing " + easing, abs(item(intro).scale()-expected) < .025)
                run.stop()
                check("stop restores and marks stopped", run.state == "stopped" and item(intro).opacity() == 1)

            timeline = Timeline(Keyframe(200, opacity=.4), Keyframe(900, opacity=.7))
            intro.set_style(opacity=.85)
            run = intro.play(timeline)
            check("implicit zero snapshots local style", item(intro).opacity() == .85)
            restarted = run.restart()
            check("restart replaces and creates new run", run.state == "replaced" and restarted.running and
                  item(intro).opacity() == .85)
            run.stop()
            check("stale handle cannot stop replacement", restarted.running)
            restarted.stop()
            restarted.stop()
            check("stop idempotent", restarted.state == "stopped" and item(intro).opacity() == .85)
            intro.set_style()

            for bad in (None, Timeline(Keyframe(0, background="#000000"), Keyframe(10, background="#ffffff"))):
                run = intro.play(example["INTRO"])
                try:
                    intro.play(bad)
                    raise AssertionError("invalid target descriptor accepted")
                except AnimationError as exc:
                    evidence.setdefault("invalid_inputs", []).append(str(exc))
                check("invalid play preserves active run", run.running)
                run.stop()

            run = intro.play(Timeline(Keyframe(0, opacity=.4), Keyframe(250, opacity=1)))
            node(intro).blockSignals(True)
            try:
                try:
                    intro.play(example["INTRO"])
                    raise AssertionError("unacknowledged play accepted")
                except AnimationError as exc:
                    check("playback failure diagnostic", "acknowledge" in str(exc))
            finally:
                node(intro).blockSignals(False)
            check("failed playback preserves original", run.running)
            wait("original completes after failed playback", lambda: run.state == "completed")

            run = intro.play(example["INTRO"])
            with patch.object(Timeline, "_plan", return_value=dict(tracks=None)):
                try:
                    intro.play(example["INTRO"])
                    raise AssertionError("internal Qt Quick preparation failure accepted")
                except AnimationError as exc:
                    check("Qt Quick preparation failure reported", "Qt Quick playback" in str(exc))
            check("Qt Quick preparation failure preserves active run", run.running)
            run.stop()

            first = intro.play(example["INTRO"])
            replacement = intro.play(Timeline(Keyframe(0, radius=0), Keyframe(800, radius=20)))
            check("disjoint replacement resets old properties", first.state == "replaced" and
                  item(intro).opacity() == 1 and item(intro).scale() == 1)
            replacement.stop()

            app.set_theme(Theme(gradient=("#126e67", "#65b8a3")))
            check("base gradient present", not background.property("gradient").isNull())
            run = morph.play(example["MORPH"])
            check("accent temporarily disables gradient", background.property("gradient").isNull())
            run.stop()
            check("stop restores gradient binding", not background.property("gradient").isNull())
            run = morph.play(Timeline(Keyframe(0, radius=0), Keyframe(250, radius=20)))
            check("radius keeps gradient", not background.property("gradient").isNull())
            wait("radius completes with gradient restored", lambda: run.state == "completed")
            check("completion keeps gradient", not background.property("gradient").isNull())
            app.set_theme("light")

            for operation in (lambda: intro.set_style(opacity=2), lambda: app.set_theme("bad")):
                run = intro.play(example["INTRO"])
                try:
                    operation()
                    raise AssertionError("invalid style/theme accepted")
                except ThemeError:
                    pass
                check("invalid style/theme preserves run", run.running)
                run.stop()

            run = morph.play(example["MORPH"])
            morph.set_style(accent="#874bb5", radius=4)
            check("local update stops and applies", run.state == "style_changed" and
                  background.property("color").name() == "#874bb5" and background.property("radius") == 4)
            run = morph.play(example["MORPH"])
            app.set_theme("dark")
            check("theme update stops and keeps local", run.state == "theme_changed" and
                  background.property("color").name() == "#874bb5" and morph.style["radius"] == 4)
            run = morph.play(example["MORPH"])
            morph.set_style()
            check("clear style stops and restores latest theme", run.state == "style_changed" and
                  background.property("color").name() == app.resolved_theme["accent"])
            independent = intro.play(example["INTRO"])
            morph.set_style(radius=3)
            check("other widget style leaves run active", independent.running)
            independent.stop()
            morph.set_style()

            app.set_theme("system")
            run = intro.play(example["INTRO"])
            scheme = rt.hints.colorScheme()
            changed = Qt.ColorScheme.Light if scheme == Qt.ColorScheme.Dark else Qt.ColorScheme.Dark
            rt.hints.setColorScheme(changed)
            wait("System notification cancels active run", lambda: run.state == "theme_changed")
            run = intro.play(example["INTRO"])
            with warnings.catch_warnings(record=True) as reported:
                warnings.simplefilter("always", RuntimeWarning)
                rt.system_changed(Qt.ColorScheme.Unknown)
            check("Unknown System retains palette and run", run.running and len(reported) == 1)
            run.stop()
            app.set_theme("light")
            rt.hints.unsetColorScheme()
            # Appended controls and all advertised widget kinds use their own host.
            dynamic = app._window.add(Label("Dynamic animated Label", style=dict(panel="#000000")))
            QTest.qWait(50)
            run = dynamic.play(Timeline(Keyframe(0, foreground="#000000", panel="#ffffff", scale=.9, radius=0),
                                        Keyframe(400, foreground="#ffffff", panel="#000000", scale=1, radius=20)))
            check("dynamic host identity", item(dynamic).objectName() == node(dynamic).nodeId)
            wait("Label completion", lambda: run.state == "completed")
            check("Label restores style", item(dynamic).property("color").name() == app.resolved_theme["foreground"])
            window_run = app._window.play(Timeline(Keyframe(0, background="#000000", opacity=.9),
                                                  Keyframe(350, background="#ffffff", opacity=1)))
            wait("Window completion", lambda: window_run.state == "completed")
            check("Window restoration", rt.window.color().name() == app.resolved_theme["background"])
            app.set_theme("light")

            errors = []
            run = intro.play(example["INTRO"])
            def worker():
                for operation in (lambda: intro.play(example["INTRO"]), run.stop, run.restart):
                    try:
                        operation()
                    except RuntimeError as exc:
                        errors.append(str(exc))
            thread = Thread(target=worker)
            thread.start()
            thread.join()
            check("worker controls rejected without mutation", len(errors) == 3 and run.running)
            run.stop()

            # Exercise real Python example callbacks via actual Qt mouse events.
            for text, target in (("Replay fade / scale", intro), ("Replay color / corners", morph)):
                for _ in range(8):
                    click(text)
                    check("repeated replay click " + text, node(target)._active is not None and node(target)._active.running)
                click("Restart last")
                check("example Restart", node(target)._active is not None)
                click("Stop all")
                check("example Stop", node(target)._active is None)
            for text in (intro.text, morph.text):
                click(text)
                check("sample itself replays " + text, node(button(text))._active is not None)
            QTest.qWait(400)
            capture("samples-active")
            click("Stop all")
            wait("all replaced/stopped objects destroyed", lambda: all(
                not n._animation_host.findChildren(QObject, "animation-run")
                for n in rt.nodes if n._animation_host is not None))
            click("Replay color / corners")
            run = node(morph)._active
            click("Dark")
            check("theme callback during animation", run.state == "theme_changed" and app.theme == "dark")
            click("Replay color / corners")
            run = node(morph)._active
            click("Local purple")
            check("style callback during animation", run.state == "style_changed")
            click("Clear local")
            click("Light")
            capture("restored")
            rt.window.setWidth(320)
            rt.window.setHeight(300)
            QTest.qWait(80)
            click("Replay fade / scale")
            check("resized replay remains responsive", node(intro)._active is not None)
            capture("narrow-active")
            rt.window.setWidth(760)
            rt.window.setHeight(720)
            QTest.qWait(50)
            final_runs = [intro.play(example["INTRO"]), morph.play(example["MORPH"]),
                          dynamic.play(Timeline(Keyframe(0, opacity=.2), Keyframe(900, opacity=1)))]
            hosts = [node(value)._animation_host for value in (intro, morph, dynamic)]
            rt.window.close()
            check("native close immediately cancels active runs", all(run.state == "closed" for run in final_runs))
            try:
                final_runs[0].restart()
                raise AssertionError("closed target restart accepted")
            except AnimationError:
                pass
            check("closed playback rejects restart", node(intro)._active is None)
            retained.extend([final_runs, hosts, intro, morph, dynamic])
        except Exception:
            evidence["failures"].append(traceback.format_exc())
        finally:
            qt_app.quit()

    QTimer.singleShot(250, exercise)
    result = app.run()
    rt = retained[0]
    if rt.errors:
        evidence["failures"].append("Runtime errors: " + repr(rt.errors))
    else:
        check("runtime errors empty", True)
    check("runtime nodes released", not rt.nodes)
    if len(retained) > 1:
        check("QML hosts destroyed on shutdown", all(not shiboken6.isValid(host) for host in retained[2]))
        check("public targets detached", all(widget._runtime is None for widget in retained[3:]))
        for handle in retained[1]:
            handle.stop()
            try:
                handle.restart()
                raise AssertionError("detached target restarted")
            except AnimationError:
                pass
        check("detached controls safe", True)
    evidence["qml_errors"] = rt.errors
    evidence["qt_messages"] = messages
    if messages:
        evidence["failures"].append("Qt messages: " + repr(messages))
    else:
        check("Qt messages empty", True)
    qInstallMessageHandler(previous)
    (output / "probe.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 1 if evidence["failures"] else result


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
