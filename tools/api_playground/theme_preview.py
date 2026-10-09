"""Small theme sample launched by the Playground's managed child runner."""
from pathlib import Path
import sys

from pyui_framework import App, Button, Label, Row, Theme, Window


def build(path):
    path = Path(path).resolve()
    theme = Theme.load(path)
    status = Label("Ready. Activate either sample button to check interaction.")
    clicks = 0

    def clicked():
        nonlocal clicks
        clicks += 1
        status.set_text(f"Sample clicked {clicks} time(s). Controls remain usable.")
        print(f"Theme sample clicked {clicks} time(s).", flush=True)

    window = Window(
        f"Theme preview — {path.name}",
        Label("Theme preview", heading=True),
        Label(f"File: {path}\nWindow background and opacity come from this saved theme."),
        Label("Labels show foreground, panel, radius and opacity. Buttons show accent text, radius and opacity."),
        Row(Button("Theme gradient", on_click=clicked),
            Button("Solid accent", on_click=clicked, style={"gradient": None})),
        status,
        Label("Save edits in the Theme tab and preview again to restart. Opacity below 1 affects the whole window and each control."),
        width=760, height=560,
    )
    return App(window, theme=theme)


if __name__ == "__main__":
    raise SystemExit(build(sys.argv[1]).run())
