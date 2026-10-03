# Python-first Qt Quick API spike (Windows, 2026-10-03)

This isolated experiment tests a Python-only authoring surface. It is not a stable framework API or a decision to adopt Qt Quick. No application QML or generated QML is used.

## Setup and run

From the repository root in PowerShell:

```powershell
.\.venv-qt-quick\Scripts\python.exe -m pip install -r prototypes\python_api_spike\requirements.txt
.\.venv-qt-quick\Scripts\python.exe prototypes\python_api_spike\main.py
.\.venv-qt-quick\Scripts\python.exe prototypes\python_api_spike\main.py --probe
```

The existing `.venv-qt-quick` from TASK-0001 already contained the pinned dependency, so the install command above is setup guidance; it was **not** run for this task. The interactive command is also setup guidance; the `--probe` command was run. The probe creates both windows, synthesizes mouse clicks, records counters and animation scale, saves [light](probe-light.png) and [dark](probe-dark.png) main-window captures, then exits.

## Authoring example

`main.py` contains the runnable example. The small public shape is:

```python
app = App(theme=Theme())
window = app.add(Window(title="API spike"))
window.add(Button("Click me", on_click=handle_click, pulse=Pulse(duration_ms=420)))
window.add(Star(on_click=handle_star))
app.run()
```

`app.add(window)` is the meaningful change from the task's illustrative shape: explicit ownership lets one app manage multiple independent windows. `App.set_theme(Theme(...))` switches the theme at runtime. `Button(..., fill="#d86642")` overrides one control's fill. Themes are Python `dataclass` values with a few named colors; this is the minimum theme input tested.

## Implementation and friction

`api.py` creates `QQuickWindow` and `QQuickPaintedItem` objects directly from Python. Python callbacks are called from each item's mouse release handler. `App.set_theme` stores the new Python theme, sets each window's Qt Quick background color, and requests repaints for its controls. `QPropertyAnimation` animates the button's Qt Quick `scale` property from Python `Pulse` configuration. The star builds one `QPainterPath` and uses it for both `paint()` and `contains()`; rounded buttons build equivalent paths for both operations. No QML generation or context-property bridge exists in this version.

The API needed explicit window registration, fixed vertical placement, manual ownership of the native windows and animation objects, and custom paint/input classes even for a basic button. `QQuickPaintedItem` paints through Qt's painter path into a scene-graph texture; this makes the one-path experiment simple but leaves rendering efficiency, text metrics, accessibility, keyboard focus, and richer layout untested. It is Qt-specific internal code. The probe's second screenshot had to be scheduled on a later event-loop turn; calling `grabWindow()` immediately after synthetic clicks hung one run, which was terminated. No production error handling or cleanup was added.

A smallest CSS-inspired extension would parse a narrow set of tokens such as `surface`, `accent`, and `star` into `Theme`, then feed the same `set_theme` path. Selectors, cascading, computed values, per-state styles, and arbitrary properties are outside this experiment; whether a token parser stays maintainable as controls multiply needs another test.

## Environment and observed results

- Windows 11 build 26200, Python 3.13.9, PySide6 6.11.2, Qt 6.11.2. GPU reported by `Win32_VideoController`: NVIDIA GeForce RTX 5060 Ti, driver 32.0.15.9636. The existing virtual environment was reused. No non-Qt runtime dependency was required.
- Commands actually run: `.\.venv-qt-quick\Scripts\python.exe prototypes\python_api_spike\main.py --probe` three times (first completed, second hung during an immediate post-click capture and was stopped, final run exited with code 0); `Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion` for environment details.
- Final probe: `WINDOWS count=2 distinct=True visible=True`; button callback count `1`; theme changed to surface `#252238`; star callback count `1`. Rounded and star interior clicks each counted `1`; their empty-corner clicks left counts at `1`. The per-control fill remained `#d86642`. Button scale was `1.029` during the probe and `1.032` later; this shows the configured Qt property animation was active in this run. Both captures were saved and visually inspected: the star and rounded controls are visible, shared colors changed, and the orange override stayed orange.
- The star's path-based hit test matches the filled geometric path for the tested interior and empty corner. Anti-aliased edge pixels and the stroked border were not compared to the input boundary. Physical mouse, touch, keyboard, accessibility, window close behavior, other operating systems, packaged deployment, rendering performance, and richer application layouts were not tested.

**Recommendation:** A Python-first surface appears practical for these small scenarios, including callback, theme, animation, star hit test, and two windows. Direct Qt Quick item authoring avoids QML leakage but requires considerable implementation per control. The next API experiment should compare this item-based approach with a minimal generated-QML bridge for layout and text, using the same small authoring example and measuring the code and debugging burden. That comparison is evidence for owner review, not an architecture decision.
