# TASK-0009: Place the vertical scrollbar at the window edge

**Status:** Ready
**Type:** Implementation
**Depends on:** TASK-0007, TASK-0008
**Likely files:** `src/pyui_framework/qml/Main.qml`, `prototypes/theme_api_spike/Main.qml`, `tests/`, `prototypes/theme_api_spike/`
**Branch:** `task/TASK-0009-scrollbar-edge-layout`

## Goal

Correct the vertical scrollbar layout in the production app shell and the
owner-reviewed theme prototype. Keep the content's visual inset, but place the
scrollbar at the right edge of the window's client area, outside the inset
content viewport, so it does not sit over or obscure content.

## Owner observation

While reviewing TASK-0008, the owner found that the scrollbar followed the same
inset as the content and slightly overlapped the content beneath it. The
scrollbar remains usable, so this is a visual/layout polish issue rather than a
theme defect or blocker for TASK-0008. The same attached-scrollbar pattern is in
the production QML from TASK-0007. The owner prefers content margins to remain
while the scrollbar sits at the window edge.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/architecture/decisions/ADR-0002-layout-defaults.md`
- `docs/git-workflow.md`
- `tasks/done/TASK-0007-core-vertical-slice.md`
- `tasks/done/TASK-0008-theme-api-spike.md`
- The two QML window/viewport files listed above and their focused probes.

## Scope

- Keep the existing content margins and clipping behavior.
- Reposition the attached vertical `ScrollBar` so its right edge aligns with the
  window's client-area edge, independently of the viewport's content margins.
  Keep it outside the clipped content viewport and prevent it from covering
  content or interactive controls.
- Apply consistent behavior to the production Qt Quick window and the standalone
  theme prototype the owner has been using.
- Preserve current scrolling paths: mouse wheel, interactive scrollbar track and
  thumb, and the desktop policy that prevents content dragging from stealing
  button clicks.
- Add focused regression checks for scrollbar geometry relative to the viewport
  and window, no overlap with content, visibility when content overflows, and
  interactive thumb scrolling. Check normal and narrow/short window sizes.
- Capture and inspect the production example and theme prototype at useful
  sizes. Update the relevant README instructions only if their behavior changed.

## Out of scope

- Theme tokens, CSS-like parsing, Python Theme APIs, or visual scrollbar skinning.
- Changing window/content margins, scroll physics, control hit targets, public
  API, or the Qt Quick foundation.
- Implementing mouse-button dragging of the content; it was disabled to protect
  action clicks during scroll movement and must stay disabled in this task.
- New controls, general responsive-layout redesign, cross-platform work, or
  performance claims.

## Acceptance criteria

- At normal and short/narrow sizes, the vertical scrollbar is visibly aligned
  with the right edge of the window's client area and no longer inherits the
  content's right inset.
- Scrollable content keeps its existing inset and does not render underneath or
  become obscured by the scrollbar.
- Wheel scrolling and interactive scrollbar dragging still work; normal button
  clicks continue to reach the correct Python callbacks during/after scrolling.
- Automated geometry/input checks cover both the production shell and theme
  prototype, with no QML warnings or errors in the tested runs.
- The report states exact sizes, measurements/checks, screenshots, commands,
  environment, and any unverified behavior. No unrelated theme behavior changes.

## Verification

- Use Windows and the project's ignored local environments. Do not install
  dependencies globally.
- Run the focused production tests and prototype checks; use QtTest for geometry,
  scrolling, and action interaction where reliable.
- Launch and inspect both apps at a default size and at a short/narrow size.
- Record actual checks and results; distinguish synthetic input from physical
  owner use and do not claim unrun coverage.

## Report

- Changed files and the scrollbar parenting/anchor strategy.
- Geometry and interaction verification for both apps, with screenshot paths.
- Any limitations or unverified conditions.
- Task branch and commit ID(s). Leave the task in `tasks/in-progress/` for owner
  review; do not merge or move it to Done.

## Findings

Implementation has not started.
