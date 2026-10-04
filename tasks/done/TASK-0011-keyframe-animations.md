# TASK-0011: Implement a first Python keyframe animation API

**Status:** Done — owner reviewed and merged
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

## Implementation report (2026-10-04)

This initial report records the first implementation. Its theme/style cancellation
rule and two-sample studio are superseded by the owner follow-up and results below.
The earlier verification evidence is retained as historical evidence.

Continued the existing `task/TASK-0011-keyframe-animations` branch from
specification commit `d720e52`. Startup working tree was clean. `git fetch origin`
and `git merge --ff-only origin/task/TASK-0011-keyframe-animations` confirmed it
was current; `git merge-base --is-ancestor origin/main HEAD` succeeded. Moved
the task from ready to in-progress and updated the index before implementation.
No main changes, merge, PR creation, release or prototype imports were made.

### API and runtime boundary

```python
from pyui_framework import App, Button, Keyframe, Timeline, Window

intro = Timeline(Keyframe(0, opacity=.25, scale=.96),
                 Keyframe(180, opacity=1, scale=1, easing="out_quad"),
                 Keyframe(420, radius=18))
button = Button("Replay", on_click=lambda: button.play(intro))
raise SystemExit(App(Window("Animations", button)).run())
```

Keyframe and Timeline are immutable, with early validation and defensive value
copies. Timestamps are integer milliseconds in 0..2147483647, strictly increasing;
a timeline requires at least two frames. Each property independently interpolates
between its own points and holds its final point until the timeline ends.
Missing zero points snapshot theme/local base values, or scale 1. Explicit zero
points apply immediately. Destination-frame easing is `linear`, `in_quad`,
`out_quad` or `in_out_quad`.

| Target | Supported properties / ranges |
| --- | --- |
| Window | opacity 0..1; background #RRGGBB |
| Label | opacity 0..1; scale 0..2; radius 0..48 logical pixels; foreground/panel #RRGGBB |
| Button | opacity 0..1; scale 0..2; radius 0..48 logical pixels; accent/accent_text #RRGGBB |

Numbers must be finite int/float, excluding bool. Arbitrary Qt/Python properties,
gradients as tracks, named/alpha colors, Row/Column animation and layout changes
are rejected/unsupported. Scale transforms about the center without relayout.

`widget.play(timeline)` returns Playback. `stop()` restores base and is idempotent;
`restart()` returns a new Playback from zero, with a fresh base snapshot.
`state`/`running` expose terminal/control state without Qt objects. The entire
previous run is replaced on new play, even for disjoint properties; stale handles
cannot stop replacements. Completion restores base bindings, without changing
authored style/theme tokens. Valid local-style replacement/clear stops only that
widget; theme replacement/known System changes stop all runs. Invalid updates
retain the previous run. Accent temporarily replaces a gradient with solid fill;
stop/completion restores it.

Python validates and compiles tracks once. Internal QML builds ParallelAnimation
and per-property SequentialAnimation groups using NumberAnimation, ColorAnimation
and PauseAnimation holds. Qt Quick performs all frame timing/interpolation; the
only Python playback notifications acknowledge start and normal completion.
No Python frame loop/timer exists. QML constructs groups before releasing a prior
run; readiness/preparation errors are reported without replacing it. Targets use
their existing per-instance Node and host. Closing immediately cancels all runs;
engine destruction releases hosts before Node bridges, and handles hold only a
weak Python target. Unpresented/pre-launch/closed targets reject playback.

The precise experimental contract and limits are in `docs/animations.md`.

### Windows launch

From `F:\Files\PythonProjects\Framework` in PowerShell:

```powershell
.\run-animations.cmd
# Exact equivalent:
.\.venv-framework\Scripts\python.exe examples\animations.py
# Ordinary example remains unchanged:
.\run.cmd
```

The new Python-only studio demonstrates fade/scale and color/corner timelines.
Each sample and separate Replay button can replay it; Stop all and Restart last
control retained handles. Light/Dark/System and local replace/clear demonstrate
deterministic interruption. The existing `.venv-framework` was used without
global installation. The launcher resolves its own repository directory.

### Verification actually performed

Windows 11 build 26200 (`Windows-11-10.0.26200-SP0`), Python 3.13.9 AMD64,
PySide6/Qt 6.11.2. The visible probe additionally records the actual Qt graphics
API and Window DPR in `evidence/TASK-0011/probe.json`.

Commands from the repository:

```powershell
git fetch origin
git merge --ff-only origin/task/TASK-0011-keyframe-animations
git merge-base --is-ancestor origin/main HEAD
.\.venv-framework\Scripts\python.exe -m pytest tests/test_animation.py -q
.\.venv-framework\Scripts\python.exe -m pytest -q
.\.venv-framework\Scripts\python.exe tests/animation_probe.py evidence/TASK-0011
.\tests\animation_launch_probe.ps1
git diff --check
```

Final focused suite: **39 passed in 9.77 s**. Final full suite:
**88 passed in 53.63 s**, including the existing model, theme, scrolling, dynamic
identity, callback and keyboard regressions. Visible animation probe:
**91 checks**, empty failure/Qt-message/QML-error lists. It verifies numeric/color
interpolation by relating simultaneous tracks rather than assuming tight frame
times; all easing choices, sparse holds, zero/base snapshots, completion, stop,
restart, disjoint replacement, stale handles, gradient restoration, invalid input,
preparation/no-acknowledgement fault rollback, thread rejection, local/theme
interaction, application-only System scheme notifications, dynamic Label, Window
animation, repeated example clicks, resize and shutdown cleanup.

QtTest clicked each Replay eight times, both samples themselves, Restart/Stop,
theme and local controls while animation was active. It resized to 320x300 and
replayed successfully. Scene captures of base, intermediate interpolation,
active example samples, restored appearance and narrow replay were directly
inspected. The ordinary example's interaction/resize checks also ran in the full
suite. Normal Windows launcher probe separately opened `run.cmd` and
`run-animations.cmd` from the system Temp directory, confirmed visible titles
and nonzero native handles, then requested normal close. Both exited **0** with
empty stderr. Launch evidence is in `evidence/TASK-0011/launch/launch.json`.
Whitespace verification passed.

### Limits and owner review

Input above is **synthetic QtTest**, not physical mouse use. Owner must launch
the studio, click both Replay controls repeatedly, resize/scroll, change themes
during playback and judge perceived motion on their display. A real Windows
OS theme transition was not repeated; System coverage uses Qt's application-only
scheme override, resets it afterward, and checks Unknown-notification retention.
Physical replay and display perception remain explicit owner-review checks,
not reported as passed. Other hardware/DPI/backends, prolonged operation,
accessibility, installed-wheel/executable deployment and non-Windows platforms
were not verified by this task. No cross-platform or stable 1.x guarantee.

No pause/resume, seek, loops, completion callbacks or persistent final-value
mode; no arbitrary property/QML escape hatch. A newly appended target must be
presented before play (use a later UI callback). Scale-up can overlap adjacent
layout content. Zero opacity/scale may require a separate replay control.
Qt's existing color precision and theme contrast limitations remain. API choices
are experimental pending owner review; no remaining implementation blocker was
observed in the tested configuration.

### Owner review follow-up (2026-10-04)

The owner launched the example and confirmed basic playback, but found too few
presets to evaluate the API. The owner also expects theme and local-style changes
to update appearance without cancelling an unrelated animation. The current
implementation intentionally cancels all runs on theme changes and cancels a
widget's run on any local-style replace/clear; revise this behavior and example
before final owner review.

#### Playback during theme/style updates

- A theme change, including a System scheme change, must not stop active runs.
  Non-animated appearance properties update immediately to the new theme.
- Replacing or clearing a widget-local style must not stop that widget's active
  run. Updated base style values apply immediately to properties not currently
  animated.
- For a property owned by an active animation track, the track remains visible
  and continues from its current play position. When it completes or the owner
  explicitly stops it, the property resolves to the latest base value (after
  the newest theme and local style changes), not a snapshot from before the run.
  This layered rule applies equally when the animation track itself animates a
  color/radius/opacity token changed by the new theme or local style.
- Preserve the existing explicit `stop()` behavior and public handle lifecycle.
  Theme/style changes are not an implicit stop. Starting another run on the
  same target may continue to replace that target's prior run as documented.
- Add deterministic tests and visible probes for theme and local-style replace
  and clear during an active run, including an overlapping animated property and
  a non-animated property. Verify latest-base restoration on both normal finish
  and explicit stop, and verify an unrelated target's playback is unaffected.

#### More owner-testable animation examples

- Expand the studio to at least six named, visibly distinct, independently
  replayable presets using the supported property types and easing. Cover
  single-property and combined/multi-stage motion, numeric properties, and color
  transitions where supported; avoid presenting six near-identical timings as
  distinct examples.
- Keep controls and status readable in the existing window flow/scroll view.
  Each preset must be triggerable repeatedly by physical click, and it must be
  clear which widget/property is being demonstrated.
- Include theme and local purple/clear controls while one or more samples are
  animating so the owner can verify continuity directly in the runnable app.
- Update the example's introductory/status copy and `docs/animations.md` to
  describe the layered update rule and list the available presets.

#### Follow-up acceptance

- Theme changes, System changes, local-style replacement and clear never cancel
  active playback. Theme/style updates remain visible on unanimated properties;
  animated properties continue and then restore the latest base value.
- `stop()` restores the latest base values, including updates made after playback
  began. Tests cover both overlapping and non-overlapping properties.
- The runnable Windows studio contains at least six different replayable
  animation presets and survives repeated clicks, resize, theme switching and
  local style replace/clear while animations run.
- Focused and full tests, Windows visible launch and the manual scenarios above
  are recorded in a new report section. Keep this task in `tasks/in-progress/`
  until owner review.

### Changed files and Git handoff

- `src/pyui_framework/animation.py`, `__init__.py`, `_model.py`, `_runtime.py`;
  new `qml/AnimatedAppearance.qml`, modified Button/Label/Main QML controls.
- `examples/animations.py`, `run-animations.cmd`; `run.cmd` is unchanged.
- `tests/test_animation.py`, `animation_probe.py`, `animation_launch_probe.ps1`;
  existing `qt_probe.py` export assertion updated.
- `docs/animations.md`, `docs/themes.md`, `docs/architecture/overview.md`,
  `README.md`, `tasks/README.md`, this moved task and `evidence/TASK-0011/`.

Branch: `task/TASK-0011-keyframe-animations`. Implementation commit and push
verification are recorded below. The task remains
in `tasks/in-progress/` as **Implementation complete; owner review pending**.
Only the architecture chat handles owner-approved merge and movement to Done.

Implementation commit: `aa01a7def478aff540cb03f9aac361daa30349f7`
(`TASK-0011: add Qt Quick keyframe animations and Windows demo`), pushed
successfully to origin on the named branch. This report-only follow-up records
the implementation ID without rewriting history. Final handoff verifies the
report commit's push and clean working tree. Ignored probe stdout/stderr logs
remain local; final standalone probe stderr was empty. No uncommitted scoped
source, test, doc or evidence work remains after the handoff.

### Owner review follow-up results (2026-10-04)

Continued the existing `task/TASK-0011-keyframe-animations` at owner-follow-up
specification commit `3d23707`, with a clean working tree. Fetched origin and
fast-forwarded the named branch; it was already up to date. Read the follow-up
before changing code. The task stays in progress for owner review.

**Layered theme/style behavior.** Removed the implicit cancellations from
`_Styled.set_style` and `Runtime.apply_theme`. The existing QML overlay already
keeps animated values separate from resolved appearance bindings. Theme changes,
known System notifications, and local-style replacement/clear now update only
the base. Unowned properties change immediately; owned tracks continue at the
same play position. Completion and explicit stop release the overlay and expose
the latest theme plus latest local overrides, including clears. An implicit
zero-point snapshot remains the track's starting value; it is not reapplied on
updates. An explicit restart captures the new base and returns a new handle.
Replacement, stop and close retain their existing semantics. Theme/style changes
no longer produce terminal `theme_changed` or `style_changed` states.

Qt Quick continues to own interpolation/timing; no Python frame timer, new
renderer, dependency or QML animation algorithm was added. Validation failures
still preserve both base and playback. Accent ownership continues to mask a
base gradient; release now restores even gradient stops replaced during playback.

**Six presets.** The studio now has named sample/Replay pairs for Fade / scale
(3500 ms, multistage opacity and scale), Color / corners (4200 ms, three color
transitions plus radius), Fade only (3000 ms, opacity), Scale pulse (3600 ms,
two shrink/return pulses), Corner sweep (4000 ms, square/rounded/square), and
Text / panel (4000 ms, paired Label text/surface colors). Their different tracks
and shapes make them visibly different effects rather than timing variations.
All five Button samples also replay themselves; the Label uses its Replay button.
Themes, Local purple/Clear local, Stop all and Restart last are above the samples
in the existing flow view. All six samples receive the purple override/clear;
the control buttons retain the app theme. Purple explicitly uses white sample
text for readability in Dark. Longer durations allow theme/local interaction.

**Regression coverage.** The visible probe checks six combinations of
theme/local replace/local clear with normal completion or explicit stop. Each
checks animated opacity/radius/accent at an intermediate position, synchronous
position and active-handle/serial preservation through the update, subsequent
progress, immediate unanimated text-color change, latest-base restoration, and
unaffected playback on another target. Additional checks cover non-overlapping
local fill/radius changes during an opacity-only track, theme text inheritance,
clear, implicit-zero preservation and restart's latest snapshot, latest actual
QML GradientStop colors, System palette changes, Unknown notifications, and
Label/Window overlapping color plus unanimated opacity behavior.

The example probe clicks each of the six Replay controls eight times, observes
actual Qt values change for every preset, and uses Dark, Local purple, Clear local,
Restart last and Stop all while it runs. It tests two concurrent targets during
theme/local updates, resizes to 320x300, sends wheel input, replays and uses the
theme/local controls while narrow, then closes with animations active and verifies
host destruction, target detachment and safe stale handles. Assertions compare
synchronous positions and wait for progress/state with generous timeouts; no
tight frame deadlines are assumed.

**Windows launch and verification.** Existing `.venv-framework`, Windows 11
build 26200, Python 3.13.9 AMD64, PySide6/Qt 6.11.2, Direct3D11, Window DPR 1.0.
No global install. Exact owner launch remains:

```powershell
.\run-animations.cmd
# Equivalent:
.\.venv-framework\Scripts\python.exe examples\animations.py
```

Commands run from the repository:

```powershell
git fetch origin
git merge --ff-only origin/task/TASK-0011-keyframe-animations
.\.venv-framework\Scripts\python.exe -m pytest tests/test_animation.py -q
.\.venv-framework\Scripts\python.exe -m pytest -q
.\.venv-framework\Scripts\python.exe tests/animation_probe.py evidence/TASK-0011/owner-follow-up
.\tests\animation_launch_probe.ps1 -Output evidence/TASK-0011/owner-follow-up/launch
git diff --check
```

Final focused suite: **39 passed in 18.10 s**. Final full suite:
**88 passed in 62.62 s**, including all existing theme, model, callback, keyboard,
dynamic identity and scrollbar/rapid-click regressions. Expanded visible probe:
**223 checks**, no failures, Qt messages or QML errors; standalone probe stderr
was empty. `git diff --check` passed. Directly inspected fresh base, active samples,
Dark/local-active and narrow-active captures: all six sample/Replay pairs are
visible at 800x820, control/status text remains readable, animated properties
continue over the updated base, and the narrow view wraps and scrolls.
Follow-up implementation commit: `d537a6053ce7fea16d12a61ab798e08ea42ef5e0`
(`TASK-0011: preserve animation tracks during style updates and add six presets`),
successfully pushed to origin on the named branch. This report-only handoff
records the ID without rewriting shared history; final handoff verifies its push
and a clean working tree.
New scene/launch evidence is under `evidence/TASK-0011/owner-follow-up/`; earlier
task evidence was preserved. `run.cmd` remains unchanged. Both ordinary and new
studio launchers were separately opened from Temp with visible native windows,
then closed normally with exit 0 and empty stderr.

**Coverage limits.** These new interactions are synthetic QtTest, not physical
mouse use. The task's follow-up records the owner's prior basic playback
confirmation; Codex does not claim owner approval or physical testing of the new
presets. System changes use Qt's application-only override and reset it afterward;
no real OS appearance transition was repeated. Owner should replay all six with
physical clicks, update themes/local styles during motion, test Stop/finish
restoration and judge perceived motion/readability on their display. Alternate
DPI/GPU/backends, long runs, accessibility, installed-wheel/executable deployment
and non-Windows targets remain unverified here. Existing API/property limitations
remain; no new blocker was observed for the tested Windows configuration.

Changed scoped files: `src/pyui_framework/_model.py`, `_runtime.py`,
`examples/animations.py`, `tests/animation_probe.py`, `tests/test_animation.py`,
`docs/animations.md`, `docs/themes.md`, `README.md`, `tasks/README.md`, this report
and new follow-up evidence. Branch remains `task/TASK-0011-keyframe-animations`.
### Owner review and completion (2026-10-04)

The owner tried the expanded animation example, approved the six presets and
continuation across theme/local-style updates, and reported no remaining bugs.
The owner accepts the current behavior and notes that some animations may be
used only occasionally; preserving continuity is still preferred. TASK-0011 was
merged to `main` in commit `8f6ca97`. The display and platform limits above
remain recorded; no blocker remains for this task's tested Windows scope.
Future animation work should use a new linked task instead of reopening this
one. The task record was moved to Done after the owner-confirmed merge.
