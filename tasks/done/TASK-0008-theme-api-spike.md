# TASK-0008: Prototype hybrid theme authoring and widget overrides

**Status:** Done; owner-approved
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

### Implementation and owner launch

Completed on 2026-10-04 in `prototypes/theme_api_spike/`, with no production
package imports or changes. The retained Python style models feed standalone
Qt Quick components. `theme.py` owns the eight-token schema, strict stdlib
parser, Python Theme objects and deterministic resolution; `app.py` owns Qt
notifications, callbacks and system scheme handling. `Main.qml`/`LabButton.qml`
present labels, panels, gradient, sample controls, source selectors, file loading
and local style controls. `README.md` contains full grammar, concise authoring
snippets, recommendations and tradeoffs. `requirements.txt`, setup/run scripts,
five focused unittest cases and a visible QtTest probe complete the experiment.
Useful JSON/captures are under its `evidence/`; local environments/logs/caches
remain ignored. No ADR, release, new production control or API was implemented.

From repository root in Windows PowerShell:

```powershell
.\prototypes\theme_api_spike\setup.cmd
.\prototypes\theme_api_spike\run.cmd
```

Choose Light/Dark/System/CSS/Python; edit `lagoon.theme` and reload or paste a
different path. Click Update local style or a local sample, then change global
themes; click Clear local override to resume inheritance. The method-configured
twin remains amber. Scroll with wheel/scrollbar at short heights to reach file
input and status. Setup requires installed Python 3.13 and installs only inside
the ignored project-local `.venv-theme-spike`.

### Rules evaluated

One case-sensitive `:theme` block supports background, foreground, panel, accent,
accent-text, radius, opacity and gradient. Colors are #RRGGBB; radius is a
unitless 0..48 logical-pixel decimal; opacity is 0..1; gradient is a horizontal
two-stop `linear-gradient(#RRGGBB, #RRGGBB)`. Every declaration requires a
semicolon. No comments, additional selectors, cascade, units, variables, image
fills or browser CSS compatibility. Python accepts equivalent named kwargs and
two-color tuple/list gradients. Both paths share validation and normalization.
No third-party CSS parser/dependency/license was introduced; runtime is the
project's selected PySide6/Qt foundation.

Precedence is built-in light defaults < selected theme < explicit widget style.
Missing theme tokens use defaults, never values from the previous theme. Unknown
tokens, duplicates, syntax and invalid ranges are errors. File diagnostics name
source/input/token and declaration line where applicable. Structural errors name
source. Failed file loading leaves the current theme and local styles intact.
Constructor style and post-construction `set_style` produce equal initial
resolved appearance. `set_style` validates first and replaces the whole local
dictionary; an empty call clears it. Global switching preserves local values.
The dynamic Python callback changes accent, radius and opacity on only one
widget. Local accent text stays explicitly white across global changes.

System uses Qt styleHints colorScheme and colorSchemeChanged. The verified
machine consistently reported Dark; selecting System applied the dark palette.
Live changes of the actual Windows setting were not performed, so reliability
of OS transitions is **unverified**, stated visibly in the window and README.
Unknown produces an explicit error and retains the last palette, without a
guessed fallback or platform adapter. This is provisional system-following
behavior, not a verified platform support promise.

### Verification actually performed

Windows 11 build 26200 (`Windows-11-10.0.26200-SP0`), Python 3.13.9 (MSC v.1944,
64-bit AMD64), PySide6 6.11.2, Qt 6.11.2. A new dedicated environment was created;
no global Python packages were changed. Commands from repository root:

```powershell
py -3.13 -m venv .venv-theme-spike
.\.venv-theme-spike\Scripts\python.exe -m pip install PySide6==6.11.2
.\prototypes\theme_api_spike\setup.cmd
.\.venv-theme-spike\Scripts\python.exe -m unittest discover -s prototypes/theme_api_spike -p test_theme.py -v
.\.venv-theme-spike\Scripts\python.exe prototypes/theme_api_spike/probe.py
git check-ignore .venv-theme-spike
git diff --check
```

Setup rerun exited 0 with dependencies already satisfied. Unittest reported
**5 tests passed (0.003 s)**, including matrices of invalid CSS and Python values,
equivalence, partial fallback, all three precedence levels and defensive copies.
Final visible probe exited 0 with **no Qt/QML messages**, including explicit
engine destruction. QtTest mouse clicks exercised Light/Dark, CSS/Python, System,
the local Python callback, persistence, clear and file reload. It also asserted
failed missing/invalid-file loads and invalid local updates retain state.
The selected custom palette equals the Python-defined palette. The CSS and
Python rendered sample region (1040×820 window, x=0..1039, y=260..649) is
pixel-identical; source-button focus and source status are intentionally outside
that comparison. `probe.json` records each click's resolved global/local state.

At 620×520, the probe checked horizontal bounds of source/sample buttons and
file input. Twelve QtTest wheel events (580,450), angle delta (0,-120), scrolled
to the status; its on-screen position was asserted. Captures `css.png`,
`python.png`, `dark-local.png`, `narrow.png` and `narrow-scrolled.png` document
appearance. CSS, dark/local, narrow and scrolled captures were visually inspected:
gradient visible, readable local white text, no horizontal overflow; vertical
content uses the scroll viewport. Path input scrolls long paths within its field.

The ordinary `run.cmd` was independently started with PowerShell Start-Process
through hidden `cmd /c prototypes\theme_api_spike\run.cmd`, redirected logs and
repository working directory. A Python process owning the visible title
`Theme studio · TASK-0008` and a nonzero native window handle was found;
CloseMainWindow closed it. Launcher exit was 0 and stderr empty (`launch.json`).
This is a visible launch plus synthetic Qt input, **not physical input testing**.

During implementation, native Qt Controls styling emitted customization
warnings; explicitly selecting Basic resolved them. A tuple nested in a QVariant
map did not render gradient stops as intended; explicit notified string
properties resolved that boundary. Explicit QML-engine destruction before Python
context objects eliminated shutdown binding warnings. The initial test helper
needed visual-tree traversal for Repeater children, and scrolling needed QtTest
wheel delivery. These issues were corrected before final successful verification.

Scoped diff/import searches confirm no changes/imports in `src/pyui_framework`
or production examples. No production tests were rerun because production code
was untouched. `git check-ignore` confirmed the environment is ignored, and
`git diff --check` passed.

### Recommendation and unresolved owner choices

Recommend a shared validated semantic token model, CSS-like `Theme.load(path)`
and equivalent Python `Theme(...)`. Recommend optional constructor `style=` for
initial intent plus one replacement `set_style(...)` method for callbacks; both
are practical, and replacement gives unambiguous clearing/rollback. If partial
patches are wanted, name that operation separately. Start with the one semantic
block and deterministic defaults/theme/local order demonstrated here. These are
recommendations, not accepted API/grammar decisions.

Files are concise and separate palette authoring from behavior but require a
parser, source diagnostics and migration/version policy. Python avoids parsing,
enables computation/composition and can offer better editor tooling with typed
tokens. Both share the same validation, resolver and Qt notification work.
The eight-token stdlib parser is small; full CSS would considerably increase
scope. This spike does not measure many-widget performance.

Owner still chooses names, typed Python shape, replacement versus patch,
schema versioning, units/ranges, reusable themes with light/dark variants,
gradient direction/stops/text token, control state tokens and contrast checks.
Hero text is fixed white; arbitrary user gradients/colors can be unreadable.
Opacity applies to whole buttons, including text. No contrast correction or
file watching is implemented. QML layout/style bridge is laboratory code only.

Owner should physically try switching, local controls, valid/invalid edited file
reloads, narrow-window scrolling and Windows Light→Dark→Light while System is
selected, and judge ergonomics/appearance. Physical mouse/keyboard, touch,
screen readers, different DPI/graphics hardware, long runs, Linux/macOS/Android,
packaging/distribution and live OS scheme transitions remain unverified.

### Git and owner review

Continued `task/TASK-0008-theme-api-spike`, preserving specification commit
`e2e2b62`. Fetch and fast-forward check reported already up to date. The task was
moved from ready to in-progress at startup and stays here with implementation
complete and owner review pending. Implementation commit:
`bb8a88558bd308c2db2852bac6abe26f06170714`. This report follow-up is committed
separately as `TASK-0008: record implementation commit for owner review`; both
commits are pushed to origin on the task branch. The preserved specification
commit is an ancestor of the implementation commit (checked with
`git merge-base --is-ancestor e2e2b62 HEAD`). Only prototype source/evidence and
this task record are committed; no merge, force-push, main push, release or
repository-setting change. Working tree is clean at handoff.

### Owner follow-up: additional reusable palettes (2026-10-04)

The owner physically explored the application, reported no noticed bugs and
liked the theme switching/appearance. This is owner feedback, not verification
of every previously unverified case. At the owner's request, added four complete
eight-token CSS-like files alongside Lagoon: `sunset.theme` (cream/rose/copper),
`lavender.theme` (violet/berry), `ocean.theme` (blue/teal) and `midnight.theme`
(dark indigo/lilac with purple/blue gradient). README lists loading paths. No
runtime, production API, parser, QML or dependency changes were needed.

Using the same `.venv-theme-spike` Windows/Python/Qt environment, a one-off
`python.exe -c` check called `Theme.load` and `lab.load` for each file in the
visible app, waited for rendering and captured `window.grabWindow()`. All four
files parsed with eight tokens, selected `CSS file` mode and showed their
expected accents (#a83c46, #7350a2, #2464a0, #bba6f5); command exit was 0 with
no Qt diagnostics. All four captures were visually inspected: distinct palettes
and gradients, readable global text and preserved amber local overrides.
Temporary previews stay ignored in `.venv-theme-spike/theme-previews/`.
`git diff --check` passed. No new physical input, OS scheme or platform claim.

Follow-up is committed as `TASK-0008: add four reusable theme palettes` and
pushed to the same `task/TASK-0008-theme-api-spike` branch. Existing commits are
preserved; task remains in progress for owner review, with no merge performed.

### Owner review and separate layout observation (2026-10-04)

The owner launched the completed prototype, switched and loaded the available
themes, including the four additional CSS-like palettes, and found the theme
behavior and appearance satisfactory with no theme-related bugs. TASK-0008 is
approved as a completed experiment. Its API recommendations remain prototypes;
the final production signatures and token schema still need an explicit design
decision before implementation.

The owner also noticed that the vertical scroll bar sits inside the content
inset and can overlap content. This is a separate application-shell/layout
polish issue, not a theme issue or a blocker for accepting the theme experiment.
In both this prototype and the production slice, `Flickable` has outer margins
and its attached `ScrollBar` uses the Flickable's default parent/geometry. Track
the production fix separately: place the bar at the window edge, outside the
content inset, and verify it no longer covers content while remaining usable.
The theme prototype remains unchanged as the reviewed experiment.
