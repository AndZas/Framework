# QML controls and dynamic Python tree spike

This is an isolated Windows experiment, not a framework backend decision or a stable API. Application construction stays in Python; QML is internal reusable control code.

## Setup and run

From the repository root in PowerShell:

```powershell
.\.venv-qt-quick\Scripts\python.exe -m pip install -r prototypes\qml_tree_spike\requirements.txt
.\.venv-qt-quick\Scripts\python.exe prototypes\qml_tree_spike\main.py
.\.venv-qt-quick\Scripts\python.exe prototypes\qml_tree_spike\main.py --probe
```

The existing `.venv-qt-quick` was reused. The install command and interactive command above are guidance; only the `--probe` command was run for this task. The normal window has three independent buttons and a star. Clicking the first button switches the theme. The orange button keeps its override.

## Python-only example

`main.py` builds the visible controls from this model; no application QML or generated source locations are involved:

```python
controls = (
    Control("theme", "button", "Change theme", callback("theme", True), pulse=Pulse()),
    Control("orange", "button", "A long label that wraps to two lines when the window becomes narrow", callback("orange"), fill="#d86642"),
    Control("third", "button", "Third independent button", callback("third")),
    Control("star", "star", "", callback("star")),
)
app = App(Window("QML controls and dynamic Python tree", controls))
app.run()
```

After the window is visible, `app.add(Control("dynamic", "button", "Added after showing", callback("dynamic")))` appends an instance; `app.remove("dynamic")` removes it. The probe then appends 50 more buttons using IDs `repeat-00` through `repeat-49`. IDs are required to be unique; the callback table is keyed by instance ID. Neither callback dispatch nor the Python example depends on a QML `objectName` or source line.

## Implementation and API friction

- `model.py` defines only `Control`, `Window`, `Theme`, and `Pulse`. The same `fill` and `pulse` fields apply to the example controls; the theme is a Python value exposed through notifying bridge properties.
- `main.py` owns a `QAbstractListModel` with roles for instance ID, type, label, fill, and animation. Insert/remove row notifications drive a QML `Repeater`. `Bridge.activate(id)` dispatches to the matching Python callback, and missing IDs or callback exceptions print `BRIDGE ERROR` with the ID.
- `Main.qml` provides the `Flickable`/`Column` and creates delegates from the model. `ButtonControl.qml` is a reusable Qt Quick Controls `Button` using the Basic style, custom rounded background, wrapped/elided two-line text, focus outline, and scale animation. `StarControl.qml` uses Qt Quick Shapes `Shape`, `ShapePath`, `PathLine`, and `LinearGradient`, with the same optional scale animation. Neither control uses Canvas or QQuickPaintedItem.
- The star has a 100×100 `MouseArea`. Its point-in-polygon hit test uses the same ten vertices written in the `ShapePath`; a click inside the polygon activates it and the tested empty corner does not. Border/edge precision and touch hit testing were not checked.
- Internal QML load and runtime warnings are printed as `QML ERROR` with component file URL and line. If the root cannot load, Python raises `RuntimeError`; the warning gives the internal QML location. Callback exceptions are caught and printed with the stable ID. There is no mapping from an internal QML line to the Python statement that created a control. The Python API does not expose QML object names, though the probe uses internal `controlAt` and `scrollTo` helpers to target synthesized events.

The main implementation cost was maintaining model roles and row notifications, the Python-to-QML bridge, and two QML component files. Qt Quick Controls needed an explicit non-native Basic style before loading the engine to allow custom `background`/`contentItem`; the first run exposed this through warnings. Capturing actual QML frames from Python also required wrapping the engine's `QWindow` root as `QQuickWindow` for this probe. These details remain internal to the experiment. Layout, wrapping, scrolling, theme bindings and animation live in short QML definitions rather than Python paint/layout code.

## Actual Windows verification

Environment printed by the probe: Windows 11 build 26200, Python 3.13.9, PySide6 6.11.2, Qt 6.11.2. Command run from repository root:

```powershell
.\.venv-qt-quick\Scripts\python.exe prototypes\qml_tree_spike\main.py --probe
```

The final run exited with code 0 and `RESULT failures=[]`, with no `QML ERROR` messages. A visible 600×460 window contained four Python-model controls. Synthetic QtTest clicks activated the three buttons and star once each, and a star empty-corner click produced no callback. The theme button changed the Python surface to `#252238`; the orange control kept `#d86642`. Sampled button scale values differed during the run (for example, 1.034 and 1.008), consistent with the configured animation; this is not a frame-rate measurement.

The window was resized to 300×500; the reported button width became 268. The [initial capture](initial.png) and [narrow capture](narrow.png) were visually inspected. The latter shows the long orange label on two lines, dark surface, changed theme colors, orange override, star gradient, and controls within the narrower viewport. The probe added `dynamic` after showing the window, clicked it once, clicked the pre-existing `third` button again, removed `dynamic`, and clicked `third` once more. All ID-specific counts matched expectations.

The probe then appended 50 buttons, bringing the model to 54 controls. It scrolled to and clicked `repeat-00` and `repeat-49`; each invoked its own callback once. The [repeated-control capture](repeated.png) shows the end of the scrollable list, including `repeat-49`. This demonstrates creation, scrolling, rendering and two sampled interactions in one short local run. It is **not** a benchmark or smoothness guarantee. No GPU timings, display FPS or sustained interaction measurements were made.

Earlier development runs found two issues, both fixed before the final run: the platform's native Qt Quick style rejected background/content customization, and a screen-level grab returned a stale frame after resize. The final probe selects Basic and captures through `QQuickWindow.grabWindow()`. A shutdown-time warning from destroying the QML context before the root was also removed by closing/deleting the window before exit.

## Recommendation and remaining unknowns

The tested QML-backed tree handled stable dynamic identity, reusable Controls/Shapes, theme binding, override, animation, scroll layout and long text cleanly enough for **owner review of Qt Quick as an MVP candidate**. No blocker appeared in this bounded slice. The cost is extra QML plumbing and weaker error attribution to the Python author. Production API design, accessible names and screen-reader behavior, focus order, physical keyboard/mouse and touch, DPI variation, edge hit precision, large-list virtualization, memory/CPU/GPU behavior, packaging, and other platforms remain unverified. The current `Repeater` creates all 50 items and is not a scalable list design. No architecture adoption is made here.
