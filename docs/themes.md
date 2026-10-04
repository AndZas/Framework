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
    opacity: 1;
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
Dark uses matching dark background/panel, pale foreground/accent and dark button
text. Both built-in palettes blend Labels into the window. An explicit custom
or local `panel` still paints a distinct Label surface; it is not discarded.
Spacing, fonts, content inset, layout and edge scrollbar geometry are independent
of theme tokens. Hover/pressed overlays and the focus outline are internal
feedback, with no public interaction-state tokens in this version.

The experimental [keyframe API](animations.md) adds a temporary appearance
overlay. A valid theme switch stops every active animation before applying its
palette; a valid local style replacement/clear stops that widget's animation.
Invalid updates retain active playback. Completion/stop restores normal theme
and local-style bindings. Animation never changes authored theme/style tokens.

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
The owner subsequently confirmed a real Windows Light/Dark transition in the
studio on this setup (TASK-0010 owner review, 2026-10-04). This is owner-observed
coverage; Codex has not repeated the OS-setting change or verified other setups.

## Whole-window opacity and gradient quantization

Loading a file does not implicitly enable transparency. The original Lagoon
asset explicitly used `opacity: 0.94`; the equivalent Python Theme did the same.
That value reaches Qt's native Window opacity and lets the desktop show through
the whole window. The shipped Lagoon file and Python object now both use **1.0**
to give an opaque default. Explicit values below 1 remain supported in both
authoring forms. See [Qt Window opacity](https://doc.qt.io/qt-6/qwindow.html#opacity-prop).

The semantic opacity token also applies to each Label and Button. At theme
opacity 0.94, controls first blend into the client background at 0.94, and the
whole window then blends with the desktop at 0.94; an isolated foreground's
contribution is approximately `0.94 * 0.94 = 0.8836`. A Window-local
`set_style(opacity=...)` affects only the native window; a Button-local override
affects only that control. Studio's 0.94/1.0 comparison buttons set a Window-local
override; the Clear window opacity button restores inheritance. A theme switch
preserves this override, just as it preserves other local styles.

Midnight uses the same accepted file syntax with stops `#55377e` → `#285b78`;
no format migration is needed. The Windows Direct3D11 follow-up probe compares
file/Python frames and measures a text-free horizontal row of the actual Button
render. Both forms produce identical images. Channels change monotonically by
at most 1/255 per adjacent pixel. On a 762-pixel button, Midnight's narrow RGB
range yields 80 distinct sampled RGB triplets and repeated colors for up to
17 pixels, versus 188 triplets / 9 pixels for Lagoon. These small quantized steps
can be perceived as bands, particularly in the dark palette.

The capture is RGBA8 (8 bits per channel). Rounded Qt Rectangles additionally
interpolate byte vertex colors at their arc mesh vertices; the verified
[Qt 6.11.2 source](https://github.com/qt/qtdeclarative/blob/v6.11.2/src/quick/scenegraph/qsgbasicinternalrectanglenode.cpp)
uses byte color arithmetic. Rounded Midnight differs from ideal float-linear RGB
by at most 1.70/255; the radius-0 control reduces this to 0.56/255 but still has
flat runs up to 18 pixels. Narrowing the rounded control to 400 pixels reduces
its longest flat run to 9. This evidence points to finite color precision and
Qt mesh quantization, rather than missing stops or a framework mapping regression.
It does not establish the exact physical monitor's perceived banding. No dithering
or alternate renderer is added; HDR, other GPUs/DPI/backends remain unverified.
The owner reports visible bands on one VA monitor and not on an IPS monitor.
That is a display-specific perceptual observation, not a reproduced renderer
defect or proof that all VA/IPS displays behave alike. The existing Windows
pixel-profile evidence is preserved.

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
theme, Python Midnight, window-opacity comparison and local replace/clear actions.
Load the production demo file with
`./run-themes.cmd examples/midnight.theme`, then compare with Python Midnight.
Both demo authoring forms set `panel` equal to `background` (`#171827`) so Labels
blend into the window. Authors can still choose a distinct `panel` in custom
files or Python Themes. The earlier prototype palette retains its historical
contrasting panel; use the production example asset for this corrected demo.
The production package does not import prototype modules.
Edit `examples/lagoon.theme`, save and
reload to test valid/invalid input. File errors appear in the studio status.
Scripts use the ignored `.venv-framework`, work from another current directory
and require no global package install. Close one example before launching the
other. `run.cmd` retains its ordinary core example and callbacks.

Physically compare colors/gradient/text, switch themes, replace/clear the local
sample, resize and scroll, and test valid/invalid file reloads. Inspect Tab/Space
focus and activation. The owner has verified physical clicks, reload and a real
OS transition on this setup; different DPI/hardware, accessibility, contrast
safety, prolonged operation and other platforms remain future verification.
No automatic contrast correction, file watching,
typography themes, arbitrary selectors, images/shaders, custom geometry or stable
1.x schema is promised. Themes and launch examples are source assets; executable
distribution remains out of scope.
