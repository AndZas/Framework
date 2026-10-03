# TASK-0008: Prototype hybrid theme authoring and widget overrides

**Status:** Ready
**Type:** Experiment
**Depends on:** TASK-0007, ADR-0001, ADR-0002
**Likely files:** `prototypes/theme_api_spike/`, `tasks/in-progress/TASK-0008-theme-api-spike.md`
**Branch:** `task/TASK-0008-theme-api-spike`

## Goal

Build a small, runnable Qt Quick prototype to evaluate the theme authoring model
for the Python framework before implementing it in the production package. The
prototype must demonstrate both CSS-like theme files and Python `Theme` objects,
plus per-widget styling that can change dynamically from Python.

## Owner direction

- CSS-like files are the preferred way to author reusable application themes.
- A Python `Theme` object must offer an equivalent way to define and apply a
  reusable theme; users can choose either authoring path.
- A widget must be independently customizable, either when constructed or by a
  widget method, and its appearance may be updated dynamically from Python.
- These are product requirements, not finalized class names, signatures, CSS
  compatibility promises, grammar, or precedence rules. Keep those decisions
  open for the owner to evaluate in the prototype.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/architecture/decisions/ADR-0002-layout-defaults.md`
- `docs/git-workflow.md`
- `tasks/done/TASK-0007-core-vertical-slice.md`
- Relevant production examples in `src/pyui_framework/qml/` and
  `examples/hello.py`; treat them as reference, not code to modify.

## Scope

- Put all prototype source and launch instructions under
  `prototypes/theme_api_spike/`. Keep it separate from `src/pyui_framework/`.
- Create one polished interactive window with labels, buttons, and panels that
  shows theme changes and local widget styling. Reuse the project's PySide6 +
  Qt Quick foundation.
- Demonstrate a reusable theme defined as a CSS-like file and an equivalent
  Python `Theme` object. Show that both produce the same semantic palette and
  control appearance. State precisely which CSS-like syntax is supported; do
  not claim complete browser CSS compatibility.
- Include built-in light and dark appearance options and a system-following mode
  if Qt exposes the system scheme reliably on the verified Windows setup. If
  system detection is unavailable or unreliable, show and document that result
  rather than silently guessing.
- Demonstrate changing the selected app-wide theme while the prototype is open.
- Demonstrate a local style override on one widget while global themes change,
  then change that widget's style dynamically from a Python callback. Compare
  constructor-time configuration and a post-construction method if both are
  practical; recommend one public interaction pattern in the report.
- Evaluate and document deterministic style precedence. At minimum, test a
  built-in default, a global theme value, and an explicit per-widget override.
- Include representative semantic values that exercise the product direction:
  background and foreground colors, accent, corner radius, opacity, and one
  linear gradient. Keep image fills, shaders, arbitrary geometry, and animation
  timelines out of this spike.
- Provide concise snippets for both authoring paths and an owner-friendly
  Windows launch command. Use an ignored local virtual environment; do not
  install dependencies globally. Avoid a third-party CSS parser unless its
  need, dependency, and license are reported.
- Add focused checks for parsing/validation and theme/override resolution. Keep
  visible/manual owner evaluation separate from automated test claims.

## Out of scope

- Changing the production package, its public API, or its built-in QML styling.
- Recording or implementing an accepted ADR; the owner will choose after seeing
  the prototype and report.
- Full CSS/browser compatibility, CSS layout, selectors beyond the prototype's
  stated small subset, image/shader fills, custom widget geometry, animation,
  new production controls, or cross-platform support.
- Publishing a package, executable distribution, or final public package name.

## Acceptance criteria

- The prototype launches on Windows with a clear interactive example.
- The owner can switch among built-in light/dark choices and load/select a
  CSS-like theme and a Python-object theme while the app is running.
- The two custom theme authoring paths expose equivalent semantic values and
  lead to equivalent appearance for the sample controls.
- One widget has a visible local override that remains understandable when the
  global theme changes; Python can also update that widget's style at runtime.
- Invalid or unsupported theme syntax/value errors are clear and identify the
  problematic input; precedence and fallback behavior are documented.
- The prototype contains no imports from or edits to the production package.
- The report compares the authoring ergonomics and implementation costs, gives
  a recommended minimal API/grammar, lists unresolved choices, and records exact
  verification commands/results. No final API decision is claimed.

## Verification

- Use Windows and an ignored project-local environment. Do not modify the
  global Python installation.
- Run parser/resolution checks and launch the visible prototype.
- Exercise live app-theme switching, both custom theme sources, local override
  precedence, and dynamic Python style updates.
- Record Python, PySide6, Qt, Windows versions, commands, observed results,
  limitations, and cases the owner should inspect manually.

## Report

- Prototype files and concise usage/API examples for CSS-like and Python themes.
- Theme precedence, validation behavior, and dynamic widget-style behavior.
- Verification results and evidence; distinguish automated from owner-visible
  checks and unverified platform/system-theme behavior.
- Recommendation for the production API and grammar, with tradeoffs and open
  decisions; do not silently turn the prototype into production code.
- Task branch and commit ID(s). Leave in `tasks/in-progress/` for owner review.

## Findings

Implementation has not started.
