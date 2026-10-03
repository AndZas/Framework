# TASK-0007: Build the first production Python UI vertical slice

**Status:** Implementation complete; owner review pending
**Type:** Implementation
**Depends on:** ADR-0001, ADR-0002, TASK-0004, TASK-0006
**Likely files:** `pyproject.toml`, `src/pyui_framework/`, `examples/`, `tests/`, `README.md`
**Branch:** `task/TASK-0007-core-vertical-slice`

## Goal

Turn the proven Qt Quick approach into the first small, installable part of the actual Python framework. A user should be able to write a Python-only example with one window, text, buttons, callbacks, and the accepted default-flow layout, then run it without importing or editing QML.

Use `pyui_framework` as a **temporary internal import name** for this task. Do not publish it, claim the name is final, or expand the task into branding. Record the temporary name in package documentation so it can be replaced before a public release.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/architecture/decisions/ADR-0002-layout-defaults.md`
- `docs/git-workflow.md`
- `tasks/done/TASK-0002-python-api-spike.md`
- `tasks/done/TASK-0003-python-api-backend-comparison.md`
- `tasks/done/TASK-0004-qml-controls-dynamic-tree.md`
- `tasks/done/TASK-0006-layout-api-comparison.md`
- Relevant code in `prototypes/layout_api_comparison/` and `prototypes/qml_tree_spike/`

## Scope

- Create a standard `src/`-layout Python package named `pyui_framework` with `pyproject.toml` metadata, a local development install path, and a concise Python-only example under `examples/`.
- Implement a small public surface for `App`, `Window`, `Label`, `Button`, `Row`, and `Column`. Exact signatures may be chosen during implementation, but document them and keep this first API explicitly version `0.x`/experimental.
- Use the layout policy from ADR-0002: direct window children flow vertically in insertion order; `Column` flows vertically; `Row` groups children horizontally. Keep sizing and wrapping responsive; do not use absolute coordinates for ordinary content.
- Render through PySide6 + Qt Quick. Keep QML, QObject bridges, generated IDs, callback routing, and Qt lifecycle details private to the package.
- Support a Python `on_click` callback per button, multiple independent buttons, and adding a button to a live window/container after startup.
- Provide a single polished built-in control appearance using internal style tokens. Do not implement public theme switching, CSS parsing, per-control theme overrides, custom shapes, or animation timelines in this task.
- Include clear Python-side error reporting for invalid child types, duplicate/invalid ownership where applicable, callback exceptions, and QML load failures. Do not silently swallow exceptions.
- Ensure package data includes all internal QML and resource files. Build a wheel and verify an installed example can launch from outside the repository root, so success does not depend on loading QML from the checkout.
- Add focused unit and Qt integration/smoke checks for the supported API. Keep tests local and deterministic; use QtTest synthetic input where appropriate and report any visible/manual checks separately.
- Document setup, the temporary package name, the Python example, supported API, test/run commands, and current limitations.

## Out of scope

- Declaring the `pyui_framework` package name permanent or publishing it to PyPI.
- A comprehensive or stable 1.0 public API, large widget catalog, or production accessibility claim.
- Theme switching/CSS-like theme files, animation timelines, custom vector/image fills, media, multiple top-level windows, gamepad input, or device capture.
- A custom renderer or changes to the Qt Quick foundation.
- Android/Linux/macOS support, executable packaging, performance benchmarking, or broad distribution setup.

## Acceptance criteria

- `pip install -e .` (or the documented local development install) works in a dedicated environment and does not alter global Python packages.
- The Python-only example launches a visible Qt Quick window containing text, a button, and a horizontal `Row` inside the vertical default flow.
- Clicking each button calls only its own Python callback. At least one control can be appended after the window is shown and then activated.
- Resizing the window changes the available layout width; text wraps and controls remain usable without unintended overlap or clipping at the tested sizes.
- Basic focus and keyboard activation work for buttons where supported by Qt Quick Controls; report any remaining limitations.
- A built wheel installs into a clean project-local test environment and launches the example from a directory outside the source checkout with its QML resources resolved.
- Automated checks cover core model/layout behavior and the Qt interaction path. The report identifies exactly which tests and visible runs passed; do not claim unrun cases.
- QML is not imported or authored by the example application, and implementation-specific bridge objects are not part of the public exports.
- The package/API remain clearly marked as an initial `0.x` development slice; no architecture change is made.

## Verification

- Use Windows and a dedicated ignored environment such as `.venv-framework`; do not install packages globally or reuse an unrelated application environment.
- Pin the initial PySide6 runtime dependency to the verified Qt 6.11.2 line and keep development/test dependencies separate from the runtime dependency.
- Install the project's pinned development dependencies, run the focused test suite, build a wheel, install it into a clean local environment, and launch the installed example from outside the repository.
- Exercise callbacks, runtime insertion, resize/wrapping, and keyboard activation with reliable synthetic input. Also report any manual visible launch or physical-input checks separately.
- Record Python, PySide6, Qt, Windows versions, exact commands, package/wheel contents relevant to QML, test results, and remaining limitations.

## Report

- Package files and the public Python example/API.
- Local installation, test, wheel-build, and installed-example launch commands.
- Verification results and evidence, including environment and QML resource resolution.
- Any API friction, architecture deviations, limitations, or unverified behavior.
- Task branch and commit ID(s). Leave the task in progress for owner review.

## Owner review feedback: rapid clicks after scrolling

**Status:** Reproduction and fix required before owner approval.

On 2026-10-04, the owner manually launched the example and found an interaction
issue after scrolling a short window to reveal a button. With the pointer kept
over the newly visible button, a rapid series of left-button clicks did not
activate it while the series continued. After pausing/releasing the mouse button
and starting to click again, the button began working. Other reported visual,
resize, scroll, and button behavior looked correct. The exact scroll input
(wheel, scrollbar, or dragging the content) has not yet been recorded. This is
an owner-observed issue, not a confirmed Qt defect; the double-click hypothesis
is also unconfirmed.

The current automated probe changes `Flickable.contentY` directly, waits between
actions, then sends isolated synthetic clicks. It does not cover a real scroll
gesture followed immediately by a burst of clicks, so its passing short-scroll
check does not resolve this report.

### Required follow-up before approval

- Reproduce the report on Windows and record the scroll method, pointer position,
  button press/release pattern, `clicked` callback count, and whether the view
  is still moving/flicking. Check each supported scroll route (wheel, scrollbar,
  and content dragging) where practical.
- Inspect the Qt Quick event path around `Flickable` and `Button`. Instrument
  relevant button press/release/cancel/click/double-click signals and view
  movement state as needed. Identify the cause before changing behavior; do not
  assume that double-click recognition is responsible.
- Add a deterministic regression test that scrolls a control into view and
  immediately sends repeated press/release clicks without an idle pause. Verify
  every intended click reaches that button's Python callback and no neighboring
  callback fires. Keep the test representative of the input route that reproduces
  the issue; report any owner-only physical check separately.
- Fix the event handling at its source. Do not hide missed clicks with callback
  throttling, arbitrary delays, or double-click-specific workarounds.
- Rerun the focused suite and installed-wheel smoke check if package/QML behavior
  changes. Update this report with the root cause, fix, exact checks, results,
  and any route that remains unverified. Keep TASK-0007 in progress until the
  owner confirms the fix.

## Findings

Implemented the initial 0.1.0 production slice with the temporary internal
`pyui_framework` import name. `pyproject.toml` defines a src-layout package,
PySide6 6.11.2 runtime and separately pinned pytest/build/setuptools development
extra. `src/pyui_framework/` exposes only App, Window, Label, Button, Row and
Column. The private Python model validates types, dimensions, single ownership
and cycles, including rollback after invalid container construction. Its Qt
adapter uses per-instance IDs, QObject properties and QAbstractListModel insert
notifications; seven packaged QML files implement reusable controls, vertical
default flow, horizontal rows, nested columns and one internal-token appearance.
This task explicitly adopts the bounded layout/runtime lessons of the prototypes
into the package; prototype files were not modified. No architecture deviation.

`examples/hello.py` is Python-only. It has separate Save/Reset counters, a status
label updated by callbacks and an Add action appending a button into a retained
Column after startup. `setup.cmd` and `run.cmd` prepare and launch it. README
documents signatures, return/error policy, setup, wheel commands and limitations.
`tests/test_model.py`, `tests/test_qt.py` and `tests/qt_probe.py` provide focused
model, actual-example, visible interaction and error-path verification.

### User launch

From `F:\Files\PythonProjects\Framework` in PowerShell:

```powershell
.\setup.cmd
.\run.cmd
```

Setup needs installed Python 3.13 and creates `.venv-framework`; no global pip
install is used. It can be rerun. Close the example window to exit. Double-click
launch is supported by the scripts but was not physically tested.

### What Codex confirmed on 2026-10-04

Environment: Windows 11 build 26200 (`Windows-11-10.0.26200-SP0`), Python 3.13.9
(MSC v.1944, AMD64), PySide6 6.11.2, Qt 6.11.2. Both dedicated environments were
created during this task, without reusing the prototype environment.

Commands actually run from repository root:

```powershell
py -3.13 -m venv .venv-framework
.\.venv-framework\Scripts\python.exe -m pip install -e ".[dev]"
.\setup.cmd
.\run.cmd
.\.venv-framework\Scripts\python.exe -m pytest -q
.\.venv-framework\Scripts\python.exe tests\qt_probe.py evidence\TASK-0007\editable
.\.venv-framework\Scripts\python.exe -m build --wheel
py -3.13 -m venv .venv-framework-wheel
.\.venv-framework-wheel\Scripts\python.exe -m pip install dist\pyui_framework-0.1.0-py3-none-any.whl
```

The ordinary `run.cmd` was launched through a hidden cmd process. PowerShell
confirmed the visible Qt window title `Python UI — first core slice` and a
nonzero native window handle, closed it with `Process.CloseMainWindow()`, and
observed launcher exit 0. This was a normal launch, without physical input.

The final test suite reported **6 passed in 4.28 s**. It covers insertion order,
invalid children/callback/text/dimensions, duplicate ownership, cycles and failed
construction rollback; independent synthetic mouse clicks; live insertion and
preservation of an existing visual instance; wrapping and geometry at 640×520
and 300×520; scrolling to a live button at 280×260; synthetic Tab/Shift+Tab focus
and Space activation; exception traceback plus nonzero app exit; and QML load
failure diagnostics. The actual `hello.py` construction and synthetic clicks
on Save, Reset, Add and the appended button produced the status
`save: 1 · reset: 1 · added: 1`, verifying live text notification too.

The standalone editable and wheel probes exited 0 with `RESULT []`, empty QML
error lists and independent final counters `[2, 2, 2]`. The long label grew from
40 px to 100 px when narrowed. Geometry checks found no leaf overlap, horizontal
overflow or insufficient leaf height in the tested layouts. Enter was explicitly
sent and **did not activate** the selected Qt Quick Controls Button; Space is
the confirmed keyboard activation key. No public keyboard customization was
added. Normal/narrow captures from both environments were visually inspected:
readable text, horizontal grouped actions and live button, no visible clipping.

Initial checks found a QML token name beginning with `on` that Qt interpreted
as a signal handler, and the test harness initially scheduled a timer before
creating QGuiApplication. Both were fixed before final checks. A null-node
guard was added to the Loader source binding to eliminate a teardown warning.
These are implementation/harness issues, not Qt foundation blockers.

### Installed wheel outside the checkout

The wheel was built in an isolated build environment and installed into the
clean `.venv-framework-wheel`, with only the runtime dependency. After a final
model validation improvement it was rebuilt and updated with:

```powershell
.\.venv-framework-wheel\Scripts\python.exe -m pip install --force-reinstall --no-deps dist\pyui_framework-0.1.0-py3-none-any.whl
$external = Join-Path $env:TEMP 'framework-TASK-0007-wheel'
New-Item -ItemType Directory -Force $external
Copy-Item examples\hello.py,tests\qt_probe.py $external
Set-Location $external
& 'F:\Files\PythonProjects\Framework\.venv-framework-wheel\Scripts\python.exe' qt_probe.py 'F:\Files\PythonProjects\Framework\evidence\TASK-0007\wheel'
& 'F:\Files\PythonProjects\Framework\.venv-framework-wheel\Scripts\python.exe' hello.py
```

Actual external directory was
`C:\Users\zasim\AppData\Local\Temp\framework-TASK-0007-wheel`. The ordinary
installed example was started with PowerShell Start-Process, hidden console,
redirected stdout/stderr and that working directory. Its visible Qt window
was confirmed by title/handle, closed using CloseMainWindow, and exited 0 with
empty stderr. The venv launcher delegates to a child Python process, so native
window inspection used the process owning the matching window title.

The external probe records the import path
`F:\Files\PythonProjects\Framework\.venv-framework-wheel\Lib\site-packages\pyui_framework\__init__.py`.
It needs no checkout QML or PYTHONPATH. Wheel archive inspection confirmed the
four Python modules and all seven QML resources: Main, NodeView, ButtonControl,
LabelControl, ColumnControl, RowControl and Style. No prototype imports exist.
`evidence/TASK-0007/wheel-contents.json` records the archive contents and SHA256
`8653c45234aa247a16448a5616d21c9ec2f491b22dff2efc3b187ecbdbf86ea7`.
Wheel/environment/build outputs remain ignored and are not committed.

Evidence: `evidence/TASK-0007/editable/` and `wheel/` each contain `probe.json`,
`normal.png` and `narrow.png`; `wheel-launch.json` records the ordinary installed
launch. `git diff --check` passed. No physical-input verification is claimed.

### What the owner must check personally

Run setup/run on your own configuration; physically click Save and Reset and
check independent counters; add and activate the live action; drag to narrow
and short sizes; use wheel/scrollbar; try Tab, Shift+Tab and Space while checking
the focus border. Enter currently does not activate the button. Judge the
appearance, readability and convenience of the Python API on your display.

Physical mouse/keyboard, screen readers/accessibility, touch, different DPI,
graphics hardware, prolonged use, performance, double-click launch and other
platforms were not verified. API is experimental 0.x; one window, one appearance,
append-only containers, no remove/reorder/reparent or worker-thread UI updates.
Rows stay horizontal and divide width equally; arbitrarily large rows and long
unbroken text were not tested. Repeaters instantiate all children eagerly.
QML diagnostics include resource URLs/lines but no Python source-line mapping.
Callbacks report tracebacks and retain error status while the window stays open.
No public theming, stable package naming, executable packaging or publishing.

### Git and review

Continued the existing `task/TASK-0007-core-vertical-slice` branch; the requested
`certical` spelling did not exist and was treated as a typo. The task was moved
from ready to in-progress at startup and remains here for owner review. No merge,
release, repository-setting change or push to main. Implementation commit:
`0bac796f37e6a2b6ccb95aab15047f819b266aba`. This report follow-up is a separate
commit; both are pushed to origin on the task branch. No uncommitted task work
remains. Owner review and architecture-chat merge are pending.
