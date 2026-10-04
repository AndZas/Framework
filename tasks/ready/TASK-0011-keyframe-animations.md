# TASK-0011: Implement a first Python keyframe animation API

**Status:** Ready
**Type:** Implementation
**Depends on:** TASK-0007, TASK-0010; ADR-0001, ADR-0003
**Likely files:** `src/pyui_framework/`, `src/pyui_framework/qml/`, `tests/`, `examples/`, `README.md`, `docs/`
**Branch:** `task/TASK-0011-keyframe-animations`

## Goal

Add an initial, usable Python API for describing and playing keyframe animations
on existing widgets. Integrate it with Qt Quick's animation system, and deliver
a Windows example the owner can launch and interact with using the project's
existing local setup. The API is experimental while the framework remains 0.x;
keep the implementation small, documented, and consistent with the Python-first
surface.

## Context to read

- `AGENTS.md`
- `docs/git-workflow.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/architecture/decisions/ADR-0002-layout-defaults.md`
- `docs/architecture/decisions/ADR-0003-theme-model.md`
- `docs/themes.md`
- `tasks/done/TASK-0007-core-vertical-slice.md`
- `tasks/done/TASK-0010-production-themes.md`

Inspect only the relevant runtime, QML controls, tests, and examples after
reading these documents. Qt Quick remains the animation/rendering foundation;
do not implement a Python per-frame timer or move drawing out of Qt Quick.

## Scope

- Design and implement a concise Python timeline/keyframe API. Use the following
  only as a shape of the desired authoring experience, not as mandatory names:

  ```python
  intro = Timeline(
      Keyframe(0, opacity=0.25, scale=0.96),
      Keyframe(180, opacity=1.0, scale=1.0),
      Keyframe(420, radius=18),
  )
  button.play(intro)
  ```

- Define and document time units, interpolation between keyframes, easing,
  playback control, and what happens when an animation starts while another
  animation is already controlling the same widget properties. Provide the
  smallest practical controls such as play, stop, and restart; add pause/resume
  only if it fits cleanly with Qt Quick and the API.
- Start with a narrow set of useful animatable properties supported by the
  current Window/Label/Button presentation (for example opacity, scale, corner
  radius, and selected colors). Validate property names, value types, ranges,
  keyframe order/timestamps, and easing before playback. Document precisely
  which widget kinds accept which properties. Do not promise arbitrary Python
  or QML property animation.
- Define stable initial-value behavior: establish a deterministic starting
  value for each animated property and restore or retain a documented final
  value when playback completes or stops. Validation or playback failures must
  report clearly without leaving the widget in a partially corrupted state.
- Keep Qt Quick animation objects and implementation details internal. Python
  callers must not need to write QML. Ensure target identity is safe when the
  widget is appended dynamically and when the app/window closes.
- Define and document interaction with app themes and widget-local styles.
  Theme/style updates during an active animation must have deterministic
  behavior; include a test or explicit supported rule rather than accidental
  QML binding behavior.
- Add automated tests for descriptor validation, interpolation/playback
  completion, playback controls, property restrictions, style/theme interaction,
  and lifecycle cleanup. Use QtTest or deterministic Qt signals/state checks;
  do not assert visual timing with fragile tight frame deadlines.
- Add a runnable `examples/animations.py` (or similarly named focused example)
  and a Windows launcher such as `run-animations.cmd` using the existing
  `.venv-framework`. The example must visibly demonstrate at least two keyframe
  animations and let the owner trigger/replay them with physical clicks. Keep
  the ordinary `run.cmd` behavior unchanged.
- Document the experimental Python API, supported properties, time/easing
  syntax, playback semantics, known limits, and exact launch command. Update
  the README/project status and task index.

## Out of scope

- A general animation editor, CSS animation syntax, an animation-file format,
  declarative state machines, a visual timeline widget, or an animation DSL.
- A Python render loop, a custom renderer, arbitrary QML escape hatches, or
  unrestricted animation of every Qt property.
- Broad hover/pressed/focus/disabled styling redesign, accessibility policy,
  media, new widgets, cross-platform claims, or stable 1.x API guarantees.
- Executable packaging or changing the framework's Qt Quick foundation.
- Moving this task to `tasks/done/`, merging its branch, or publishing a release.

## Acceptance criteria

- A short Python example declares multiple keyframes and plays them on an
  existing Button or Label without application-authored QML.
- At least two useful animation types run visibly in the delivered example;
  repeated physical clicks replay them, and the UI remains responsive.
- Qt Quick performs the interpolation/timing. There is no Python callback or
  timer on every rendered frame.
- Invalid descriptors fail early with useful errors and leave the target in a
  documented valid state.
- Stop/restart and normal window shutdown do not leave stale animation objects
  or callbacks. A destroyed/closed target cannot receive later updates.
- Interaction with themes and local styles follows a written deterministic
  rule, verified by tests and demonstrated where practical.
- The exact public API and limitations appear in docs and match the runnable
  example. API choices remain experimental until owner review.
- The Windows animation example launches with the documented project venv and
  can be tested without global package installation or manual QML editing.
- The report includes actual platform/environment, focused and full test
  results, launch/manual checks, and any unverified limitations.

## Verification

- Start on the named branch from current `origin/main`; move this task to
  `tasks/in-progress/` and update the task index before implementation.
- Run focused animation tests and the full test suite using
  `.venv-framework` (Python 3.13 as currently documented).
- Launch the normal example and the new animation example on Windows. Click
  each replay control repeatedly, resize the window, switch themes during a
  supported animation, and confirm the app remains responsive and closes
  cleanly.
- Verify invalid properties, out-of-range values, duplicate/non-monotonic
  keyframe times, and invalid easing produce clear errors before playback.
- Inspect the diff, run `git diff --check`, commit scoped changes, and push the
  task branch. Do not merge or move this task to `done/`; leave it for owner
  review.

## Report

- Summarize the Python API with a small usable code example.
- List supported animated properties and their value ranges by widget type.
- Explain timeline units, interpolation/easing, stop/restart, theme/style
  interaction, and the rendering/runtime boundary.
- List changed files, task branch, commit IDs, verification commands/results,
  Windows launch instructions, and any limitations or unresolved decisions.
