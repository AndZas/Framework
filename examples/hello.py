"""Python-only experimental framework example."""
from pyui_framework import App, Button, Column, Label, Row, Window


def build():
    window = Window("Python UI — first core slice")
    status = Label("Ready. Each action has its own counter.")
    counts = {"save": 0, "reset": 0, "added": 0}

    def record(action):
        counts[action] += 1
        status.set_text(" · ".join(f"{key}: {value}" for key, value in counts.items()))

    window.add(Label("A small Python UI", heading=True))
    window.add(Label("This window is authored entirely in Python. Resize it to see the text wrap and the horizontal actions share the available width."))
    window.add(Row(Button("Save", on_click=lambda: record("save")),
                   Button("Reset", on_click=lambda: record("reset"))))
    body = window.add(Column(status))
    added = False

    def append():
        nonlocal added
        if not added:
            body.add(Button("Added after startup", on_click=lambda: record("added")))
            added = True

    window.add(Button("Add a live action", on_click=append))
    return window


if __name__ == "__main__":
    raise SystemExit(App(build()).run())
