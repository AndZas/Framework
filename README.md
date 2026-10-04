# Framework

Personal Python UI framework project. The MVP targets Windows; Linux, macOS, and Android are future targets to evaluate.

The selected MVP foundation is **PySide6 + Qt Quick**, recorded in [ADR-0001](docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md). Python is the planned public authoring language, with Qt Quick/QML used internally for presentation and rendering. This establishes the foundation while leaving the public API and implementation plan open for design.

## Project map

- `AGENTS.md` — instructions for Codex working in this repository.
- `docs/architecture/overview.md` — current goals and architecture summary.
- `docs/architecture/decisions/` — decisions and recorded experiments.
- `docs/git-workflow.md` — branch, commit, push, and review workflow.
- `tasks/ready/` — tasks ready for an implementation chat.
- `tasks/in-progress/` — tasks currently being implemented.
- `tasks/done/` — completed task records.
- `prototypes/` — experiments that are not yet part of the framework.

The first experimental production slice lives in `src/pyui_framework/`.
`pyui_framework` / `pyui-framework` is a temporary internal name, to be replaced
before public release. Version 0.1.0 is an unstable development API; nothing is
published to PyPI. Experiments remain under `prototypes/`.

## Windows setup and launch

With Python 3.13 installed, run from the repository in PowerShell:

```powershell
.\setup.cmd
.\run.cmd
```

Setup creates the dedicated ignored `.venv-framework` and installs the editable
package with pinned development dependencies. It does not install globally.
`run.cmd` can also be double-clicked after setup. Close the window to exit.
Equivalent explicit commands:

```powershell
py -3.13 -m venv .venv-framework
.\.venv-framework\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv-framework\Scripts\python.exe examples\hello.py
```

The [example](examples/hello.py) uses only Python:

```python
from pyui_framework import App, Window, Label, Button, Row

window = Window("Hello")
window.add(Label("A Python UI", heading=True))
window.add(Row(Button("Save", on_click=lambda: print("save")),
               Button("Reset", on_click=lambda: print("reset"))))
raise SystemExit(App(window).run())
```

## Experimental API

| API | Behavior |
| --- | --- |
| `Window(title, *children, width=640, height=520)` | One window, vertical direct-child flow; minimum 280×260 |
| `Label(text, heading=False)` | Wrapped text; `heading` is keyword-only |
| `label.set_text(text)` | Update text, including from a callback |
| `Button(text, on_click=callable)` | Keyword-only zero-argument Python callback |
| `Row(*children)` | Horizontal group with equal available widths |
| `Column(*children)` | Vertical group in insertion order |
| `container.add(child)` | Append and return the child, before or after startup |
| `App(window).run()` | Show, block until closed, return exit status; one run per App |
| `App(window, theme="light")` / `app.set_theme(theme)` | Light, Dark, System or custom `Theme`; live appearance updates |
| `Theme(name="Custom", **tokens)` / `Theme.load(path)` | Equivalent Python and CSS-inspired file authoring |
| `Window/Label/Button(..., style={...})` / `widget.set_style(**tokens)` | Local override; replace or clear with an empty call |

Production theme API, grammar, ranges, precedence, System behavior and limits
are documented in [docs/themes.md](docs/themes.md). Run `./run-themes.cmd` after
setup to compare the themes, reload `examples/lagoon.theme` and replace/clear a
local Button override. The ordinary `run.cmd` remains the core example.

Children have one owner. Invalid types, duplicate ownership and cycles raise
Python errors. Use retained container references to append controls in callbacks.
Live `add` and `set_text` must run on the application thread. Direct changes to
other attributes after startup are unsupported. QML loading failures raise
`RuntimeError` with diagnostics; QML warnings and callback exceptions print to
stderr. Callback errors retain the Python traceback and private instance ID;
the UI remains open and returns status 1 when closed. Internal bridges and QML
are not public exports. Qt Quick Controls provides button focus and keyboard
activation, with a visible focus border. Content scrolls vertically when needed.
Use the mouse wheel or scrollbar to scroll. Dragging the content with a mouse
button is disabled so that Flickable does not consume action clicks during
scroll movement. Dragging the scrollbar thumb still works.
Synthetic checks confirmed Tab/Shift+Tab and Space. Enter did not activate the
selected Qt Quick Controls button; use Space for keyboard activation in this slice.

## Verification and local wheel

```powershell
.\.venv-framework\Scripts\python.exe -m pytest -q
.\.venv-framework\Scripts\python.exe tests\qt_probe.py evidence\TASK-0007\editable
.\.venv-framework\Scripts\python.exe tests\scroll_click_probe.py --route wheel --output evidence\TASK-0007\rapid-clicks\wheel.json
.\.venv-framework\Scripts\python.exe -m build --wheel
py -3.13 -m venv .venv-framework-wheel
.\.venv-framework-wheel\Scripts\python.exe -m pip install dist\pyui_framework-0.1.0-py3-none-any.whl
```

The suite launches real visible Qt windows and uses synthetic QtTest input.
The standalone probe saves normal/narrow captures, geometry and environment
evidence. The rapid-click probe sends actual wheel/scrollbar input and immediately
checks a stationary-pointer burst of ten paired presses/releases; `--route`
also accepts `scrollbar` and `drag` (the latter verifies mouse content dragging
is disabled). It records input, button signals and viewport movement in JSON.
For the wheel check, copy `examples/hello.py` and `tests/qt_probe.py`
to a directory outside this checkout, change to that directory and run them
with the absolute path to `.venv-framework-wheel\Scripts\python.exe`. The
installed package must resolve QML from that environment's `site-packages`.
The runtime dependency is PySide6 6.11.2; pytest/build/setuptools belong to the
optional development extra. A wheel includes all seven internal QML files.

## Owner checks and limits

Run the ordinary example, click Save/Reset independently, click Add a live
action and activate the appended button. Drag the window narrower and shorter;
inspect wrapping and scroll using the wheel/scrollbar. Try physical Tab,
Shift+Tab, Space and Enter and inspect the focus border. Assess readability and
appearance on your own display. Synthetic checks do not establish physical
input usability, accessibility, screen-reader support, DPI/hardware coverage
or prolonged-operation behavior.

Only Windows is verified. Rows keep a horizontal grouping rather than becoming
vertical; arbitrarily large rows and extremely long unbroken text are outside
the tested cases. Light/Dark/System and a validated semantic styling API are
available; there is no remove/reorder/reparent, multiple windows, worker-thread UI updates, executable
packaging or platform support beyond this Windows slice. Each Repeater eagerly
creates its children; no large-list performance claim is made.

## Current status

See [the architecture overview](docs/architecture/overview.md), accepted [ADR-0001](docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md), [ADR-0002](docs/architecture/decisions/ADR-0002-layout-defaults.md), and [ADR-0003](docs/architecture/decisions/ADR-0003-theme-model.md). [TASK-0010](tasks/in-progress/TASK-0010-production-themes.md) implements the production theme runtime; owner review is pending. Completed evidence: [Qt Quick feasibility](tasks/done/TASK-0001-qt-quick-feasibility.md), [Python-first API](tasks/done/TASK-0002-python-api-spike.md), [Python API backend comparison](tasks/done/TASK-0003-python-api-backend-comparison.md), [QML controls and dynamic Python tree](tasks/done/TASK-0004-qml-controls-dynamic-tree.md), [interactive showcase](tasks/done/TASK-0005-interactive-qt-quick-showcase.md), [layout API comparison](tasks/done/TASK-0006-layout-api-comparison.md), [first production Python UI slice](tasks/done/TASK-0007-core-vertical-slice.md), [hybrid theme authoring prototype](tasks/done/TASK-0008-theme-api-spike.md), and [scrollbar edge layout](tasks/done/TASK-0009-scrollbar-edge-layout.md).
