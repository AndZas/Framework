# Python API backend comparison (Windows, 2026-10-03)

This isolated experiment compares direct Python-created Qt Quick items with a Python-authored tree rendered by internal QML. It does not select a framework backend or define a stable API. Application code writes no QML. `qml_backend.py` owns the internal QML template; `direct.py` uses no QML.

## Setup and run

From the repository root in PowerShell:

```powershell
.\.venv-qt-quick\Scripts\python.exe -m pip install -r prototypes\api_backend_comparison\requirements.txt
.\.venv-qt-quick\Scripts\python.exe prototypes\api_backend_comparison\main.py --backend direct
.\.venv-qt-quick\Scripts\python.exe prototypes\api_backend_comparison\main.py --backend qml
```

The install and interactive commands above are setup guidance, not commands run for this task. The existing virtual environment was reused. The exact verification commands are below. The button changes the theme and prints a callback count; the star prints its callback count. Space activates the focused button. Resize the window to see label width and star position change.

## Matched authoring example

Both backends consume this one Python construction in `main.py`:

```python
window = Window("Backend comparison", (
    Label("Python-authored Qt Quick UI"),
    Button("Change theme", button_clicked, fill="#d86642", pulse=Pulse()),
    Star(star_clicked),
))
app = App(window)
app.run("direct")  # or "qml"
```

The button callback switches between two Python `Theme` values; the star callback increments a Python counter. `fill` keeps the button orange across the theme switch. `Pulse` animates its scale. The sole authoring difference is the backend string passed to `run`; the executable uses `--backend` to select it. This surface is intentionally limited to one label, one button and one star in one window. It is a comparison fixture, not a general tree compiler or layout API.

## How the implementations differ

| Concern | Direct items | Internal QML |
| --- | --- | --- |
| Python authoring | Same `Window` and three children | Same `Window` and three children |
| Control implementation | `Painted` branches for label, rounded button and star; QPainter drawing, `QPainterPath` hit testing, mouse/key handlers | Internal `Text`, `Rectangle`, `Canvas`, `MouseArea` and keys; star points shared by Canvas drawing and polygon hit testing |
| Layout and text | `widthChanged` calls a Python layout function; QPainter font and alignment are explicit | `Column`, width binding, anchors and `Text` font/alignment handle the tested layout |
| Theme and override | Python changes window color and calls `update()` for each item; button resolves override in paint | `Bridge` exposes notifying color properties; QML bindings update window, label and button; Canvas explicitly requests repaint; override is a generated literal |
| Animation | Python owns a looping `QPropertyAnimation` | Internal QML owns a looping `SequentialAnimation` |
| Callbacks and mapping | Each painted item holds its Python specification; `items` maps names to native items | `Bridge.activate(name)` dispatches to Python callbacks; `objectName` and `findChild` map names to QML objects |
| Errors and debugging | Python exceptions point into paint/event/layout methods; item properties can be inspected directly | QML parse/runtime errors occur across the generated source and bridge boundary; the loader checks root and named objects, but does not annotate generated lines with Python widget source locations |

Adding or changing a control in the direct variant requires painting, size/layout and possibly input/focus code. In the QML variant it requires an internal template item plus Python-data substitution and mapping. For this fixed example, QML bindings made resize and text layout simpler to express. The QML variant needed explicit bridge notification and Canvas repaint logic; a missed `requestPaint()` initially left the dark theme's star yellow in the captured image, and fixing the signal handler made it mint. The direct variant needed manual layout and painted text for even this small screen.

The QML `Canvas` uses a JavaScript 2D context, while the direct variant uses `QQuickPaintedItem`. Both can involve image-to-texture uploads, particularly when repainted; no timing or GPU measurements were made. Qt documents these mechanisms in [QQuickPaintedItem](https://doc.qt.io/qt-6.11/qquickpainteditem.html) and [Canvas](https://doc.qt.io/qt-6.11/qml-qtquick-canvas.html). The QML `Text` item and focus/key handlers are promising built-in primitives, but accessibility tree, screen readers, focus order, focus visuals, physical keyboard/mouse, DPI variation and assistive technology were not checked. Neither prototype configures accessibility metadata.

## Actual Windows verification

Environment printed by both probes: Windows 11 build 26200, Python 3.13.9, PySide6 6.11.2, Qt 6.11.2. Existing `.venv-qt-quick` was used. Commands run from the repository root:

```powershell
.\.venv-qt-quick\Scripts\python.exe prototypes\api_backend_comparison\main.py --backend direct --probe
.\.venv-qt-quick\Scripts\python.exe prototypes\api_backend_comparison\main.py --backend qml --probe
.\.venv-qt-quick\Scripts\python.exe prototypes\api_backend_comparison\main.py --backend direct --capture
.\.venv-qt-quick\Scripts\python.exe prototypes\api_backend_comparison\main.py --backend qml --capture
```

Final sequential probe runs exited with code 0 for both backends. Each reported a visible 420×350 window, then a 600×400 window. Label scene width changed from 372 to 552; star scene x changed from 150 to 240, keeping it centered. The button's sampled scale changed from about 1.00 to about 1.07 during the probe, so the configured animation was active. A synthetic click at the rounded button's empty corner did not invoke its callback; an interior click invoked it once and set the dark theme. A synthetic star interior click invoked its callback once; a star empty-corner click did not. Synthesized Space activation invoked the button again and restored the light theme. The orange override remained `#d86642` in Python. The button's `mapToScene` x coordinate varied slightly because its scale animation was running; the logical left edge remained at 24.

The separate capture runs exited with code 0 and saved `direct-initial.png`, `direct-resized.png`, `qml-initial.png` and `qml-resized.png`. They were visually inspected: text was readable and left aligned, the rounded button text was centered, the star was centered after resize, the background and star changed to dark-theme colors, and the orange override remained orange. An earlier attempt combining screenshot capture with synthetic clicks hung the direct process after its first button callback and was stopped. A separate attempt that sent the rounded-corner click immediately after the theme-changing click also hung the direct process; moving the corner click before the theme-changing click completed. The exact Qt interaction causing these hangs was not diagnosed. Captures and probe actions therefore use separate runs.

These are synthetic QtTest input events and Qt window grabs, not physical-device or accessibility checks. The test covered one resize only. Small-window clipping, long or translated text, high DPI, multiple controls of one type, cleanup, QML error-to-Python source mapping, other platforms and performance remain unverified. The static QML template assumes exactly one of each child type and does not escape arbitrary style values beyond JSON string quoting.

## Recommendation for owner review

For the tested label, button and star, **internal QML was easier for layout and text** because widths, alignment and resize response were declarative. **Direct items were easier to trace from Python object to rendering and hit-test code**, and the star reused one `QPainterPath`. Both kept identical short Python authoring code. Complexity moved from Python paint/layout/event handlers to an internal QML template, context-property bridge, object lookup and explicit Canvas repaint. Neither is yet a backend choice. The smallest useful next experiment is one additional dynamic control instance with a long label at two window sizes: it would test whether a Python tree can generate repeated QML objects with reliable callback identity and source-level error reporting, versus how much manual direct-item layout grows.
