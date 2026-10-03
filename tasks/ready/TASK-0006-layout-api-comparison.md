# TASK-0006: Compare default flow layout with explicit containers

**Status:** Ready  
**Type:** Experiment  
**Depends on:** TASK-0004, ADR-0001  
**Likely files:** `prototypes/layout_api_comparison/`, this task's findings section  
**Branch:** `task/TASK-0006-layout-api-comparison`

## Goal

Build a small runnable Windows prototype that lets the owner compare two Python API styles over the same Qt Quick presentation:

1. **Hybrid/default flow hypothesis:** direct children added to a window are laid out top-to-bottom in insertion order; explicit `Row` and `Column` containers group items when the author wants a different structure.
2. **Explicit tree:** the author expresses the whole layout through explicit `Column` and `Row` containers.

The purpose is to evaluate authoring clarity and visible behavior before adopting either layout style in the production Python API. “Automatic” means this deterministic default flow rule; do not infer arbitrary positions from labels or widget types.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/git-workflow.md`
- `tasks/done/TASK-0002-python-api-spike.md`
- `tasks/done/TASK-0003-python-api-backend-comparison.md`
- `tasks/done/TASK-0004-qml-controls-dynamic-tree.md`
- `prototypes/qml_tree_spike/README.md` and relevant source

## Scope

- Create the isolated prototype under `prototypes/layout_api_comparison/`; do not add this experiment to a production package.
- Provide two concise Python-only app-author examples, one per layout style. App authors must not write or inspect QML to use either example.
- Render equivalent screens with the same Qt Quick controls, theme, window size, spacing, and behavior so layout API is the main variable.
- Include direct sequential children and at least one explicitly grouped `Row` in the hybrid example. The explicit-tree example should express the corresponding complete hierarchy with `Column`/`Row`.
- Include a practical screen with a heading, explanatory text, multiple buttons with independent callbacks, a longer label, and one control added at runtime. If dynamic insertion differs between styles, show the difference in the examples and document it.
- Let the owner switch between the examples in the running prototype, or provide equally simple launch commands for each. Both must support resizing.
- Use Qt Quick layout primitives internally; avoid fixed-position coordinates for ordinary content.
- Add a README with environment setup, run instructions, the two Python examples, known limitations, and a concise comparison table covering readability, explicitness, resizing, grouping, and dynamic updates.
- Capture both layouts at a normal size and a narrow size for visual comparison.
- Record a recommendation, but leave the layout API decision to the owner. Keep the examples clearly marked as experimental.

## Out of scope

- Implementing the production package or a general-purpose layout engine.
- Inferring layout semantics from widget labels, types, or visual content.
- Building a full constraint solver, CSS engine, grid, overlay, or absolute-positioning API.
- Performance benchmarking or cross-platform builds.
- Selecting the final public API without the owner's review.

## Acceptance criteria

- Both styles are runnable and present equivalent content and behavior through the same Qt Quick backend.
- The hybrid style visibly demonstrates direct children flowing top-to-bottom and an explicit `Row` grouping.
- The explicit-tree style visibly demonstrates the same content using an explicitly authored root and nested containers.
- Resizing to a narrow window keeps content usable without overlap or clipping; report any remaining limitations.
- Buttons call their distinct Python callbacks. The runtime-added control works and its behavior is described for both styles.
- The owner can switch between or separately launch the two examples without editing implementation internals.
- Python examples stay free of QML and bridge details; those stay inside the prototype implementation.
- The task report compares the authoring experience, visible results, tradeoffs, verification, and recommendation without claiming broad performance or platform support.

## Verification

- Run both variants on Windows using the pinned project-local dependency setup; do not install packages into global Python.
- Verify initial rendering, independent button callbacks, runtime insertion, and narrow-window resizing in each variant through a visible run and reliable synthetic interaction where available.
- Capture normal and narrow layouts for both variants; inspect the captures for parity, readability, and layout failures.
- Record Python/PySide6/Qt versions, commands, and any unverified physical-input or hardware cases.

## Report

- Prototype files and commands to launch each layout style.
- The two Python authoring examples and a concise comparison table.
- Verification performed, evidence/capture paths, environment, and limitations.
- Recommendation for owner review; do not declare the final API decision.
- Task branch and commit ID(s).

## Findings

Implementation has not started.
