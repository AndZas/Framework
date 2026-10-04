# TASK-0009: Place the vertical scrollbar at the window edge

**Status:** Done; owner-approved
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

### Implementation

Completed on Windows on 2026-10-04. In both
`src/pyui_framework/qml/Main.qml` and `prototypes/theme_api_spike/Main.qml`, the
vertical scrollbar stays attached to the Flickable for Qt's size, position and
input synchronization, but its visual parent is `window.contentItem`. Explicit
right/top/bottom anchors put it at the client-area edge over the full client
height. It is outside the clipped Flickable, which retains its existing 20 px
production / 28 px prototype margins, width, clipping and `Qt.NoButton` policy.
No theme tokens, control skin, Python public API or scroll physics changed.

`tests/scrollbar_edge_probe.py` opens the actual Python production example or the
standalone theme app in separate processes. `tests/test_qt.py` runs both modes as
regressions. The prototype's existing `probe.py` now accepts an optional output
directory so fresh evidence does not overwrite TASK-0008 captures. Its README
documents edge placement and the verification commands. Root README, architecture
overview and task index links now point to this moved in-progress task.

### Verification actually performed

Windows 11 build 26200 (`Windows-11-10.0.26200-SP0`), Python 3.13.9 (MSC v.1944,
64-bit AMD64), PySide6 6.11.2 and Qt 6.11.2. Used the existing ignored local
`.venv-framework` and `.venv-theme-spike`; no dependency installation or global
environment changes. Commands from repository root:

```powershell
git fetch origin
git merge --ff-only origin/task/TASK-0009-scrollbar-edge-layout
.\.venv-framework\Scripts\python.exe -m pytest -q
.\.venv-framework\Scripts\python.exe tests/scrollbar_edge_probe.py --app production --output evidence/TASK-0009/production
.\.venv-theme-spike\Scripts\python.exe tests/scrollbar_edge_probe.py --app theme --output evidence/TASK-0009/theme
.\.venv-theme-spike\Scripts\python.exe -m unittest discover -s prototypes/theme_api_spike -p test_theme.py -v
.\.venv-theme-spike\Scripts\python.exe prototypes/theme_api_spike/probe.py evidence/TASK-0009/theme-regression
git check-ignore .venv-framework .venv-theme-spike
git diff --check
```

Final pytest run: **11 passed in 26.94 s**, including both new shell checks,
existing wheel/scrollbar rapid-click regressions, disabled content dragging,
example callbacks, model checks, keyboard/dynamic-tree smoke and error paths.
Prototype unittest: **5 passed in 0.005 s**. Both dedicated edge probes exited 0;
their captured Qt message lists, including cleanup, are empty. The existing
theme input/render probe exited 0 with no Qt messages and CSS/Python render
equality preserved; it also checks local overrides and live source switching.
Both environments are ignored, and whitespace verification passed.

All measurements below are Qt client-area logical pixels; rectangles are
`[x, y, width, height]` in scene coordinates. The scrollbar right edge equals
the client width, its y is 0 and its height equals the client height.

| App / client size | Clipped viewport | Scrollbar | Horizontal gap | Drag-to-bottom contentY |
| --- | --- | --- | --- | --- |
| Production 640×520 | [20,20,600,480] | [630,0,10,520] | 10 | 204 |
| Production 280×260 | [20,20,240,220] | [270,0,10,260] | 10 | 584 |
| Theme 1040×820 | [28,28,984,764] | [1030,0,10,820] | 18 | 114 |
| Theme 620×420 | [28,28,564,364] | [610,0,10,420] | 18 | 554 |

The default production example content is 236 px tall and fits at 640×520;
its default screenshot is taken before any test additions. The probe also
captures that unchanged example at 280×260, before and after actual thumb
dragging. For normal-size overflow regression it then appends 14 test labels
through the existing runtime API; content height becomes 684 px at 640×520 and
804 px at 280×260 after the example's live action has been added. Theme content
heights are 878 px and 918 px. Full JSON measurements and input results are in
`evidence/TASK-0009/production/probe.json` and `theme/probe.json`.

At each regression size the checks assert visual parenting, unchanged margins,
clipping and disabled mouse content drag; disjoint scrollbar/viewport rectangles
prove that clipped content cannot render beneath the bar. QtTest wheel events
increase contentY, overflow produces a visible thumb, an exposed track click
scrolls, actual thumb press/move/release reaches both endpoints, and geometry
remains correct after input and resizing. No position/contentY property is set
to simulate scrolling. Five immediate clicks and one click after a 500 ms pause
reach the real Python action: production Add is counted per invocation and adds
exactly one live button; theme Load/reload emits one Python change notification
per click and selects the CSS file. Save/Reset status and theme local overrides
remain untouched. Existing production regressions separately verify ten rapid
Target callbacks with no Neighbor callback after wheel and scrollbar input.

Resizing to 640×1200 / 1040×1200 removes overflow: scrollbar size is 1 and thumb
opacity is 0. Returning to the minimum size restores overflow and size < 1.
An initial probe attempted 2400 px height and Windows constrained it to the
screen's maximum with a geometry diagnostic. The probe was corrected to 1200;
final runs have no Qt/QML diagnostics. A harness assertion was also corrected
to compare only explicit local tokens, since inherited theme values legitimately
change after loading CSS. Neither adjustment required application behavior changes.

### Captures and visual inspection

Both apps were launched visibly through their normal construction paths in the
QtTest probes. All ten edge-probe captures were inspected with the image viewer:

- `evidence/TASK-0009/production/default.png` (640×520 unchanged hello example),
  `example-narrow.png` and `example-narrow-scrolled.png` (280×260 unchanged example).
- `evidence/TASK-0009/production/normal-overflow-scrolled.png` (640×520),
  `narrow.png` and `narrow-scrolled.png` (280×260), with test overflow labels.
- `evidence/TASK-0009/theme/default.png` and `normal-overflow-scrolled.png`
  (1040×820), `narrow.png` and `narrow-scrolled.png` (620×420).

The active scrollbar appears at the right edge with a clear gap from controls;
text/cards retain their inset and clip at the viewport boundary. The production
short scrolled capture shows Save/Reset and Add unobscured; the theme short
scrolled capture shows the file field, Load/reload and status unobscured.
Basic-style thumb padding is unchanged; the control's right edge is the client
edge. Overflow visibility retains Qt's existing auto-hide/active behavior.

The existing theme probe also saved its five captures and JSON under
`evidence/TASK-0009/theme-regression/`; its CSS and narrow-scrolled images were
inspected. The full source/style interaction and render-equality checks passed.
TASK-0007/TASK-0008 evidence was preserved.

### Limitations

Input was synthetic QtTest on this Windows machine, not physical mouse use.
Physical wheel/track/thumb feel, touch, alternate DPI/graphics hardware, other
Qt styles, accessibility and Linux/macOS/Android remain unverified. No packaging,
installed-wheel, long-run or performance verification was rerun for this layout
change. Launch scripts were unchanged; these launches used the same application
construction paths directly through the probes. No acceptance blocker remains
for the stated Windows sizes and synthetic input; owner visual/physical review
was pending at implementation handoff.

### Owner review (2026-10-04)

The owner inspected and exercised both the basic production app and the theme
prototype after the change. In both apps the scrollbar sits at the right edge
without covering content; the owner approves the result. This confirms the
reported visual behavior on the owner's setup; the remaining platform and
physical-input coverage limits above still apply.

### Git and owner review

Continued the existing `task/TASK-0009-scrollbar-edge-layout` branch, preserving
specification commit `d5ec77a`. Fetch and fast-forward check were already up to
date. Moved the task from ready to in-progress at startup; it stays here marked
`Implementation complete; owner review pending`. Implementation commit:
`0ce71a7af6f39f4e73eb6c29138c7b31ccdac2a2`
(`TASK-0009: place attached scrollbars at the client edge`). A report-only
follow-up commit, `TASK-0009: record implementation commit for owner review`,
records this ID. Both implementation commits are pushed to origin on the task
branch. The owner approved the result after checking both applications; the
architecture chat records final integration in the GitHub pull request.
