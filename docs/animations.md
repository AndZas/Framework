# Experimental keyframe animations

The 0.x API describes temporary appearance animations in Python. Qt Quick
performs timing and interpolation; there is no Python timer or callback per
frame. Windows is the verified target. Public names remain experimental.

```python
from pyui_framework import App, Button, Keyframe, Timeline, Window

intro = Timeline(
    Keyframe(0, opacity=0.25, scale=0.96),
    Keyframe(180, opacity=1.0, scale=1.0, easing="out_quad"),
    Keyframe(420, radius=18),
)
button = Button("Replay", on_click=lambda: button.play(intro))
raise SystemExit(App(Window("Animations", button)).run())
```

`Keyframe(time, *, easing="linear", **values)` is immutable. `time` is an
integer in **milliseconds**, from 0 to 2147483647 inclusive (Qt's signed-int
duration boundary). Booleans, fractional timestamps and negative times are
invalid. At least one supported property is required in each keyframe.
`frame.values` returns a defensive dictionary of canonical values.

`Timeline(*keyframes)` is immutable and requires at least two Keyframe objects
with strictly increasing timestamps. Duplicate timestamps are errors; frames
are never silently sorted. The last timestamp is `timeline.duration` and is
therefore positive. `timeline.keyframes` is an immutable tuple. Descriptors
can be shared by widgets without sharing playback state.

## Properties and interpolation

| Widget | Accepted properties | Values |
| --- | --- | --- |
| Window | `opacity`, `background` | opacity 0..1; background `#RRGGBB` |
| Label | `opacity`, `scale`, `radius`, `foreground`, `panel` | opacity 0..1; scale 0..2; radius 0..48 logical pixels; colors `#RRGGBB` |
| Button | `opacity`, `scale`, `radius`, `accent`, `accent_text` | Same numeric ranges; colors `#RRGGBB` |

Numbers accept finite int/float, excluding bool. Colors canonicalize to lowercase.
No gradients, alpha-color strings, named colors, geometry/layout or arbitrary
QML properties are accepted. Row and Column have no animation API. Scale changes
presentation about the center without changing layout allocation. Scaling up
can overlap neighbors or be clipped by the viewport. Scale/opacity zero can
make a sample invisible; use a separate visible replay button if needed.
Window opacity affects desktop compositing and content as described in
[themes](themes.md).

Each property has an independent track, interpolating between only frames that
contain it. Omitting a property does not create a point or reset its track.
If its first point is later than zero, an implicit zero point snapshots the
resolved theme plus local style at playback start; scale's base is always 1.
An explicit point at zero applies immediately and deterministically. Each track
holds its last value until the whole timeline's last timestamp. Then all animated
properties restore their base appearance. In the snippet, opacity reaches 1 at
180 ms and holds until 420 ms; radius interpolates from its styled base at zero
to 18 at 420 ms.

The **destination keyframe** supplies the segment's easing. Supported,
case-sensitive names: `linear`, `in_quad`, `out_quad`, `in_out_quad`.
Easing at zero has no incoming segment. Numbers use Qt Quick NumberAnimation;
colors use ColorAnimation, without a perceptual color-space or gamma-correction
guarantee. See Qt's [animation](https://doc.qt.io/qt-6/qml-qtquick-animation.html),
[NumberAnimation](https://doc.qt.io/qt-6/qml-qtquick-numberanimation.html) and
[ColorAnimation](https://doc.qt.io/qt-6/qml-qtquick-coloranimation.html) contracts.
Existing finite rendering/color precision still applies.

## Playback and lifecycle

`widget.play(timeline)` requires a live Window, Label or Button inside
`App.run()`, called on the application thread (normally a button callback).
It returns a `Playback`; obtain it through play rather than constructing it.
Calling play before launch, after close, or before an appended widget has been
presented raises `AnimationError`. Appending then playing in a later UI callback
is supported. There is no pre-launch queue.

```python
run = button.play(intro)
run.stop()                  # stop immediately and restore the base
run = run.restart()         # new Playback from zero; fresh base snapshot
print(run.state, run.running)
```

Exactly one timeline controls a widget. A valid new play replaces the **entire**
previous run, even with disjoint property sets. Replacement resets to the base
before applying new zero points; it never samples a partially animated value
as its starting value. Different widgets can run independently together.

Stop is idempotent and affects only that run if still active. An old handle
cannot stop its replacement. Restart returns a **new** Playback of the same
description, replacing any current run on the target. It can restart a completed,
stopped or replaced run while the target remains live. After close/destruction
it raises AnimationError. A detached handle's stop is a safe no-op. Handles
retain a descriptor and weak target reference, with no Qt objects.

`state` is `running` during playback, then `completed`, `stopped`, `replaced`,
`theme_changed`, `style_changed` or `closed`. `running` equals
`state == "running"`. No pause/resume, seek, loops, completion callbacks,
persistent final-value mode or public Qt objects are offered. Qt sends one
completion notification per run. Completion/stop/replacement stops and schedules
internal objects for destruction. Shutdown stops all runs, destroys QML before
bridge objects, and detaches Python targets.

Descriptors validate names/types/ranges/easing at construction; play validates
widget-specific restrictions and target readiness before modifying appearance.
Failures raise `AnimationError` (a ValueError subclass) and preserve the previous
valid appearance/run. Qt Quick constructs the next group before releasing the
previous one. A missing playback acknowledgement reports an error. Wrong-thread
controls raise RuntimeError before mutation, like other live APIs.

## Themes and local styles

Animation is a **temporary overlay**, without changing `widget.style` or theme
values. Completion and stop restore theme plus local style bindings. A valid
`widget.set_style(...)`, including clear or a repeated value, stops that widget's
entire run with `style_changed` before applying the replacement. Other widgets
keep running. A valid `app.set_theme(...)`, including reselecting the same theme,
stops all active runs with `theme_changed`, then applies the theme while retaining
local overrides. A known System scheme notification follows this rule. Invalid
style/theme changes preserve active runs; an Unknown System notification retains
the previous palette and playback.

A Button `accent` track temporarily displays a solid fill even with a base
gradient. Stop/completion restores the gradient. Other property tracks do not
disable it. Hover/pressed feedback and focus outlines remain Qt Quick control
feedback; no new interaction-state styling policy is introduced.

## Windows launch and checks

From `F:\Files\PythonProjects\Framework` in PowerShell:

```powershell
.\run-animations.cmd
# Exact equivalent using the existing dedicated environment:
.\.venv-framework\Scripts\python.exe examples\animations.py
# Ordinary example is unchanged:
.\run.cmd
```

If the venv is absent, run `./setup.cmd` first. The launcher locates the repository
from its own directory and works with another current directory. It needs no
global package installation or application-authored QML.

The example demonstrates fade/scale and color/corner keyframes. Click either
sample or its Replay repeatedly. Stop all restores the base, and Restart last
replays retained descriptions. Change Light/Dark/System during playback; try
Local purple and Clear local. Resize and scroll, then repeat the actions.

```powershell
.\.venv-framework\Scripts\python.exe -m pytest tests/test_animation.py -q
.\.venv-framework\Scripts\python.exe tests\animation_probe.py evidence\TASK-0011
.\.venv-framework\Scripts\python.exe -m pytest -q
.\tests\animation_launch_probe.ps1
```

The probe launches the actual example with synthetic QtTest input. It relates
parallel tracks to check interpolation and waits for state transitions with
generous timeouts, without tight frame deadlines. Evidence includes Windows
captures and environment/results JSON. Physical input, real OS theme transitions,
other GPUs/DPI, prolonged runs and non-Windows platforms remain unverified here.
Owner review must confirm physical replay and perceived motion on their display.
