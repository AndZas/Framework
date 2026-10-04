"""Python-only keyframe studio. Launch with run-animations.cmd on Windows."""
from pyui_framework import App, Button, Keyframe, Label, Row, Timeline, Window


INTRO = Timeline(
    Keyframe(0, opacity=.25, scale=.86),
    Keyframe(450, opacity=1, scale=1, easing="out_quad"),
    Keyframe(900, opacity=.65, scale=.94, easing="in_out_quad"),
    Keyframe(1400, opacity=1, scale=1, easing="out_quad"),
)
MORPH = Timeline(
    Keyframe(0, radius=0, accent="#365a94", accent_text="#ffffff"),
    Keyframe(700, radius=24, accent="#9b4296", easing="in_out_quad"),
    Keyframe(1400, radius=6, accent="#126e67", easing="in_out_quad"),
    Keyframe(2100, radius=24, accent="#b36a17", easing="in_out_quad"),
)


def build():
    status = Label("Click a sample or Replay. Theme/style changes stop animations and restore their base.")
    runs = {}
    counts = {"intro": 0, "morph": 0}

    def replay(name, target, timeline):
        runs[name] = target.play(timeline)
        counts[name] += 1
        status.set_text(f"Replay counts — fade/scale: {counts['intro']}; color/corners: {counts['morph']}. "
                        "Completion and Stop restore the base style.")

    intro = Button("Fade + scale — click to replay", on_click=lambda: replay("intro", intro, INTRO))
    morph = Button("Color + corners — click to replay", on_click=lambda: replay("morph", morph, MORPH))

    def stop():
        for run in runs.values():
            run.stop()
        status.set_text("Stopped. Base appearance restored; Replay starts again from time zero.")

    def restart():
        for name, run in list(runs.items()):
            runs[name] = run.restart()
        status.set_text("Restarted existing descriptions from their deterministic starting values.")

    def theme(choice):
        app.set_theme(choice)
        status.set_text(f"Theme: {choice}. Active runs stopped; local overrides retained.")

    def local(enabled):
        morph.set_style(**(dict(accent="#874bb5", radius=4, gradient=None) if enabled else {}))
        status.set_text("Color/corners animation stopped; local style replaced/cleared. Replay to compare.")

    window = Window("Keyframe animations — Python + Qt Quick",
                    Label("Keyframe animations", heading=True),
                    Label("Qt Quick animates existing Python widgets. Replay repeatedly, resize, "
                          "or switch themes while a sample is moving."),
                    intro,
                    Button("Replay fade / scale", on_click=lambda: replay("intro", intro, INTRO)),
                    morph,
                    Button("Replay color / corners", on_click=lambda: replay("morph", morph, MORPH)),
                    Row(Button("Stop all", on_click=stop), Button("Restart last", on_click=restart)),
                    Row(*(Button(choice.title(), on_click=lambda c=choice: theme(c))
                          for choice in ("light", "dark", "system"))),
                    Row(Button("Local purple", on_click=lambda: local(True)),
                        Button("Clear local", on_click=lambda: local(False))),
                    status, width=760, height=720)
    app = App(window)
    return app


if __name__ == "__main__":
    raise SystemExit(build().run())
