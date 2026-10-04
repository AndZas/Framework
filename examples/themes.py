"""Production theme studio, authored entirely in Python."""
from pathlib import Path
from pyui_framework import App, Button, Label, Row, Theme, ThemeError, Window

CUSTOM = Theme("Lagoon", background="#eaf5f2", foreground="#173b3a", panel="#eaf5f2",
               accent="#126e67", accent_text="#ffffff", radius=20, opacity=1,
               gradient=("#126e67", "#65b8a3"))
MIDNIGHT = Theme("Midnight", background="#171827", foreground="#eeedf8", panel="#24263a",
                 accent="#bba6f5", accent_text="#211a34", radius=20, opacity=1,
                 gradient=("#55377e", "#285b78"))


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
            status.set_text(f"Active: {name}. Theme opacity: {app.resolved_theme['opacity']:g} (whole window and widgets). Local overrides are preserved.")
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

    def window_opacity(value):
        window.set_style(opacity=value)
        status.set_text(f"Window-only opacity override: {value:g}. Values below 1 reveal the desktop behind the whole window.")

    def clear_window_opacity():
        window.set_style()
        status.set_text("Window opacity inherits the active theme again.")

    window.add(Label("Production theme studio", heading=True))
    window.add(Label("Switch appearance on existing controls. File and Python Lagoon use the same opaque tokens. Load Midnight via the file path to compare with Python Midnight."))
    window.add(Row(*(Button(name.title(), on_click=lambda choice=name: choose(choice, choice.title()))
                     for name in ("light", "dark", "system"))))
    window.add(Row(Button("Load / reload file", on_click=load),
                   Button("Python theme", on_click=lambda: choose(CUSTOM, "Python Lagoon")),
                   Button("Python Midnight", on_click=lambda: choose(MIDNIGHT, "Python Midnight"))))
    window.add(Label(f"Theme file: {path}\nEdit it, save, then reload. Pass another path to run-themes.cmd."))
    window.add(Button("Inherited sample", on_click=lambda: status.set_text("Inherited sample clicked")))
    window.add(local)
    window.add(Row(Button("Replace local style", on_click=replace), Button("Clear local style", on_click=clear)))
    window.add(status)
    window.add(Label("Theme opacity applies to the whole window and each Label/Button; values below 1 can reveal the desktop and also soften controls. Lagoon ships at 1. These buttons override only window opacity; reloading a theme preserves that local override."))
    window.add(Row(Button("Window opacity 0.94", on_click=lambda: window_opacity(.94)),
                   Button("Window opacity 1.0", on_click=lambda: window_opacity(1))))
    window.add(Button("Clear window opacity", on_click=clear_window_opacity))
    window.add(Label("System follows Qt's available scheme. The owner verified a Windows Light/Dark transition on this setup. Unknown reports an error and retains the last appearance."))
    return app


if __name__ == "__main__":
    import sys
    raise SystemExit(build(sys.argv[1] if len(sys.argv) > 1 else None).run())
