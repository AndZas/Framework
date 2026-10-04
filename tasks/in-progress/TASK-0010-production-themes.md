# TASK-0010: Implement production theme support

**Status:** Implementation complete; owner review pending
**Type:** Implementation
**Depends on:** TASK-0007, TASK-0008, TASK-0009; ADR-0003
**Likely files:** `src/pyui_framework/`, `tests/`, `examples/`, `README.md`, package resource configuration
**Branch:** `task/TASK-0010-production-themes`

## Goal

Implement the first production theme runtime in the existing Python + PySide6/Qt Quick framework. Deliver the hybrid authoring model accepted in [ADR-0003](../../docs/architecture/decisions/ADR-0003-theme-model.md): built-in Light/Dark/System themes, custom CSS-like theme files, equivalent Python theme objects, and widget-local style overrides that resolve consistently and update live.

## Context to read

- `AGENTS.md`
- `docs/git-workflow.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/architecture/decisions/ADR-0002-layout-defaults.md`
- `docs/architecture/decisions/ADR-0003-theme-model.md`
- `tasks/done/TASK-0007-core-vertical-slice.md`
- `tasks/done/TASK-0008-theme-api-spike.md`
- `tasks/done/TASK-0009-scrollbar-edge-layout.md`

Inspect only the relevant production package, prototype theme reference, tests, and example files after reading these documents. Treat the prototype as behavioral evidence, not production code to import.

## Scope

- Implement a validated semantic theme model and a small documented CSS-inspired parser in the production package. Python-authored themes and parsed files must produce the same canonical values.
- Provide built-in Light, Dark, and System choices, plus loading/using custom themes from both supported authoring forms. Follow the API and precedence contract in ADR-0003; pick and document concise public names/signatures consistent with the existing API.
- Apply appearance to the existing production Window, Label, and Button components. Preserve layout behavior and the scrollbar edge placement from TASK-0009.
- Support a local per-widget style at construction and runtime update/clear. App-theme changes must update existing widgets while preserving local overrides; clearing a local override must resume inheritance.
- Keep theme parsing, token conversion, and validation in Python; pass resolved presentation state through the existing internal QML boundary. Do not require application-authored QML.
- Reject malformed files, unknown declarations, invalid types, and out-of-range values with useful errors. Failed loads/updates must leave the previously active appearance intact.
- Add a runnable, focused theme example that lets the owner compare built-in and custom themes, switch appearance while running, and observe a local override. Keep it consistent with the framework's concise Python authoring goal.
- Document public API, supported grammar and token ranges, precedence, System behavior, and current limits in README or focused docs. Update the project status and task index as needed.

## Out of scope

- Full browser CSS syntax, selectors, inheritance or cascade semantics.
- New widgets, layout changes, animation APIs, media, image/shader fills, custom geometry, or renderer replacement.
- Cross-platform support claims, a final 1.x API guarantee, or renaming the temporary `pyui_framework` package.
- Importing prototype modules into the production package.
- Merging this branch or moving this task into `tasks/done/`.

## Acceptance criteria

- The existing example and the new theme example launch on Windows using the project's documented environment.
- Light, Dark, and System resolve predictably. Theme changes update already-visible controls without recreating the window or losing widget-local overrides.
- A CSS-like file and an equivalent Python Theme object produce the same canonical token values and visible result.
- Local style creation, runtime replacement, and clearing work on supported widgets; unrelated widgets continue to inherit the app theme.
- Invalid input reports the source/declaration clearly and does not partially change the active theme or widget appearance.
- Focused automated tests cover parsing and validation, Python/file equivalence, precedence, local override update/clear, live app-theme change, and failed-update rollback.
- The documented production API and grammar agree with implementation; the theme parser is explicitly described as CSS-inspired rather than browser CSS.
- The report states whether a real Windows system light/dark transition was tested. If it cannot be automated reliably, test Qt's available system-scheme path where feasible and clearly record the unverified OS transition.
- Verification evidence includes commands/results for focused tests, full project tests, and manual Windows launch. Any unavailable check is recorded as unverified, not passed.

## Verification

- Use the task branch from current `origin/main`; do not modify `main`.
- Run focused theme tests, then the full project test suite in the project environment.
- Launch the ordinary example and theme example on Windows. Resize and scroll the example to confirm TASK-0009 behavior remains intact.
- While each example runs, switch among Light, Dark, System, and a custom theme; change and clear a local Button or Label style; verify existing controls update and local overrides retain precedence.
- Try malformed syntax, unknown tokens, wrong value types, and values outside allowed ranges; confirm a useful error and unchanged visible state.
- Inspect the final diff, run `git diff --check`, commit scoped changes, and push this task branch. Do not create or merge a PR unless the owner has separately approved review/merge in the architecture chat.

## Report

- Summarize the public API and supported grammar/tokens.
- List changed files and the branch/commit IDs.
- Record exact verification commands, results, Windows environment, and manual scenarios.
- State system-theme transition coverage, limitations, and unresolved design questions.

## Implementation report (2026-10-04)

Implemented the production theme contract from ADR-0003 on the existing Qt Quick
foundation. The task was moved from ready to in-progress before implementation.
It remains here for owner review, with no PR creation, merge or release.

### API and implementation

`Theme(name="Custom", **tokens)`, `Theme.load(path)` and
`Theme.parse(text, source=...)` share validation and canonicalization.
`App(window, theme="light")` / `app.set_theme(...)` select `light`, `dark`,
`system` or a Theme. `app.resolved_theme` returns the full active palette;
`theme.tokens` returns authored values. Both return defensive copies.
Window/Label/Button accept `style={...}`; `set_style(**tokens)` atomically
replaces local tokens and `set_style()` clears them. Row/Column stay layout-only.
Precedence is Light defaults < selected app theme < component-local style.
Partial custom themes never inherit leftover values from a prior theme.

The CSS-inspired grammar has exactly one `:theme` block, semicolon-terminated
declarations, no comments/selectors/cascade and eight semantic tokens:
background, foreground, panel, accent, accent-text, radius, opacity and gradient.
Colors are #RRGGBB, radius is 0..48 logical pixels, opacity is 0..1, and gradient
is a two-stop horizontal `linear-gradient(#RRGGBB, #RRGGBB)` or `none`.
Python uses `accent_text`, numeric int/float (excluding bool), tuple/list gradient
or None. Canonical colors are lowercase, numbers float, gradients tuple/None.
Unknown/malformed declarations, duplicates, wrong types and invalid ranges raise
ThemeError with source/line/token diagnostics where applicable. File read and
encoding errors include the path. Component-specific local tokens are documented
and unsupported local tokens are errors. No dependency or prototype import added.

Python resolves presentation maps and emits QObject notifications into the
existing internal QML components. Light retains the core palette; Dark adds
dark surfaces, pale text/accent and dark Button text. Window uses background/
opacity, Label foreground/panel/radius/opacity, and Button accent/accent_text/
radius/opacity/gradient. Theme changes preserve control/window identities and
local overrides; appended controls inherit the current theme. Fonts, spacing,
inset, scrolling and scrollbar anchors were not redesigned. QML is destroyed
before its bridge objects and scheme notification is disconnected at shutdown.

Changed files:

- `src/pyui_framework/theme.py`, `__init__.py`, `_app.py`, `_model.py`,
  `_runtime.py`; `qml/Main.qml`, `LabelControl.qml`, `ButtonControl.qml`,
  `Style.qml`.
- `examples/themes.py`, `examples/lagoon.theme`, `run-themes.cmd`.
  Ordinary `examples/hello.py`, `setup.cmd` and `run.cmd` remain unchanged.
- `tests/test_theme.py`, `theme_probe.py`, `theme_launch_probe.ps1`;
  existing `qt_probe.py` exports check and `scrollbar_edge_probe.py` private
  runtime construction updated for the new theme runtime.
- `README.md`, `docs/themes.md`, `docs/architecture/overview.md`,
  `tasks/README.md`, this moved task and `evidence/TASK-0010/`.
  No prototype files or package dependency metadata changed.

### User launch

From `F:\Files\PythonProjects\Framework` in PowerShell, with Python 3.13:

```powershell
.\setup.cmd
.\run.cmd
.\run-themes.cmd
# Optional alternate theme asset; paths with spaces are supported:
.\run-themes.cmd "C:\path with spaces\custom.theme"
```

Close one example before launching the other. Theme studio provides Light/Dark/
System, file reload, the equivalent Python Lagoon theme, an amber local sample,
replace and clear actions. Edit `examples/lagoon.theme`, save and reload to test
valid/invalid changes. Errors are displayed in status while the active appearance
is retained. Setup uses the existing ignored `.venv-framework`; no global install.

### What Codex confirmed

Environment: Windows 11 build 26200 (`Windows-11-10.0.26200-SP0`), Python 3.13.9
(MSC v.1944, AMD64), PySide6 6.11.2, Qt 6.11.2, dedicated `.venv-framework`.
Continued existing branch `task/TASK-0010-production-themes`, preserving task
specification commits `54127d8` and `b758101`. Startup status was clean;
`git fetch origin` confirmed the branch includes current origin/main, with only
the two specification commits ahead. No unrelated changes were present.

Commands actually run from repository root:

```powershell
git fetch origin
.\setup.cmd
.\.venv-framework\Scripts\python.exe -m pytest tests/test_theme.py -q
.\.venv-framework\Scripts\python.exe -m pytest -q
.\.venv-framework\Scripts\python.exe tests/theme_probe.py --app ordinary --output evidence/TASK-0010/ordinary
.\.venv-framework\Scripts\python.exe tests/theme_probe.py --app studio --output evidence/TASK-0010/studio
.\tests\theme_launch_probe.ps1
git diff --check
rg 'prototypes|import.*theme_api_spike' src/pyui_framework examples
```

Focused suite: **36 passed**. Full project suite: **47 passed**. These include
parser/validation matrices, line diagnostics, encoding/missing-file errors,
empty/partial fallback, multiline whitespace, defensive copies, Python/file
equivalence, local replacement/clear, live app changes, rollback and existing
callback/focus/dynamic-insertion/rapid-click/scrollbar regressions. The existing
prototype scrollbar test also remains in the full suite; no prototype runtime
is used by the production package. Import search found no prototype references.

Visible QtTest probes passed **77 checks (ordinary)** and **99 checks (studio)**,
with empty failure, QML error and global Qt-message lists, including teardown.
They open the actual examples through the normal public App.run lifecycle;
input is synthetic QtTest, not physical mouse/keyboard use. They verify:

- Light/Dark/System/file/Python updates on retained visible controls; constructor
  and runtime local overrides; Label/Button clear and Window replacement/clear;
  Window local background does not cascade to child text.
- CSS-file and Python-theme whole-window captures are pixel-identical with
  matching widget state; tokens are canonical-equivalent in unit tests.
- Malformed syntax, unknown tokens, wrong types and invalid ranges preserve the
  complete rendered image and active/local values. The studio's real file-reload
  button reports errors for invalid edited files and recovers after correction.
- Wrong-thread updates reject before mutation; dynamically appended controls
  inherit the active palette. Ordinary Save/Reset/Add callbacks and studio theme,
  local replacement and clear callbacks are exercised by actual synthetic clicks.
- Resize from ordinary 640×520 / studio 800×760 to 280×260; viewport retains
  `[20,20,width-40,height-40]`, scrollbar is `[width-10,0,10,height]` and does not
  overlap content. Actual wheel input scrolls; actual thumb drag reaches bottom.

Normal launch verification independently started `run.cmd`, `run-themes.cmd` and
`run-themes.cmd` with an alternate path containing spaces from the system Temp
directory. Hidden consoles launched **visible Qt windows**, each confirmed by
title and nonzero native handle. CloseMainWindow then closed each; all launchers
exited **0 with empty stderr**. `evidence/TASK-0010/launch/launch.json` records
commands, working directory, titles, handles and results. This satisfies a normal
visible Windows launch check; physical manual interaction and double-clicking
the launchers were **not** performed by Codex.

`evidence/TASK-0010/ordinary/` and `studio/` retain probe JSON, default, file,
Python, dark/local and normal/short scrolled PNGs. Default/Light, custom gradient,
Dark, local amber, and short scrolled images were visually inspected: readable
content, distinct palettes, horizontal gradient, inset retained and scrollbar at
the client edge. One deliberately local-colored heading illustrates that custom
styles are not contrast-corrected. Probe copies of the reload file are evidence
assets; the shipped theme asset was never edited by the probes. Earlier task
evidence remains unchanged. `git diff --check` passed.

### System coverage and what the owner must check

Qt initially reported **Dark**. The probes set Qt's **application-only** available
scheme override to Light → Dark → Light and then unset it. The real
colorSchemeChanged signal updated the active System palette each time. Unknown
selection was injected and rejected without mutation; a synthetic Unknown
notification while already following System produced a RuntimeWarning and kept
the last palette. Explicit choices ignore system notifications. Production never
sets the Qt override or changes Windows settings. See the Qt API reference linked
in `docs/themes.md` for this distinction.

**Real Windows OS Light/Dark transition remains unverified.** With System selected
in the studio, personally switch Windows appearance Light → Dark → Light and
verify that the visible controls follow it while the local sample stays amber.
Physically click all theme choices, compare file/Python results, replace/clear
local style, try an invalid saved file then restore it, resize and scroll with
wheel/track/thumb, and test Tab/Space. Judge appearance/readability on your display.

Physical input, double-click launch, touch, accessibility, alternate DPI/GPU,
long runs/performance, installed-wheel/executable distribution and non-Windows
platforms were not reverified. No automatic contrast correction, file watching,
interaction-state/typography tokens, selectors, image/shader fills or stable 1.x
schema is promised. These are current limits/future design questions, with no
unresolved blocker for the task's tested Windows theme contract.

### Owner review follow-up (2026-10-04)

The owner launched the theme studio and confirmed Light/Dark/System switching
(including a real Windows system light/dark transition), physical clicks, and
file reload work. Resolve these remaining visual questions on this task branch
before asking for final approval:

1. **Dark Label surface:** the built-in Dark palette currently sets
   `panel: #202c42` and `background: #131a2a`, while Light sets `panel` equal
   to its window background. Every Label paints its `panel`, so Labels blend
   into Light but appear as cards in Dark. Make the built-in Dark Label surface
   blend into the window by default (match its background), while retaining
   explicit custom `panel` values. Add regression coverage for both built-in
   palettes and custom panels.
2. **File-theme window opacity:** `examples/lagoon.theme` explicitly declares
   `opacity: 0.94`; runtime applies it to the whole Window. Desktop show-through
   is therefore expected from this particular file, not an implicit effect of
   loading any file theme. Confirm visibly at 0.94 and 1.0, ensure the Python
   Lagoon object matches, and make the studio/docs explain whole-window opacity.
   Keep custom transparency supported. Set the shipped example's Lagoon
   opacity to 1.0 if that removes the surprising default; explain the choice
   and retain a test proving explicit opacity reaches the Window.
3. **Midnight gradient:** `prototypes/theme_api_spike/midnight.theme` uses the
   same two-stop `linear-gradient(#RRGGBB, #RRGGBB)` syntax accepted in
   production; no format migration is evident. Compare file-loaded Midnight
   with an equivalent Python Theme and Lagoon. Inspect resolved stops and a
   rendered horizontal pixel profile/capture to determine whether reported
   bands come from the selected stop colors, Qt rendering, or a regression.
   Fix the renderer/mapping if it is a regression; otherwise record evidence
   for correct interpolation versus color/display quantization. Token equality
   alone does not establish visual gradient quality.

#### Follow-up acceptance and verification

- Built-in Dark Labels have no visually distinct unintended card background;
  custom themes with a distinct `panel` still render it.
- The studio explains opacity, the owner can compare the file and equivalent
  Python theme, and explicit opacity remains functional.
- Midnight file and Python forms resolve to the same stops. Include a capture
  or measured profile to establish smooth interpolation or reproduce banding.
- Re-run focused theme tests and the full suite, launch the studio on Windows,
  and repeat Dark Label, Lagoon opacity, Midnight gradient, file reload, and
  theme switching checks. Record results and any visual limitation.
- Leave the task in `tasks/in-progress/` until owner review of these fixes.

### Git and review

Task branch: `task/TASK-0010-production-themes`. Implementation commit:
`1bd9797c74b1a2435fc504811e77af7d68732a36`
(`TASK-0010: implement production themes and live local styles`), pushed to
origin. This report-only follow-up records that ID; final handoff verifies its
push and a clean working tree. Scoped source, tests, docs, task move and evidence
are committed; ignored environments/logs remain local. The task stays in
`tasks/in-progress/` with owner review pending; the architecture chat handles
the explicitly approved PR/merge and completion. No task code was pushed to main.
