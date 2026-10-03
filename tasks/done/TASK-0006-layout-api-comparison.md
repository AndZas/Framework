# TASK-0006: Compare default flow layout with explicit containers

**Status:** Done — implementation reviewed and approved by owner
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

Implemented the isolated experiment under `prototypes/layout_api_comparison/`.
`hybrid.py` adds sequential direct window children and an explicit `Row`;
`explicit.py` authors a root `Column` containing the corresponding `Row` and
content. Shared `content.py` creates labels, buttons and distinct callbacks.
`api.py` supplies experimental Python declarations; `runtime.py` and six QML
files keep Qt models, callback IDs, layouts and presentation internal.
`main.py` selects either style and provides the visible synthetic probe.
`setup.cmd`, `run.cmd` and pinned `requirements.txt` prepare the owner launch.
The README includes both Python examples, comparison table, implementation
boundaries, evidence links and a separate owner checklist. No production code
or architecture documents were changed.

**User launch, from repository root in PowerShell:**

```powershell
.\prototypes\layout_api_comparison\setup.cmd
.\prototypes\layout_api_comparison\run.cmd hybrid
.\prototypes\layout_api_comparison\run.cmd explicit
```

Close the first window and launch the other. Add appends one runtime button;
later Add clicks do not duplicate it. Hybrid appends via `window.add(button)`;
explicit appends via the retained `body.add(button)` reference. Both preserve
existing controls and append below the status label. Neither author example
needs QML, bridge names or implementation edits.

**What Codex confirmed on 2026-10-04:** Windows 11 build 26200
(`Windows-11-10.0.26200-SP0`), Python 3.13.9, PySide6/Qt 6.11.2, existing
project-local `.venv-qt-quick`. Setup ran successfully with pinned dependencies
already satisfied; no global packages were installed. Both ordinary `run.cmd`
commands opened visible named windows and exited 0 when PowerShell closed them
through `Process.CloseMainWindow()`. These were normal launches, not probe-only
startup checks; physical user input was not involved.

```powershell
.\prototypes\layout_api_comparison\run.cmd hybrid --probe
.\prototypes\layout_api_comparison\run.cmd explicit --probe
```

Final visible QtTest runs both exited 0 with `RESULT failures=[]`, no QML or
callback errors. They checked initial rendering and authored hierarchy; direct
vertical insertion order and horizontal grouping; independent callbacks;
runtime insertion after show; no duplicate on repeated Add; preservation of an
existing button instance; and interactions after narrowing. Final independent
counts matched in both: Save 3, Reset 2, Add 2, runtime action 3. Geometry checks
found no leaf overlap, horizontal overflow or inadequate text height at 640×520
and 300×520. The longer label grew from 40 to 100 px. At 280×260, synthetic
scrolling reached and activated the runtime button. Exact text/rectangle parity
for initial, normal and narrow states was checked by loading both JSON reports
with the project Python and asserting `a['layouts'] == b['layouts']` and empty
failure lists. This assertion passed.

**Evidence:** `prototypes/layout_api_comparison/evidence/hybrid-probe.json` and
`explicit-probe.json` record environment, rectangles, counters, errors and
failures. `hybrid-normal.png`, `explicit-normal.png`, `hybrid-narrow.png` and
`explicit-narrow.png` show both layouts after insertion at 640×520 and 300×520.
All four captures were visually inspected: equivalent content, legible wrapped
text, grouped actions, status and runtime button, with no visible clipping or
overlap. `git diff --check` also passed. Earlier Loader sizing errors and binding
cycles were fixed before the final runs; they are prototype implementation
issues, not observations about Qt capability.

**Comparison and recommendation:** Both styles render the same layout and have
the same resizing and runtime behavior. Hybrid makes sequential addition and
the runtime target simpler in this small form, at the cost of a documented
implicit root direction. Explicit `Column`/`Row` makes hierarchy clearer and
requires keeping the intended insertion-container reference. Recommend hybrid
default vertical flow with explicit containers for grouping for owner review.
This is an authoring recommendation based on this bounded sample; the owner
decides the public layout API. This task makes no final overall architecture
selection.

**What the owner must verify personally:** normal launch on their setup;
physical mouse clicks and independent counters; wheel/scrollbar use in a short
window; dragging to narrow sizes; physical Tab/Shift+Tab/Space/Enter and focus
behavior; and which Python authoring style is clearer. Codex has not confirmed
these physical-input or subjective usability cases. Screen readers,
accessibility, touch, different DPI/hardware, prolonged operation, performance,
fresh environment creation, double-click launch, packaging and other platforms
remain unverified. The direct `hybrid.py`/`explicit.py` entry points are documented
but were not separately launched. Minimum size is 280×260; arbitrary large rows,
remove/reorder/reparent and a production layout engine are outside this spike.

**Git:** continued the existing `task/TASK-0006-layout-api-comparison` branch.
Implementation commit: `9f893f5ddb509902cf82491037a2fcae78c1f27a`; implementation-report commit: `5e9d779`.
The branch also updates `AGENTS.md`, `docs/git-workflow.md`, and `tasks/README.md`
to preserve the designated task branch when continuing implementation. No other
project behavior was changed.

**Owner review (2026-10-04):** The owner ran both variants, found their
appearance and behavior equivalent and satisfactory, and confirmed resizing
and runtime content updates behaved correctly. The owner prefers the hybrid
authoring model because it is more convenient, provided it does not create
implementation problems. The prototype report and code show no blocker for
that bounded model. Accept the hybrid default-flow policy: direct children of
a window/container flow top-to-bottom in insertion order; authors use explicit
`Row` and `Column` groups where needed. This selects the layout policy for the
MVP while leaving exact API naming and advanced layout features open. See
ADR-0002. The owner authorizes the architecture chat to create and merge the PR
after review; the task is complete after the reviewed branch is integrated.
