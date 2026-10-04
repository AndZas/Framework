import subprocess
import sys
from pathlib import Path
import pytest
from pyui_framework import App, Button, Label, Theme, ThemeError, Window
from pyui_framework.theme import LIGHT, _resolve

ROOT = Path(__file__).resolve().parents[1]


def test_python_file_canonical_equivalence():
    import runpy
    python_theme = runpy.run_path(str(ROOT / "examples/themes.py"))["CUSTOM"]
    file_theme = Theme.load(ROOT / "examples/lagoon.theme")
    assert file_theme.tokens == python_theme.tokens
    assert _resolve(file_theme) == _resolve(python_theme)
    assert Theme(accent="#ABCDEF", radius=10).tokens == {"accent": "#abcdef", "radius": 10.0}
    assert Theme.parse(":theme { gradient: none; }").tokens == {"gradient": None}
    assert Theme.parse(":theme {}").tokens == {}
    assert Theme.parse(":theme {\n gradient: linear-gradient(\n #123456,\n #ABCDEF\n );\n}").tokens == {"gradient": ("#123456", "#abcdef")}
    assert _resolve(Theme(accent="#123456")) == LIGHT.tokens | {"accent": "#123456"}


@pytest.mark.parametrize("text, fragment", [
    ("Label { accent: #123456; }", "block"),
    (":theme {} :theme {}", "block"),
    (":theme { /* no comments */ }", "semicolon"),
    (":theme { accent: #123456 }", "semicolon"),
    (":theme { accent: #123456;; }", "malformed"),
    (":theme { missing: #123456; }", "unknown"),
    (":theme { accent: #123456; accent: #234567; }", "duplicate"),
    (":theme { radius: 4px; }", "decimal"),
    (":theme { radius: -1; }", "decimal"),
    (":theme { radius: 49; }", "0..48"),
    (":theme { opacity: 1.01; }", "0..1"),
    (":theme { opacity: true; }", "decimal"),
    (":theme { foreground: red; }", "#RRGGBB"),
    (":theme { gradient: linear-gradient(90deg, #123456, #234567); }", "gradient"),
    (":theme { gradient: linear-gradient(#123456, #234567, #345678); }", "gradient"),
    (":theme { accent_text: #ffffff; }", "malformed"),
])
def test_invalid_files(text, fragment):
    with pytest.raises(ThemeError, match=fragment):
        Theme.parse(text, source="bad.theme")


@pytest.mark.parametrize("tokens", [
    dict(missing=1), dict(radius=True), dict(radius="2"), dict(radius=-.1),
    dict(radius=48.01), dict(radius=10**1000), dict(opacity=float("nan")),
    dict(opacity=float("inf")), dict(opacity=-1), dict(opacity=None),
    dict(accent=123), dict(accent="#123"), dict(gradient="none"),
    dict(gradient=("#123456",)), dict(gradient=("#123456", "no")),
])
def test_invalid_python(tokens):
    with pytest.raises(ThemeError):
        Theme(**tokens)


def test_diagnostics_and_file_errors(tmp_path):
    with pytest.raises(ThemeError, match=r"custom.theme:3: radius"):
        Theme.parse(":theme {\n accent: #123456;\n radius: 99;\n}", source="custom.theme")
    with pytest.raises(ThemeError, match="missing.theme: cannot read"):
        Theme.load(tmp_path / "missing.theme")
    path = tmp_path / "bad.theme"
    path.write_bytes(b"\xff")
    with pytest.raises(ThemeError, match="cannot read"):
        Theme.load(path)
    path.write_text("\ufeff:theme { opacity: 0; radius: 48; }", encoding="utf-8")
    assert Theme.load(path).tokens == dict(opacity=0., radius=48.)


def test_defensive_copies_precedence_and_atomic_model_updates():
    gradient = ["#123456", "#abcdef"]
    theme = Theme(gradient=gradient)
    gradient[0] = "bad"
    theme.tokens["opacity"] = 0
    assert theme.tokens == {"gradient": ("#123456", "#abcdef")}
    local = dict(accent="#ABCDEF", gradient=None)
    button = Button("local", on_click=lambda: None, style=local)
    local["accent"] = "bad"
    assert button.style == dict(accent="#abcdef", gradient=None)
    app = App(Window("test", button), theme="dark")
    app.resolved_theme["accent"] = "bad"
    assert (app.resolved_theme | button.style)["accent"] == "#abcdef"
    for bad in ("Dark", {}, None, 3):
        with pytest.raises(ThemeError):
            app.set_theme(bad)
        assert app.theme == "dark"
    before = button.style
    with pytest.raises(ThemeError):
        button.set_style(accent="#123456", opacity=2)
    assert button.style == before
    button.set_style(radius=0)
    assert button.style == {"radius": 0.}
    button.set_style()
    assert button.style == {}
    app.set_theme(Theme(foreground="#123456"))
    assert app.resolved_theme["accent"] == LIGHT.tokens["accent"]
    with pytest.raises(ThemeError, match="Label style"):
        Label("bad", style=dict(accent="#123456"))
    with pytest.raises(ThemeError):
        Window("bad", style=False)
    with pytest.raises(ThemeError):
        Theme(name="")
    assert _resolve("system", "dark") == _resolve("dark")
    with pytest.raises(ThemeError, match="Unknown"):
        _resolve("system")


@pytest.mark.parametrize("example", ["ordinary", "studio"])
def test_live_theme_example(example, tmp_path):
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("theme_probe.py")),
                             "--app", example, "--output", str(tmp_path)],
                            capture_output=True, text=True, timeout=50)
    assert result.returncode == 0, result.stdout + result.stderr


def test_owner_review_rendering(tmp_path):
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("theme_review_probe.py")), str(tmp_path)],
                            capture_output=True, text=True, timeout=50)
    assert result.returncode == 0, result.stdout + result.stderr
