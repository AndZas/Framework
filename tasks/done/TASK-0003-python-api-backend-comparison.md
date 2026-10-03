# TASK-0003: Python API backend comparison

**Status:** Done
**Type:** Experiment
**Depends on:** TASK-0002
**Likely files:** `prototypes/api_backend_comparison/`, this task's findings section

## Goal

Compare two ways to implement the same small Python-authored UI over Qt Quick:

1. Direct Python-created Qt Quick items, following `prototypes/python_api_spike/`.
2. A Python-authored declarative tree that is translated to or instantiated through internal QML components, without requiring the application author to write QML.

Find out which approach gives a simpler and more maintainable route to layouts, text, input, and custom shapes while preserving the concise Python-facing API. This is an experiment, not a backend decision.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `prototypes/python_api_spike/README.md`
- `prototypes/python_api_spike/api.py`
- `prototypes/python_api_spike/main.py`
- `tasks/done/TASK-0002-python-api-spike.md`

Read only the relevant files in `prototypes/qt_quick_spike/` if needed for comparison.

## Scope

Create a self-contained comparison under `prototypes/api_backend_comparison/`. Keep it out of the production package. Use the same or near-identical Python-facing example for both implementations; explain any unavoidable API differences.

Both variants should exercise:

1. A resizable window containing a short vertical layout with a text label, a rounded button, and a star-shaped control.
2. A Python callback from the button and star.
3. A theme change and one per-control style override.
4. A small property animation.
5. Layout response when the window is resized, plus usable text sizing/alignment.
6. Keyboard focus or key activation for the button, if practical; document accessibility and focus support that was not verified.

For the direct-item variant, reuse or adapt the `QQuickPaintedItem` approach from TASK-0002. For the QML-backed variant, generate or instantiate QML internally from Python data. The sample application author must not write QML in either variant.

Record a practical comparison of:

- Python-facing API clarity and amount of app-authored code.
- Backend implementation code needed to add or modify a control.
- Layout, text, input, theme and animation effort.
- Debugging, errors and mapping from a Python widget to its rendered Qt Quick object.
- Known performance or accessibility implications from APIs used; do not make benchmark claims without measurements.

Provide a README with setup/run instructions, the matched example, actual environment and results, limitations, and a recommendation. A small table of rough handwritten implementation line counts is acceptable if the counting method and included files are stated; do not optimize for line count alone.

## Out of scope

- Production framework code, API stabilization, or architecture adoption.
- General CSS parsing, broad theme language, a full layout engine, or a full widget library.
- Re-running the media and rendering stress experiments from TASK-0001.
- Android/Linux/macOS builds, multimedia, or GPU stress benchmarking.
- Custom C++ rendering, direct Vulkan, or broad input-device support.
- Changing the architecture overview to select a backend.

## Acceptance criteria

- Both variants run on the stated Windows environment and use the same Python-authored example to the extent practical.
- The window resize, text/layout, callbacks, theme update, animation, and custom star interaction are demonstrated or explicitly marked unverified.
- The application author writes no QML in either variant.
- README comparisons are based on observed implementation and verification, not assumptions alone.
- Findings are recorded below. Do not change the architecture overview to select a backend.

## Verification

Run both variants on Windows. Demonstrate their example and resize behavior. Record actual commands and environment. Do not claim accessibility, physical input, or performance behavior was verified unless it was actually checked.

## Report

Summarize which approach was easier for each tested concern, where implementation complexity moved, the API differences, unresolved risks, and the smallest useful next experiment. Recommendation is input for owner review only.

## Findings

Implemented the isolated comparison in `prototypes/api_backend_comparison/`: a shared Python `Window`/`Label`/`Button`/`Star` example and `Theme`/`Pulse` data in `model.py` and `main.py`, a direct `QQuickPaintedItem` backend in `direct.py`, and an internally generated QML backend with a Python `Bridge` in `qml_backend.py`. The sole app-authoring difference is the selected backend name. No application-authored QML, production-package code, or architecture decision was added. `README.md` contains setup, the matched example, implementation comparison, results, limitations and recommendation; four captures show initial and resized themed states.

**Platform and actual verification:** Windows 11 build 26200, Python 3.13.9, PySide6/Qt 6.11.2, existing `.venv-qt-quick`. From the repository root, `.\.venv-qt-quick\Scripts\python.exe prototypes\api_backend_comparison\main.py --backend direct --probe`, the same command with `--backend qml`, and corresponding `--capture` commands for both backends were run. The final sequential runs each exited with code 0. Both probes reported a visible window resized from 420×350 to 600×400, label width 372→552, centered star x 150→240, button and star callbacks once each from synthesized interior clicks, no callback from their tested empty corners, dark theme after button click, and a second button callback from synthesized Space restoring light theme. The orange per-control fill remained configured as `#d86642`. Button scale samples moved from about 1.00 to about 1.07, demonstrating active animation. The four Qt window grabs saved successfully and were visually inspected: text and alignment, rounded button, star, resize, dark surface and star color, and persistent orange override were visible.

**Comparison and recommendation:** QML `Column`/bindings/`Text` required less manual work for this layout and text; direct items made the Python object, shape path and input code easier to trace. Complexity in the direct backend is paint/layout/key and mouse code for each control. Complexity in the QML backend is an internal template, Python-to-QML property bridge, callback dispatch and object lookup; Canvas needed an explicit repaint on theme change. An initial capture exposed that missing repaint and the corrected capture showed the expected mint star. A combined screenshot/synthetic-click run and one direct-item corner click immediately after a theme-changing click hung and were stopped; separate capture runs and corner-before-theme probe runs completed. The cause was not diagnosed. Qt documents image/texture upload implications of both painted items and Canvas; no performance measurement was run. Physical input, accessibility, screen readers, focus visuals/order, DPI variation, long or translated text, small-window clipping, arbitrary or repeated child controls, cleanup, other platforms and error mapping remain unverified. The narrow fixed QML template is not a general tree translator. For owner review, internal QML is the more convenient layout/text direction in this small sample, while direct items remain simpler to trace. The smallest next experiment is adding a repeated dynamic control with a long label at two sizes to test callback identity, generated-object mapping, error reporting and layout growth. This recommendation is not a backend adoption.
