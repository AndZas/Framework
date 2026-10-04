"""Six Python-only keyframe presets. Launch with run-animations.cmd on Windows."""
from pyui_framework import App, Button, Keyframe, Label, Row, Timeline, Window


INTRO = Timeline(
    Keyframe(0, opacity=.25, scale=.86),
    Keyframe(900, opacity=1, scale=1, easing="out_quad"),
    Keyframe(2100, opacity=.5, scale=.9, easing="in_out_quad"),
    Keyframe(3500, opacity=1, scale=1, easing="out_quad"),
)
MORPH = Timeline(
    Keyframe(0, radius=0, accent="#365a94", accent_text="#ffffff"),
    Keyframe(1400, radius=24, accent="#9b4296", easing="in_out_quad"),
    Keyframe(2800, radius=6, accent="#126e67", easing="in_out_quad"),
    Keyframe(4200, radius=24, accent="#b36a17", easing="in_out_quad"),
)
FADE = Timeline(Keyframe(0, opacity=1), Keyframe(1500, opacity=.15, easing="in_quad"),
                Keyframe(3000, opacity=1, easing="out_quad"))
PULSE = Timeline(Keyframe(0, scale=1), Keyframe(900, scale=.65, easing="in_out_quad"),
                 Keyframe(1800, scale=1, easing="out_quad"), Keyframe(2700, scale=.8),
                 Keyframe(3600, scale=1, easing="out_quad"))
CORNERS = Timeline(Keyframe(0, radius=0), Keyframe(1800, radius=24, easing="in_out_quad"),
                   Keyframe(4000, radius=0, easing="in_out_quad"))
INK = Timeline(Keyframe(0, foreground="#ffffff", panel="#365a94"),
               Keyframe(2000, foreground="#173b3a", panel="#b9e3d6", easing="in_out_quad"),
               Keyframe(4000, foreground="#ffffff", panel="#874bb5", easing="in_out_quad"))

# Preset name, sample caption, descriptor, widget kind. Durations allow time
# to change theme or local style; each preset demonstrates a different effect.
PRESETS = (
    ("Fade / scale", "Fade + scale — click to replay", INTRO, Button),
    ("Color / corners", "Color + corners — click to replay", MORPH, Button),
    ("Fade only", "Fade only — opacity", FADE, Button),
    ("Scale pulse", "Scale pulse — size without relayout", PULSE, Button),
    ("Corner sweep", "Corner sweep — square to round", CORNERS, Button),
    ("Text / panel", "Text / panel — paired color transitions", INK, Label),
)


def build():
    status = Label("Choose a preset. Theme/local updates keep tracks running; Stop/finish restores the latest base.")
    runs, samples, counts = {}, {}, {}

    def replay(name, timeline):
        runs[name] = samples[name].play(timeline)
        counts[name] = counts.get(name, 0) + 1
        status.set_text(f"{name}: replay {counts[name]}. Tracks continue through theme/local changes.")

    rows = []
    for name, caption, timeline, kind in PRESETS:
        sample = (Button(caption, on_click=lambda n=name, t=timeline: replay(n, t))
                  if kind is Button else Label(caption))
        samples[name] = sample
        rows.append(Row(sample, Button("Replay " + name, on_click=lambda n=name, t=timeline: replay(n, t))))

    def stop():
        for run in runs.values():
            run.stop()
        status.set_text("Stopped. Samples restored to the latest theme and local styles.")

    def restart():
        for name, run in list(runs.items()):
            runs[name] = run.restart()
        status.set_text("Restarted last runs from zero using their current base appearance.")

    def theme(choice):
        app.set_theme(choice)
        status.set_text(f"Theme: {choice}. Tracks keep running; other properties update immediately.")

    def local(enabled):
        for sample in samples.values():
            tokens = (dict(accent="#874bb5", accent_text="#ffffff", radius=4, gradient=None) if isinstance(sample, Button)
                      else dict(panel="#874bb5", foreground="#ffffff", radius=4))
            sample.set_style(**(tokens if enabled else {}))
        status.set_text("Local purple applied to all samples." if enabled else "Local styles cleared on all samples.")

    window = Window("Keyframe animations — Python + Qt Quick",
                    Label("Six keyframe presets", heading=True),
                    Label("Samples on the left; Replay on the right. Run several together, then switch "
                          "theme or local style. Tracks continue until Stop or finish."),
                    Row(*(Button(choice.title(), on_click=lambda c=choice: theme(c))
                          for choice in ("light", "dark", "system"))),
                    Row(Button("Local purple", on_click=lambda: local(True)),
                        Button("Clear local", on_click=lambda: local(False))),
                    Row(Button("Stop all", on_click=stop), Button("Restart last", on_click=restart)),
                    status, *rows, width=800, height=820)
    app = App(window)
    return app


if __name__ == "__main__":
    raise SystemExit(build().run())
