# TASK-0004: QML controls and dynamic Python tree

**Status:** Done
**Type:** Experiment
**Depends on:** TASK-0003
**Likely files:** `prototypes/qml_tree_spike/`, this task's findings section

## Goal

Validate a production-shaped vertical slice for the leading candidate architecture: a Python-authored UI tree backed by reusable native Qt Quick QML controls. Focus on the untested risks exposed by TASK-0003: repeated/dynamic widgets, stable callback identity, reusable controls, responsive layout and text, and the native Qt Quick Shapes path.

This is the final targeted architecture experiment before deciding whether to adopt Qt Quick for the MVP. It must remain isolated from the production package.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `prototypes/api_backend_comparison/README.md`
- `prototypes/api_backend_comparison/model.py`
- `prototypes/api_backend_comparison/main.py`
- `prototypes/api_backend_comparison/qml_backend.py`
- `tasks/done/TASK-0003-python-api-backend-comparison.md`

Read other prototype files only when needed. Preserve completed task records.

## Scope

Create a self-contained prototype under `prototypes/qml_tree_spike/`. Keep application authoring in Python; QML may be packaged internally as reusable controls/components. Do not build a general-purpose compiler or move code into the framework package.

The example should demonstrate:

1. Reusable rounded buttons based on Qt Quick Controls (or its Templates), with custom theme styling and Python callbacks.
2. A reusable star control built with Qt Quick Shapes/ShapePath rather than QQuickPaintedItem or Canvas, with gradient fill and a documented hit test.
3. A Python-authored tree that creates at least three controls of the same type with distinct stable IDs and callbacks. Verify that each control calls its own callback; no lookup keyed only by widget type.
4. Adding and removing a control after the window is shown, or document a concrete limitation if this cannot be made reliable.
5. Resizing across at least two useful window sizes, including a narrower size and a long label. Show how the layout and text respond (wrap, elide, or minimum-width behavior).
6. Runtime theme change, a per-control override, and a short property animation using the same Python-facing configuration across the example.
7. A small repeated-control display (at least 50 controls) to observe interaction and rendering behavior. Record actual observations; do not claim a benchmark or smoothness guarantee based only on swap callbacks or screenshots.

Use an explicit data model / stable identifier for control instances. Keep the same public Python example independent of QML object names and generated source locations as far as practical. Record how errors in internal QML are reported to the Python author.

Provide a README with setup/run instructions, the Python-only example, implementation structure, observed results, API friction, limitations, and a recommendation about whether the approach is ready for an MVP architecture decision.

## Out of scope

- Shipping the framework, promising a stable API, or expanding to a full widget library.
- A general CSS parser, broad layout inference engine, or all arbitrary SVG/shape features.
- Android/Linux/macOS builds, multimedia, gamepads/HID, or global input capture.
- Writing a custom C++ renderer, direct Vulkan rendering, or implementing a second backend.
- Changing the architecture overview to declare the backend adopted. Report evidence for owner review only.

## Acceptance criteria

- The prototype launches on the stated Windows environment and all example widgets are created through the Python-facing tree.
- Three same-type controls invoke distinct callbacks, including after dynamic add/remove operations if implemented.
- The reusable button and star render with the selected Qt Quick Controls/Shapes types; no QQuickPaintedItem or Canvas is used for those controls.
- Theme, per-control override, animation, narrow/long-text behavior, and resizing are demonstrated or explicitly marked unverified.
- The repeated-control scenario is exercised and observations are accurately qualified.
- README records exact environment, commands, actual verification, implementation costs, and remaining unknowns.
- Findings are added below; no final architecture decision is made by the implementation chat.

## Verification

Run on Windows. Exercise callbacks, theme switching, shape interaction, resizing, long text, animation, and dynamic controls. Include screenshots or logs as evidence. If any behavior is not verified, label it clearly. Do not treat `frameSwapped` timing as display FPS or a benchmark.

## Report

Summarize whether the QML-backed Python tree handled dynamic identity, reusable controls, layout/text, theme and custom shapes cleanly; where QML complexity surfaced; what the 50-control scenario showed; and any remaining blocker to adopting Qt Quick for the MVP. Keep the recommendation evidence-based and owner-reviewed.

## Findings

Implemented the isolated `prototypes/qml_tree_spike/` vertical slice. The public example is Python `Window`/`Control`/`Theme`/`Pulse` data with stable instance IDs. A `QAbstractListModel` and row notifications create/remove QML delegates. Three initial buttons have distinct callbacks; a fourth control is a Qt Quick Shapes star. The reusable button uses Qt Quick Controls `Button` with the Basic style. The star uses `Shape`/`ShapePath`/`PathLine` with `LinearGradient` and a point-in-polygon hit test using the same vertices. No Canvas, QQuickPaintedItem, production-package code, or backend decision was added. Internal QML warnings report file URL and line; callback errors report the Python control ID. Python-source-to-QML-line attribution remains unavailable.

**Platform and actual verification:** Windows 11 build 26200, Python 3.13.9, PySide6/Qt 6.11.2, existing `.venv-qt-quick`. From repository root, `.\.venv-qt-quick\Scripts\python.exe prototypes\qml_tree_spike\main.py --probe` was run. The final run exited 0 with `RESULT failures=[]` and no QML warnings. It showed a 600×460 window; synthetic QtTest clicks invoked each of the three button callbacks and the star callback once, while the tested star empty corner did not activate. The theme changed to dark, the orange override remained configured, and two sampled scale values differed while the animation ran. Resizing to 300×500 yielded a 268-pixel button width. The saved and visually inspected `initial.png` and `narrow.png` show the long label wrapping to two lines, changed theme colors, orange override, gradient star, and narrow layout. A control added after show invoked its own callback; after its removal an existing button still invoked its own callback. Appending 50 buttons gave 54 controls total; synthetic clicks on the first and last repeated buttons invoked their distinct callbacks. `repeated.png` shows the scrolled list end. These are short-run synthetic interactions and window captures, not physical-input, accessibility, or performance tests.

**Recommendation for owner review:** The QML-backed Python tree handled dynamic identity, reusable controls, responsive text/layout, theme, override, animation, and the tested shape interaction cleanly in this bounded slice. Complexity surfaced in model roles/notifications, Loader delegates, bridge properties, a required customizable Controls style, QML error attribution, and capture/lifetime handling. The 50-control case established successful creation, rendering and sampled interaction, but no smoothness or scalability guarantee; its `Repeater` eagerly creates every control. No blocker appeared for an MVP architecture decision based on this slice, but accessible behavior, physical input, DPI variation, large-list performance, packaging, and other platforms remain unverified. Qt Quick remains a candidate pending owner review.
