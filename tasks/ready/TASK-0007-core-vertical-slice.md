# TASK-0007: Build the first production Python UI vertical slice

**Status:** Ready
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

## Findings

Implementation has not started.
