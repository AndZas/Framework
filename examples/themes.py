"""Production theme studio, authored entirely in Python."""
from pathlib import Path
from pyui_framework import App, Button, Label, Row, Theme, ThemeError, Window

CUSTOM = Theme("Lagoon", background="#eaf5f2", foreground="#173b3a", panel="#eaf5f2",
               accent="#126e67", accent_text="#ffffff", radius=20, opacity=.94,
               gradient=("#126e67", "#65b8a3"))


def build(path=None):
    path = Path(path) if path is not None else Path(__file__).with_name("lagoon.theme")
    window = Window("Production themes · TASK-0010", width=800, height=760)
    app = App(window)
    status = Label("Ready. Light defaults; amber button has a local override.")
    local = Button("Local sample", on_click=lambda: status.set_text("Local sample clicked"),
                   style=dict(accent="#b36a17", accent_text="#ffffff", radius=24, gradient=None))

    def choose(theme, name):
        try:
            app.set_theme(theme)
            status.set_text(f"Active: {name}. Local overrides are preserved.")
        except ThemeError as exc:
            status.set_text(f"Unchanged appearance: {exc}")

    def load():
        try:
            choose(Theme.load(path), f"file {path.name}")
        except ThemeError as exc:
            status.set_text(f"Unchanged appearance: {exc}")

    def replace():
        local.set_style(accent="#874bb5", accent_text="#ffffff", radius=6, opacity=.8, gradient=None)
        status.set_text("Local sample replaced: violet, radius 6, opacity 0.8.")

    def clear():
        local.set_style()
        status.set_text("Local sample cleared: inheriting the active theme.")

    window.add(Label("Production theme studio", heading=True))
    window.add(Label("Switch appearance on existing controls. File and Python use the same Lagoon tokens. Resize and scroll with the wheel or the edge scrollbar."))
    window.add(Row(*(Button(name.title(), on_click=lambda choice=name: choose(choice, choice.title()))
                     for name in ("light", "dark", "system"))))
    window.add(Row(Button("Load / reload file", on_click=load),
                   Button("Python theme", on_click=lambda: choose(CUSTOM, "Python Lagoon"))))
    window.add(Label(f"Theme file: {path}\nEdit it, save, then reload. Pass another path to run-themes.cmd."))
    window.add(Button("Inherited sample", on_click=lambda: status.set_text("Inherited sample clicked")))
    window.add(local)
    window.add(Row(Button("Replace local style", on_click=replace), Button("Clear local style", on_click=clear)))
    window.add(status)
    window.add(Label("System follows Qt's available scheme. A real Windows Light/Dark transition still needs owner verification. Unknown reports an error and retains the last appearance."))
    return app


if __name__ == "__main__":
    import sys
    raise SystemExit(build(sys.argv[1] if len(sys.argv) > 1 else None).run())
