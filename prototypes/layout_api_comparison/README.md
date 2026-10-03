# Experimental layout API comparison

TASK-0006 compares two Python authoring styles using the same internal PySide6 +
Qt Quick presentation. It recommends a layout policy for owner review; it makes
no final public API or overall architecture decision. Nothing is added to the
production framework.

## User launch (Windows)

From the repository root in PowerShell:

```powershell
.\prototypes\layout_api_comparison\setup.cmd
.\prototypes\layout_api_comparison\run.cmd hybrid
.\prototypes\layout_api_comparison\run.cmd explicit
```

Close one window and launch the other to compare them. No implementation edits
are needed. Double-clicking `run.cmd` starts hybrid; the launcher resolves the
repository from its own location. Keep the terminal open to see callback counts.
Both windows intentionally have the same title, size, theme and content.

Setup uses the project-local `.venv-qt-quick` and pinned `PySide6==6.11.2`. If the
environment is missing, it requires the Windows Python launcher with Python
3.13 (`py -3.13`) to create it. No global package installation occurs. The
existing-environment setup path was run; fresh environment creation and
double-click launch have not been tested.

The Python-only examples can also be launched directly:

```powershell
.\.venv-qt-quick\Scripts\python.exe prototypes\layout_api_comparison\hybrid.py
.\.venv-qt-quick\Scripts\python.exe prototypes\layout_api_comparison\explicit.py
```

The verified user launch commands are the `run.cmd` commands above; these direct
example entry points share the runtime but are not separate verification runs.

## Python authoring examples

Both examples use [content.py](content.py), which constructs ordinary `Label` and
`Button` instances and contains four separate Python callbacks. For example:

```python
self.save_button = Button("Save draft", on_click=self.save)
self.reset_button = Button("Reset draft", on_click=self.reset)
```

`save`, `reset`, `add` and `dynamic_action` increment independent counters and
update a status label. Reset is a named independent callback, not an instruction
to reset the verification counters. On the first Add click, the callback uses:

```python
self.dynamic = Button("Runtime action", on_click=self.dynamic_action)
self.target.add(self.dynamic)
```

Later Add clicks increment their counter without creating duplicates.

Hybrid ([hybrid.py](hybrid.py)):

```python
from api import Row, Window, run
from content import Screen

screen = Screen()
window = Window("Layout API comparison")
window.add(screen.heading)
window.add(screen.explanation)
window.add(Row(screen.save_button, screen.reset_button))
window.add(screen.long_label)
window.add(screen.add_button)
window.add(screen.status)
screen.target = window
run(window)
```

Explicit tree ([explicit.py](explicit.py)):

```python
from api import Column, Row, Window, run
from content import Screen

screen = Screen()
body = Column(
    screen.heading,
    screen.explanation,
    Row(screen.save_button, screen.reset_button),
    screen.long_label,
    screen.add_button,
    screen.status,
)
window = Window("Layout API comparison", body)
screen.target = body
run(window)
```

Application authors need neither QML nor bridge objects. Hybrid direct children
flow top-to-bottom strictly in insertion order. Runtime insertion is
`window.add(button)` in hybrid and `body.add(button)` in explicit. Both append
after the status label. There is no inference from widget type or label.

## Comparison and recommendation

| Concern | Hybrid/default flow | Explicit tree |
| --- | --- | --- |
| Readability | Sequential window additions make this small form easy to extend. | Nested declaration shows the entire layout in one place. |
| Explicitness | Root vertical direction is a documented default. | Root `Column` explicitly declares vertical direction. |
| Resizing | Same wrapped text, expanding controls and vertical scrolling. | Identical measured geometry at tested sizes. |
| Grouping | `Row` marks the local horizontal exception. | Root `Column` and nested `Row` show both directions. |
| Dynamic updates | Append through the window reference. | Keep a reference to the intended `Column` and append there. |

For this small form, recommend hybrid default flow with explicit containers as
an escape hatch. It avoids a root-container variable for runtime addition while
retaining visible grouping. Explicit trees make hierarchy easier to audit as
nesting grows. The recommendation concerns authoring clarity, not rendering
quality: both styles produced the same output. This is implementation analysis;
the owner must judge personal authoring preference before selecting a public API.

## Internal implementation and boundaries

`api.py` contains the experimental Python declarations. `runtime.py` adapts each
instance into an internal QObject and each container into a QAbstractListModel.
Instance IDs route callbacks independently. Insert-row notifications append only
the new delegate, preserving existing controls; status labels use a notifying
property. The probe confirms one existing button instance survives insertion.

The window supplies an implicit `ColumnLayout`. The explicit variant has one
extra authored `ColumnLayout`, without extra margins. Internal `RowLayout` and
`ColumnLayout` use 12 px spacing; content has 20 px window margins. Row children
share width, including at 300 px. Labels and button text wrap without line-count
elision. A `Flickable` with a vertical scrollbar handles content taller than the
window. Ordinary content uses layouts, not fixed coordinates. `Loader` details,
QML control files and object names stay internal.

This bounded API supports Window, Column, Row, Label, Button, append and label
text changes. It has no remove/reorder/reparent, grid, overlay, configurable
spacing, theme-switching API or general tree compiler. Each node belongs to one
tree; reuse/reparenting is unsupported. The examples intentionally do not imply
that appending to `Window` inserts into an explicitly authored inner `Column`.
For explicit layout, use the retained `body` reference. Below the 280 px minimum
width or 260 px minimum height the window will not shrink. Arbitrarily many row
children, translated text, custom fonts and larger DPI need separate checks.

## What Codex actually verified

Windows 11 build 26200 (`Windows-11-10.0.26200-SP0`), Python 3.13.9,
PySide6 6.11.2, Qt 6.11.2, project-local `.venv-qt-quick`.

On 2026-10-04, setup completed with the pinned dependencies already installed.
Both ordinary user commands above were launched through `cmd /c`, with the
console hidden and the Qt window visible. PowerShell observed each named window,
closed it using `Process.CloseMainWindow()`, and recorded exit code 0. This tests
normal startup/shutdown, not physical interaction.

```powershell
.\prototypes\layout_api_comparison\run.cmd hybrid --probe
.\prototypes\layout_api_comparison\run.cmd explicit --probe
```

Final visible synthetic runs each exited 0 with `RESULT failures=[]` and no QML
or callback errors. The QtTest probe verified initial rendering, seven initial
leaf controls, authored hierarchy, insertion order and grouped Row geometry;
distinct Save/Reset/Add/runtime callbacks; insertion after showing; idempotent
repeated Add; existing button identity; and interactions after narrowing.
Final counts were `save=3, reset=2, add=2, dynamic=3` in each variant.

The probe checked horizontal bounds, non-overlap and sufficient text height at
640×520 and 300×520. The longer label grew from 40 to 100 px high. At 280×260,
it scrolled to the runtime button and activated it successfully. That short
height case verifies synthetic scroll/activation, not a separately inspected
capture. JSON text and rectangles matched exactly between variants for initial,
normal-after-insertion and narrow-after-insertion states.

Four captured Qt window frames were visually inspected for matching output,
readability, wrapped text, grouped buttons, status and the inserted button:

| Style | Normal, 640×520 | Narrow, 300×520 | Probe details |
| --- | --- | --- | --- |
| Hybrid | [capture](evidence/hybrid-normal.png) | [capture](evidence/hybrid-narrow.png) | [JSON](evidence/hybrid-probe.json) |
| Explicit | [capture](evidence/explicit-normal.png) | [capture](evidence/explicit-narrow.png) | [JSON](evidence/explicit-probe.json) |

Development exposed a read-only Loader implicit-height assignment and then a
size binding cycle. An Item wrapper around the Loader fixed both. The final
runs above contain neither warning. These were prototype implementation issues.

## What the owner should check personally

1. Launch both normal commands, use Save and Reset, and observe their independent
   counts. Click Add, then Runtime action; repeated Add should keep one button.
2. Resize by dragging to narrow and short sizes. Read the full text, scroll with
   the physical wheel/scrollbar, and click the inserted button at the bottom.
3. Try Tab, Shift+Tab, Space and Enter. Decide whether focus visibility, ordering,
   mouse feedback and interaction feel suitable. Codex has not verified physical
   input, keyboard activation or screen-reader accessibility.
4. Compare the Python examples and choose whether implicit root flow or explicit
   hierarchy feels clearer, especially the different runtime insertion targets.

Other hardware, DPI/scaling, touch, fresh installation, packaging, prolonged
interaction, performance and other operating systems remain unverified. No
benchmark, broad platform support or final architecture choice is claimed.
