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
from pyui_framework.theme import _resolve


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
            intro.set_style(opacity=.65)
            check("base change does not rebase implicit starting point", run.running and item(intro).opacity() == .85)
            restarted = run.restart()
            check("restart replaces and creates new run", run.state == "replaced" and restarted.running and
                  item(intro).opacity() == .65)
            run.stop()
            check("stale handle cannot stop replacement", restarted.running)
            restarted.stop()
            restarted.stop()
            check("stop idempotent", restarted.state == "stopped" and item(intro).opacity() == .65)
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
            morph.set_style(gradient=("#223344", "#778899"))
            check("gradient base can change beneath active accent", run.running and background.property("gradient").isNull())
            run.stop()
            check("stop restores gradient binding", not background.property("gradient").isNull())
            gradient = background.property("gradient").toQObject()
            stops = sorted((stop.property("position"), stop.property("color").name())
                           for stop in gradient.children() if stop.metaObject().indexOfProperty("position") >= 0)
            check("stop restores latest actual gradient stops", stops == [(0., "#223344"), (1., "#778899")])
            run = morph.play(Timeline(Keyframe(0, radius=0), Keyframe(250, radius=20)))
            check("radius keeps gradient", not background.property("gradient").isNull())
            wait("radius completes with gradient restored", lambda: run.state == "completed")
            check("completion keeps gradient", not background.property("gradient").isNull())
            morph.set_style()
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

            # Each update changes owned numeric/color properties AND unowned
            # text color. Check current position synchronously, then progress,
            # latest-base restoration on BOTH finish and explicit stop.
            changing = Timeline(Keyframe(0, opacity=.25, radius=0, accent="#111111"),
                                Keyframe(1100, opacity=.8, radius=24, accent="#777777"))
            for update in ("theme", "replace", "clear"):
                for ending in ("finish", "stop"):
                    name = update + "/" + ending
                    app.set_theme("dark")
                    morph.set_style(**({} if update == "theme" else
                        dict(accent="#134466", accent_text="#eeeeee", radius=8, opacity=.95)))
                    independent = intro.play(example["INTRO"])
                    run = morph.play(changing)
                    wait(name + " reaches intermediate position", lambda: .35 < item(morph).opacity() < .6)
                    def position():
                        return (item(morph).opacity(), background.property("radius"), background.property("color").name())
                    before = position()
                    serial = node(morph)._active_serial
                    if update == "theme":
                        app.set_theme(Theme(accent="#874bb5", accent_text="#ffffff", radius=5, opacity=.9))
                    elif update == "replace":
                        morph.set_style(accent="#874bb5", accent_text="#ffffff", radius=4, opacity=.65)
                    else:
                        morph.set_style()
                    base = node(morph).appearance
                    check(name + " keeps run and current track position", run.running and
                          node(morph)._active is run and node(morph)._active_serial == serial and position() == before)
                    check(name + " updates unanimated text immediately",
                          item(morph).property("contentItem").property("color").name() == base["accent_text"])
                    check(name + " unrelated target still running", independent.running)
                    wait(name + " continues progressing", lambda: item(morph).opacity() > before[0] + .04)
                    if ending == "stop":
                        run.stop()
                        check(name + " explicit stop state", run.state == "stopped")
                    else:
                        wait(name + " normal completion", lambda: run.state == "completed")
                    check(name + " restores latest overlapping base", item(morph).opacity() == base["opacity"] and
                          background.property("radius") == base["radius"] and
                          background.property("color").name() == base["accent"])
                    check(name + " unrelated playback unaffected", independent.running)
                    independent.stop()

            app.set_theme("light")
            morph.set_style()
            run = morph.play(Timeline(Keyframe(0, opacity=.3), Keyframe(600, opacity=.8)))
            before = item(morph).opacity()
            morph.set_style(accent="#874bb5", radius=4)
            check("non-overlapping local tokens apply during opacity track", run.running and
                  item(morph).opacity() == before and background.property("color").name() == "#874bb5" and
                  background.property("radius") == 4)
            app.set_theme("dark")
            check("non-overlapping theme text applies with local precedence", run.running and
                  item(morph).property("contentItem").property("color").name() == app.resolved_theme["accent_text"] and
                  background.property("color").name() == "#874bb5")
            morph.set_style()
            check("non-overlapping clear updates fill immediately", run.running and
                  background.property("color").name() == app.resolved_theme["accent"])
            wait("non-overlapping updates permit completion", lambda: run.state == "completed")

            app.set_theme("system")
            run = morph.play(Timeline(Keyframe(0, accent="#000000"), Keyframe(1100, accent="#ffffff")))
            before = background.property("color").name()
            scheme = rt.hints.colorScheme()
            changed = Qt.ColorScheme.Light if scheme == Qt.ColorScheme.Dark else Qt.ColorScheme.Dark
            rt.hints.setColorScheme(changed)
            check("System scheme actually resolves new palette", app.resolved_theme ==
                  _resolve("light" if changed == Qt.ColorScheme.Light else "dark"))
            check("System notification preserves active color track", run.running and
                  background.property("color").name() == before)
            check("System updates unanimated text", item(morph).property("contentItem").property("color").name() ==
                  app.resolved_theme["accent_text"])
            with warnings.catch_warnings(record=True) as reported:
                warnings.simplefilter("always", RuntimeWarning)
                rt.system_changed(Qt.ColorScheme.Unknown)
            check("Unknown System retains palette and run", run.running and len(reported) == 1)
            run.stop()
            check("System stop restores newest palette color", background.property("color").name() == app.resolved_theme["accent"])
            app.set_theme("light")
            rt.hints.unsetColorScheme()
            # Appended controls and all advertised widget kinds use their own host.
            dynamic = app._window.add(Label("Dynamic animated Label"))
            QTest.qWait(50)
            run = dynamic.play(Timeline(Keyframe(0, foreground="#000000", panel="#ffffff", scale=.9, radius=0),
                                        Keyframe(400, foreground="#ffffff", panel="#000000", scale=1, radius=20)))
            check("dynamic host identity", item(dynamic).objectName() == node(dynamic).nodeId)
            wait("Label completion", lambda: run.state == "completed")
            check("Label restores style", item(dynamic).property("color").name() == app.resolved_theme["foreground"])
            run = dynamic.play(Timeline(Keyframe(0, foreground="#000000"), Keyframe(600, foreground="#ffffff")))
            dynamic.set_style(foreground="#123456", opacity=.7, panel="#eaf5f2")
            check("Label overlapping color track and unowned opacity", run.running and
                  item(dynamic).property("color").name() == "#000000" and item(dynamic).opacity() == .7)
            dynamic.set_style()
            app.set_theme("dark")
            check("Label clear/theme keeps color and updates opacity", run.running and
                  item(dynamic).opacity() == app.resolved_theme["opacity"])
            wait("Label completes into latest theme", lambda: run.state == "completed")
            check("Label latest foreground", item(dynamic).property("color").name() == app.resolved_theme["foreground"])
            window_run = app._window.play(Timeline(Keyframe(0, background="#000000", opacity=.9),
                                                  Keyframe(350, background="#ffffff", opacity=1)))
            wait("Window completion", lambda: window_run.state == "completed")
            check("Window restoration", rt.window.color().name() == app.resolved_theme["background"])
            window_run = app._window.play(Timeline(Keyframe(0, background="#000000"), Keyframe(600, background="#ffffff")))
            app.set_theme(Theme(background="#eaf5f2", opacity=.95))
            check("Window theme keeps background track and updates opacity", window_run.running and
                  rt.window.color().name() == "#000000" and rt.window.opacity() == .95)
            app._window.set_style(background="#123456", opacity=.9)
            check("Window local overlap/non-overlap", window_run.running and
                  rt.window.color().name() == "#000000" and rt.window.opacity() == .9)
            app._window.set_style()
            window_run.stop()
            check("Window clear then stop restores latest theme", rt.window.color().name() == "#eaf5f2" and
                  rt.window.opacity() == .95)
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

            # Every shipped preset must actually animate, replay and survive
            # theme/local replace/clear through its visible Python callbacks.
            check("six different named presets", len(example["PRESETS"]) >= 6)
            for name, caption, timeline, kind in example["PRESETS"]:
                target = next(n.value for n in rt.nodes if type(n.value) is kind and
                              getattr(n.value, "text", None) == caption)
                text = "Replay " + name
                for _ in range(8):
                    click(text)
                    check("repeated replay click " + text, node(target)._active is not None and node(target)._active.running)
                run = node(target)._active
                host = node(target)._animation_host
                initial = {track["name"]: host.value(track["name"], 0)
                           for track in timeline._plan(kind.__name__, node(target).appearance)["tracks"]}
                wait("preset progresses " + name, lambda: run.running and any(
                    host.value(prop, 0) != value for prop, value in initial.items()))
                click("Dark")
                check("demo theme keeps preset " + name, run.running and node(target)._active is run)
                click("Local purple")
                check("demo local replace keeps preset " + name, run.running and node(target)._active is run)
                click("Clear local")
                check("demo local clear keeps preset " + name, run.running and node(target)._active is run)
                click("Restart last")
                check("example Restart", node(target)._active is not None)
                click("Stop all")
                check("example Stop", node(target)._active is None)
                click("Light")
            for text in (intro.text, morph.text):
                click(text)
                check("sample itself replays " + text, node(button(text))._active is not None)
            QTest.qWait(400)
            capture("samples-active")
            click("Stop all")
            wait("all replaced/stopped objects destroyed", lambda: all(
                not n._animation_host.findChildren(QObject, "animation-run")
                for n in rt.nodes if n._animation_host is not None))
            click("Replay Color / corners")
            run = node(morph)._active
            other = intro.play(example["INTRO"])
            click("Dark")
            check("theme callback during two animations", run.running and other.running and app.theme == "dark")
            click("Local purple")
            check("style callback during two animations", run.running and other.running)
            capture("dark-local-active")
            click("Clear local")
            check("clear callback during two animations", run.running and other.running)
            click("Light")
            check("theme switch back keeps both animations", run.running and other.running)
            click("Stop all")
            other.stop()
            wait("Stop releases all sample runs", lambda: node(morph)._active is None)
            capture("restored")
            rt.window.setWidth(320)
            rt.window.setHeight(300)
            QTest.qWait(80)
            viewport = rt.window.findChild(QObject, "viewport")
            QTest.wheelEvent(rt.window, QPoint(30, 40), QPoint(0, -480))
            QTest.qWait(100)
            check("animation studio wheel scroll", viewport.property("contentY") > 0)
            click("Replay Fade / scale")
            check("resized replay remains responsive", node(intro)._active is not None)
            capture("narrow-active")
            click("Dark")
            click("Local purple")
            click("Clear local")
            check("resized theme/local controls preserve run", node(intro)._active is not None)
            rt.window.setWidth(800)
            rt.window.setHeight(820)
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
