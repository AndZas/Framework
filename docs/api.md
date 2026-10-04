# Public Python API

This page documents the implemented, importable API in `pyui_framework` 0.1.0.
It describes the Windows-first 0.x development framework, not internal Qt/QML
objects, prototypes, or test utilities. The package name is temporary, the API is
experimental, and no stable 1.x compatibility is promised. Python 3.13 and
PySide6 6.11.2 are the current runtime requirements; Windows is the only
verified platform.

## Quick start

```python
from pyui_framework import App, Button, Label, Row, Window

window = Window(
    "Hello",
    Label("A small Python UI", heading=True),
    Row(
        Button("Save", on_click=lambda: print("save")),
        Button("Reset", on_click=lambda: print("reset")),
    ),
)

raise SystemExit(App(window, theme="system").run())
```

The framework owns presentation and rendering through its private Qt Quick
runtime. Application code builds a Python object tree and supplies Python
callbacks. It does not need to write QML.

## Public imports

All supported public names are exported from the package root:

```python
from pyui_framework import (
    App, Window, Label, Button, Row, Column,
    Theme, ThemeError,
    Keyframe, Timeline, Playback, AnimationError,
)
```

`_app`, `_model`, `_runtime`, Qt bridge objects, and QML files are implementation
details and are not public API.

## Application and window

### `App(window, *, theme="light")`

Creates an application around one `Window` and selects its initial appearance.
The same Window cannot be attached to a second App.

| Public member | Description |
| --- | --- |
| `theme` | The selected choice: `"light"`, `"dark"`, `"system"`, or the `Theme` object supplied by the caller. For `"system"`, this remains `"system"` while the resolved palette follows Qt's reported color scheme. |
| `resolved_theme` | A new dictionary containing the canonical, complete palette. For `theme="system"`, raises `RuntimeError` until `run()` resolves the system scheme. |
| `set_theme(theme)` | Validate and select a built-in choice or `Theme`. Can be called before startup or on the application thread while running. It preserves each widget's local style and active animation. |
| `run()` | Show the window and block until it closes; return the process-style exit status. Each App can be run once. A second call raises `RuntimeError`. |

`set_theme` accepts only the exact lower-case strings `"light"`, `"dark"`,
`"system"`, or a `Theme` instance. System mode follows Qt's color-scheme
notifications; it does not change the operating-system setting. An unknown
system scheme prevents initial resolution with `ThemeError`; after startup, an
unknown notification retains the last valid palette.

### `Window(title, *children, width=640, height=520, style=None)`

Creates the top-level window. Its direct children are arranged in a vertical
flow. The minimum accepted dimensions are 280 by 260 logical pixels.

| Public member | Description |
| --- | --- |
| `title` | Initial window title, a string. |
| `width`, `height` | Initial dimensions, exact integers at or above their respective minimums. |
| `children` | Read-only tuple snapshot of direct children. |
| `add(child)` | Append a `Label`, `Button`, `Row`, or `Column`; return that child. Live calls must run on the application thread. |
| `style` | Defensive copy of the window's local style tokens. |
| `set_style(**tokens)` | Replace all local window overrides. Calling with no tokens clears them and resumes inheritance. |
| `play(timeline)` | Start an appearance animation; see [Animations](#animations). |

Title and dimensions are construction-time settings; changing these attributes
directly after startup is unsupported. There is no public API yet to close,
remove, reorder, or reparent individual child objects, or to create multiple
windows in one App.

## Elements and layout

Every container accepts child elements either as constructor arguments or with
`add`. Children have one owner: adding a child that already belongs to a
container, creating a cycle, or using an unsupported child type raises a Python
error. `children` returns a tuple, not the mutable internal list. A live `add`
must be called on the application's thread.

| Constructor | Behavior and public members |
| --- | --- |
| `Label(text, *, heading=False, style=None)` | Displays wrapped text. `text` is read-only; `set_text(text)` changes it. `heading` is a Boolean presentation choice. `style`, `set_style(...)`, and `play(...)` are available. |
| `Button(text, *, on_click, style=None)` | Displays a clickable button. `on_click` must be a callable taking no arguments. It is called on activation. `text` and `on_click` are constructor-time attributes; no dynamic text setter is currently provided. `style`, `set_style(...)`, and `play(...)` are available. |
| `Row(*children)` | Horizontal layout; children share the available width. Provides `children` and `add(child)`. |
| `Column(*children)` | Vertical layout in insertion order. Provides `children` and `add(child)`. |

`Window`, `Row`, and `Column` are containers. `Label` and `Button` are leaves.
Row and Column are layout-only: they do not currently expose local style or
animation methods. The top-level content scrolls vertically when it exceeds the
available window space. Rows remain horizontal when the window narrows; their
children do not automatically wrap into a column.

`Label.set_text(text)` and live `add` calls must run on the application thread.
Direct assignment to other attributes after startup is unsupported. A callback
exception is reported to stderr; the window remains open and the App returns a
nonzero status when it eventually closes.

## Themes and widget styles

### `Theme(name="Custom", **tokens)`

Creates an immutable partial application theme. Missing tokens use the Light
defaults; they do not retain values from a previously selected theme.

| Public member | Description |
| --- | --- |
| `name` | Theme name. Must be a non-empty string. |
| `tokens` | Defensive dictionary copy of the explicitly authored, canonical tokens (not the fully resolved palette). |
| `Theme.load(path)` | Read and parse a UTF-8 theme file; an optional UTF-8 BOM is accepted. |
| `Theme.parse(text, *, source="<theme>")` | Parse CSS-inspired theme text. `source` is included in diagnostics. |

Invalid theme declarations raise `ThemeError`, a `ValueError` subclass. The
parser accepts a small CSS-inspired format, not general browser CSS. See the
grammar below and the [theme file example](../examples/lagoon.theme).

### Style tokens

`Window`, `Label`, and `Button` accept `style=None` or a dictionary in their
constructor. Their `.style` property returns a defensive copy. The
`set_style(**tokens)` method replaces the entire local override dictionary; it
does not merge with the previous call. `set_style()` with no arguments clears
the local overrides. Resolution order is Light component defaults → selected
application theme → widget-local style. Local styles do not cascade from a
Window into its children.

| Token | Theme / Python value | Valid on | Effect |
| --- | --- | --- | --- |
| `background` | `"#RRGGBB"` | Theme, Window | Window client-area color. |
| `foreground` | `"#RRGGBB"` | Theme, Label | Label text color. |
| `panel` | `"#RRGGBB"` | Theme, Label | Label surface color. |
| `accent` | `"#RRGGBB"` | Theme, Button | Button solid fill. |
| `accent_text` | `"#RRGGBB"` | Theme, Button | Button text and focus outline color. In a theme file, spell this `accent-text`. |
| `radius` | finite number from 0 to 48 | Theme, Label, Button | Corner radius in logical pixels. |
| `opacity` | finite number from 0 to 1 | Theme, Window, Label, Button | Window, label, or entire button opacity, including its text. |
| `gradient` | two-color tuple/list or `None` | Theme, Button | Horizontal two-stop fill. `None` disables the gradient and restores solid `accent`. |

Colors must be six-digit `#RRGGBB` strings and are normalized to lower case.
Numeric values accept finite `int` or `float` values, but not `bool`; they are
normalized to floats. Python gradients have exactly two colors, for example
`("#126e67", "#65b8a3")`. In a theme file, use
`linear-gradient(#126e67, #65b8a3)` or `none`.

As a theme token, `opacity` is applied to the Window and to each Label and Button.
The effects can therefore compound. A Window-local opacity override affects
the native window only; a Label/Button-local override affects that widget.
Token validation completes before appearance changes, so an invalid style or
theme leaves the previous valid appearance in place.

Built-in theme choices are `"light"`, `"dark"`, and `"system"`. In the default
Light palette, background and panel are `#f1f4f9`, foreground is `#23324d`,
accent is `#365a94`, accent text is `#ffffff`, radius is 10, opacity is 1, and
gradient is disabled. In Dark, background and panel are `#131a2a`, foreground is
`#e5eafa`, accent is `#819bff`, accent text is `#131a2a`, radius is 10, opacity
is 1, and gradient is disabled.

The supported file structure is one `:theme { ... }` block with semicolon-ended
declarations. For example:

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

Selectors, comments, variables, cascade rules, CSS units, named colors,
alpha-color syntax, and arbitrary CSS are not supported. File numeric values are
unsigned unitless decimals. Duplicate or unknown declarations are rejected.

## Animations

Animations are immutable Python descriptions; Qt Quick handles timing and
interpolation. The Python API does not receive a callback for each rendered
frame.

### `Keyframe(time, *, easing="linear", **values)`

Describes the values at an integer timestamp in milliseconds. Time must be an
exact integer from 0 through 2147483647. Each frame needs at least one supported
property. Keyframes cannot be modified after creation.

| Public member | Description |
| --- | --- |
| `time` | Timestamp in milliseconds. |
| `easing` | Easing name used when interpolation arrives at this frame. |
| `values` | Defensive dictionary copy of this frame's canonical property values. |

### `Timeline(*keyframes)`

Requires at least two `Keyframe` objects with strictly increasing timestamps;
frames are not sorted automatically. Its public properties are `keyframes`, an
immutable tuple, and `duration`, the time of the final frame. A Timeline can be
shared by widgets; each call to `play` creates independent playback state.

### `widget.play(timeline)` and `Playback`

`Window`, `Label`, and `Button` expose `play(timeline)`. The target must be live,
presented in `App.run()`, and called from the application thread. The method
returns a `Playback`; animation cannot be queued before startup. Invalid
descriptions, unsupported target properties, or unavailable targets raise
`AnimationError`, a `ValueError` subclass.

`Playback` is exported for its state and control interface; obtain instances from
`widget.play(...)` rather than constructing them directly.

| Public member | Description |
| --- | --- |
| `state` | `"running"`, then `"completed"`, `"stopped"`, `"replaced"`, or `"closed"`. |
| `running` | Boolean convenience property, true only while `state == "running"`. |
| `stop()` | Stop this active run and restore the latest theme/local-style base. Idempotent; a stale handle cannot stop its replacement. |
| `restart()` | Start the same Timeline from zero with a fresh base snapshot; return a new `Playback`. Raises `AnimationError` if its target no longer exists. |

One Timeline controls a widget at a time. Starting another valid Timeline on
that widget replaces the whole previous run. Different widgets can animate in
parallel. Stop and completion release the temporary animated appearance and
restore the latest theme and local style, including changes made during
playback. Animated properties keep their tracks while unanimated properties
reflect style/theme changes immediately.

| Widget | Supported animated properties |
| --- | --- |
| `Window` | `opacity` (0..1), `background` (`#RRGGBB`) |
| `Label` | `opacity` (0..1), `scale` (0..2), `radius` (0..48), `foreground`, `panel` |
| `Button` | `opacity` (0..1), `scale` (0..2), `radius` (0..48), `accent`, `accent_text` |

Animation colors use `#RRGGBB`; numeric values must be finite `int` or `float`
values excluding `bool`. Easing names are case-sensitive: `linear`, `in_quad`,
`out_quad`, `in_out_quad`. Easing on a destination keyframe applies to the
segment arriving at that frame.

Properties have independent tracks. If a track has no keyframe at time zero, it
starts from the currently resolved appearance (or scale 1). An explicit zero
keyframe applies immediately. A track holds its last value until the complete
Timeline ends. Scale is centered and does not change layout, so it can overlap
neighbors or be clipped. Gradients, geometry, layout, Row/Column animation, and
arbitrary QML properties are not supported animation targets.

```python
from pyui_framework import App, Button, Keyframe, Timeline, Window

intro = Timeline(
    Keyframe(0, opacity=0.25, scale=0.96),
    Keyframe(180, opacity=1.0, scale=1.0, easing="out_quad"),
    Keyframe(420, radius=18),
)
button = Button("Replay", on_click=lambda: button.play(intro))
raise SystemExit(App(Window("Animation", button)).run())
```

## Current API boundaries

- The framework currently targets Windows. Linux, macOS, and Android have not
  been verified.
- One `App` owns one top-level `Window`; there is no public API for multiple
  windows, modal dialogs, remove/reparent/reorder, or explicit geometry layout.
- There is no public arbitrary drawing/canvas, custom path shape, shader,
  per-frame Python animation callback, or public QML escape hatch.
- Mouse and Qt Quick button keyboard activation are provided by the controls;
  this API does not expose a general raw-input event stream, gamepad API, audio
  device API, or video playback API.
- There is no public image/texture widget, accessibility contract, executable
  packaging workflow, or stable 1.x schema yet.

These boundaries describe the current importable API, not a promise that later
versions will never add those capabilities.
