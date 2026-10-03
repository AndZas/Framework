# TASK-0002: Python-first API feasibility spike

**Status:** Done
**Type:** Experiment
**Depends on:** TASK-0001 (completed)
**Likely files:** `prototypes/python_api_spike/`, this task's findings section

## Goal

Determine whether a small, understandable Python-only public API can drive a Qt Quick interface without requiring the application author to write or read QML for the tested scenarios.

This is a contained API experiment. It does not select Qt Quick as the production backend and does not define a stable public API.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `prototypes/qt_quick_spike/README.md`
- `tasks/done/TASK-0001-qt-quick-feasibility.md`

Inspect only relevant parts of `prototypes/qt_quick_spike/` to reuse lessons. Keep TASK-0001 unchanged unless the user explicitly asks to revise it.

## Scope

Create an isolated runnable prototype under `prototypes/python_api_spike/`. Use PySide6/Qt Quick internally, with all app-authored interface construction and callbacks expressed in Python. Internal/generated QML is allowed, but it must not be necessary for the prototype user to write QML.

Exercise this illustrative API shape (refine names if needed, and explain meaningful deviations):

```python
app = App(theme=Theme(...))
window = Window(title="API spike")
window.add(
    Button("Click me", on_click=handle_click)
)
app.run()
```

The prototype should include:

1. A basic rounded button created from Python, with a Python click callback.
2. A custom star-shaped control with gradient fill and an explicit hit-test result. Reuse the same shape description for drawing and hit testing if feasible; record any duplication or constraints.
3. A runtime theme change and one per-control style override, controlled from Python.
4. A short animation controlled from Python configuration.
5. Two independently created windows, if this can be expressed cleanly by the proposed API.
6. A minimal theme input/representation that keeps the public authoring surface Python-only. Do not build a general CSS parser or full theme language here. Explain the smallest practical path to a CSS-inspired theme format and its likely boundary.
7. A short README with setup, run instructions, example app code, implementation notes, and observed friction (boilerplate, binding/lifecycle issues, QML leakage, debugging difficulty, or awkward API choices).

Reuse the existing local media asset or helper only if it does not significantly complicate this API-focused experiment. Multimedia and performance were already probed in TASK-0001 and are not acceptance requirements here.

## Out of scope

- Moving code into the production package or promising API stability.
- Full widget library, layout inference engine, or general CSS/theme parser.
- Re-running the media and rendering stress experiments from TASK-0001.
- Android, Linux, macOS packaging or porting.
- Custom C++ rendering, direct Vulkan, or broad input/device integrations.
- Changing the architecture overview to mark Qt adopted.

## Acceptance criteria

- The prototype launches on the stated Windows environment using the Python-only app example.
- The application author does not need to author QML to create the tested windows, controls, theme, animation, or callbacks.
- Button callbacks and the tested theme change work at runtime.
- The star's visible and interactive areas are exercised and the hit-test behavior is recorded.
- Any QML generation/bridge design and its maintainability tradeoffs are documented.
- The report separates demonstrated behavior from reasoned-but-unverified platform claims.
- The recommendation says whether the Python-first surface appears practical, what felt awkward, and what next API experiment would answer remaining questions. It is evidence for owner review, not an architecture decision.

## Verification

Run the prototype on Windows. Demonstrate the example, callback, theme change, star hit test, and animation. Exercise two windows if implemented. Record actual commands and environment; do not claim tests or platform behaviors that were not run.

## Report

Summarize files created, exact environment, example API, how Python state reaches the Qt Quick scene, scenario results, extra implementation required, usability friction, and remaining unknowns. Add findings below.

## Findings

Implemented `prototypes/python_api_spike/api.py`, `main.py`, pinned `requirements.txt`, `.gitignore`, `README.md`, and two probe captures. The runnable application authoring code in `main.py` uses `App`, `Theme`, `Window`, `Button`, `Star`, and `Pulse` entirely from Python. Explicit `app.add(window)` registers each independent window, a small deviation from the illustrative API. Nothing was moved into the framework package and no architecture decision was made.

**Actual environment and command:** Windows 11 build 26200; Python 3.13.9; PySide6/Qt 6.11.2; NVIDIA GeForce RTX 5060 Ti, driver 32.0.15.9636. The existing `.venv-qt-quick` was reused. `.\.venv-qt-quick\Scripts\python.exe prototypes\python_api_spike\main.py --probe` was run three times: the first completed, an attempt to capture immediately after synthetic clicks hung and was stopped, and the final delayed-capture run exited with code 0. `Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion` collected GPU details. No non-Qt runtime dependency was used. The interactive command without `--probe` was not run separately.

**Demonstrated on this Windows run:** Two distinct windows reported visible. A synthesized center click invoked the rounded button's Python callback once; an empty rounded corner did not increase the count. The theme callback changed the app to dark, while the orange per-control fill stayed `#d86642`. A synthesized star-interior click invoked its Python callback once; an empty corner did not increase the count. Light and dark captures were saved and visually inspected. A Python-configured `QPropertyAnimation` changed button scale (observed `1.029` and `1.032` at two samples in the final run). The star uses one `QPainterPath` for visible fill and `contains()` hit testing. Anti-aliased edges and stroke pixels were not tested for exact matching.

**Implementation and limits:** Python directly creates `QQuickWindow` and custom `QQuickPaintedItem` controls. Python callbacks are invoked by item mouse handlers; Python theme state calls window background updates and control `update()`; animation targets the Qt Quick item property. There is no generated QML or QML bridge in this variant, so the author writes no QML. The small `Theme` dataclass is the only theme input. An optional CSS-inspired token layer could map a few named colors into it; cascading/selectors would require a separate experiment. Explicit ownership, fixed placement, custom drawing/input for basic controls, and the Qt-specific painted-item internals were awkward. Performance, physical input, touch, keyboard focus, accessibility, richer layout, packaging, and other platforms remain unverified. Full results and setup guidance are in `prototypes/python_api_spike/README.md`.

**Recommendation:** The Python-first surface appears practical for the tested small scenarios. Compare this direct-item approach with a minimal generated-QML bridge using the same example to learn which gives more maintainable layout, text, and debugging. This is evidence for owner review, not adoption of Qt Quick.
