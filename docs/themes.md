# Experimental production themes

The 0.x Python API implements ADR-0003 on the existing PySide6/Qt Quick runtime.
Application authors do not write QML. Only Windows has been verified.

```python
from pyui_framework import App, Button, Label, Theme, Window

local = Button("Action", on_click=lambda: None,
               style={"accent": "#b36a17", "accent_text": "#ffffff", "gradient": None})
app = App(Window("Themes", Label("Hello"), local), theme="system")
# In a callback, while running:
app.set_theme(Theme.load("lagoon.theme"))
app.set_theme(Theme("My theme", accent="#126e67", radius=20))
local.set_style(accent="#874bb5", radius=6)  # replaces all local tokens
local.set_style()                            # clears; resumes inheritance
app.run()
```

`App(window, *, theme="light")` and `app.set_theme(theme)` accept a validated
`Theme` or the case-sensitive strings `"light"`, `"dark"`, `"system"`. File
paths must be loaded explicitly. `Theme(name="Custom", **tokens)` makes an
immutable partial theme; `Theme.load(path)` reads UTF-8 (optional BOM), and
`Theme.parse(text, *, source="<theme>")` accepts text with diagnostic context.
`theme.tokens` returns a defensive copy of authored canonical tokens.
`app.theme` is the selected choice; `app.resolved_theme` returns a defensive
copy of the complete active palette. System resolves at `run()` startup;
reading its unresolved palette beforehand raises `RuntimeError`.

Window, Label and Button accept keyword-only `style=None` or a token dictionary.
Their `.style` returns a defensive copy. `.set_style(**tokens)` **replaces**
the complete local style, including before launch. No patch semantics or local
style file parsing is provided. Row and Column remain layout-only.

## Grammar and tokens

This is **CSS-inspired**, not browser CSS. Exactly one case-sensitive `:theme`
block is allowed. Every declaration ends with `;`. Whitespace and an empty
block are accepted. Duplicate declarations, empty declarations, unknown tokens,
comments, arbitrary selectors, additional blocks, variables, CSS cascade,
units, exponents and named colors are rejected. Declaration errors identify
the source, line and token/value; structural errors identify the source.

```css
:theme {
    background: #eaf5f2;
    foreground: #173b3a;
    panel: #eaf5f2;
    accent: #126e67;
    accent-text: #ffffff;
    radius: 20;
    opacity: 0.94;
    gradient: linear-gradient(#126e67, #65b8a3);
}
```

| File token | Python keyword | Accepted value | Used by / allowed local tokens |
| --- | --- | --- | --- |
| `background` | `background` | `#RRGGBB` | Window client background |
| `foreground` | `foreground` | `#RRGGBB` | Label text |
| `panel` | `panel` | `#RRGGBB` | Label background |
| `accent` | `accent` | `#RRGGBB` | Button solid fill |
| `accent-text` | `accent_text` | `#RRGGBB` | Button text and focus outline |
| `radius` | `radius` | 0..48 logical pixels | Label / Button corners |
| `opacity` | `opacity` | 0..1 | Window / Label / whole Button, including text |
| `gradient` | `gradient` | Two-stop horizontal gradient or `none` | Button fill replaces solid accent |

Colors canonicalize to lowercase. Python numeric tokens accept finite `int`/
`float` (excluding bool) and canonicalize to float. File numbers are unsigned
unitless decimals (`0`, `10`, `0.94`); signs, `.5`, `1.`, NaN and infinity are
unsupported. Python gradients accept a two-color tuple/list, canonicalized to
an immutable tuple, or `None` to disable. File gradients use exactly
`linear-gradient(#RRGGBB, #RRGGBB)` or `none`. Unknown types/ranges raise
`ThemeError`, a `ValueError` subclass. Local tokens unsupported by a component
also raise `ThemeError`, rather than silently having no effect.

## Resolution, live updates and System

Resolution is **Light component defaults → selected application theme → local
widget tokens**. Partial custom themes use Light defaults for every missing
token, never leftover values from the preceding theme. Window-local styles
do not cascade into children. Window opacity also affects its displayed content
through Qt's window compositing; child opacity can further reduce it.

Light retains the core slice palette and radius 10, opacity 1, no gradient;
Dark uses a dark background/panel, pale foreground/accent and dark button text.
Spacing, fonts, content inset, layout and edge scrollbar geometry are independent
of theme tokens. Hover/pressed overlays and the focus outline are internal
feedback, with no public interaction-state tokens in this version.

Theme/style validation finishes before mutation or notification. A failed load
or update raises an error and preserves the previous appearance and local styles.
Catch `ThemeError` in a callback to show an error without treating it as an
uncaught callback exception. Existing controls receive notified presentation
values; switching does not recreate their visual instances. Newly appended
controls inherit the current palette. All live updates must use the application
thread, like `add` and `set_text`; direct attribute assignment is unsupported.

System reads `QGuiApplication.styleHints().colorScheme()` and follows
`colorSchemeChanged`; explicit Light/Dark choices ignore those notifications.
The framework never changes the OS setting or sets Qt's scheme override.
If Qt reports Unknown when selecting System, `ThemeError` retains the last
valid theme (startup cannot show an unresolved System window). If the scheme
becomes Unknown while already following System, a `RuntimeWarning` reports it
and the last palette remains visible until a known scheme arrives.

The Windows probe exercised Qt's application-only `setColorScheme` Light →
Dark → Light and reset via `unsetColorScheme`, which Qt exposes for testing:
[Qt QStyleHints documentation](https://doc.qt.io/qt-6/qstylehints.html#colorScheme-prop).
This is evidence of the Qt signal path, **not a real Windows settings transition**.
The owner must still check Windows Light → Dark → Light while System is selected.

## Owner launch and limits

From the repository in PowerShell, with Python 3.13 installed:

```powershell
.\setup.cmd
.\run.cmd
.\run-themes.cmd
# Optional alternate reusable theme file:
.\run-themes.cmd "C:\path with spaces\custom.theme"
```

The theme studio has built-in choices, file reload, an equivalent Python Lagoon
theme and local replace/clear actions. Edit `examples/lagoon.theme`, save and
reload to test valid/invalid input. File errors appear in the studio status.
Scripts use the ignored `.venv-framework`, work from another current directory
and require no global package install. Close one example before launching the
other. `run.cmd` retains its ordinary core example and callbacks.

Physically compare colors/gradient/text, switch themes, replace/clear the local
sample, resize and scroll, and test valid/invalid file reloads. Inspect Tab/Space
focus and activation. Real OS transitions, physical input, different DPI/hardware,
accessibility, contrast safety, prolonged operation and other platforms remain
owner/future verification. No automatic contrast correction, file watching,
typography themes, arbitrary selectors, images/shaders, custom geometry or stable
1.x schema is promised. Themes and launch examples are source assets; executable
distribution remains out of scope.
