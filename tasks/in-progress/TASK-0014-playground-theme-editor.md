# TASK-0014: Add a theme editor and preview to the API Playground

**Status:** Implementation complete; owner review pending
**Type:** Implementation — repository developer tool; no framework API change
**Depends on:** TASK-0012 and TASK-0013 (merged to `main`); TASK-0010; ADR-0001 and ADR-0003
**Likely files:** `tools/api_playground/`, focused files under `tests/`, `tasks/`
**Branch:** `task/TASK-0014-playground-theme-editor`

## Goal

Let a framework developer edit, validate, save, and visually preview the
framework's existing CSS-inspired `.theme` files directly in the API Playground.
Keep the editor focused: this is a small authoring surface for the framework's
defined theme grammar, not a general CSS editor or visual design suite.

## Context to read

- `AGENTS.md`
- `docs/git-workflow.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/architecture/decisions/ADR-0003-theme-model.md`
- `docs/themes.md`
- `docs/api.md`
- `tasks/README.md`
- `tools/api_playground/README.md`
- `tools/api_playground/Main.qml`
- `tools/api_playground/editor.py`
- `tools/api_playground/runner.py`
- `src/pyui_framework/theme.py` (read only to understand existing validation)
- `examples/themes.py` and `examples/lagoon.theme`

Inspect additional code only where needed. Keep the editor under
`tools/api_playground/`; do not move it into the importable framework package.

## Scope

- Add a Theme tab beside Python source and API Docs in the existing editor
  window. Maintain a separate theme text buffer and dirty state; changing or
  saving the theme must never alter the Python source buffer.
- Edit the repository's existing `.theme` format as UTF-8 text. Provide Open,
  Save, and Save As for theme files, with `.theme` filters/default extension.
  Provide a useful starter theme in a new buffer; never overwrite an existing
  personal scratch theme without an explicit confirmation. Accept an optional
  UTF-8 BOM when opening and save as plain UTF-8.
- Validate the current in-memory text by calling the framework's public
  `Theme.parse(text, source=...)`. Present success or the useful `ThemeError`
  diagnostic, including line/token information where available. Validation is
  read-only and must not launch or stop an application.
- Add a **Preview Theme** action that validates the current theme, saves it if
  needed with clear Save/Cancel behavior, and launches a small representative
  framework preview window in a separate child process. The preview should use
  the public `Theme.load(path)` / `App(..., theme=theme)` API and include a
  Window, Label, and Button so background, text/panel, accent, radius, opacity,
  and gradient effects can be inspected. It may include a button interaction
  that proves controls remain usable. Do not edit, inject into, or overwrite the
  user's Python source to make this preview.
- Reuse the Playground's existing asynchronous child lifecycle and one-child
  limit. Clearly communicate that starting the theme preview replaces a
  currently running authored app; the normal Run action can relaunch the
  authored source. Do not introduce an untracked child process or block the
  editor event loop.
- If parsing fails, keep the editor open, show the diagnostic, and leave the
  currently running child untouched. A saved invalid file may remain on disk
  for editing, but it must not be launched as a preview.
- Track unsaved Python and theme buffers independently. Closing the editor must
  preserve the existing Python save/discard/cancel behavior and also protect
  theme edits from accidental loss. Switching tabs must preserve both buffers.
- Update `tools/api_playground/README.md` with the tab, file controls,
  validation, preview behavior, scratch-file location, and one-child limitation.
- Do not modify the public theme grammar, framework runtime/API, `docs/themes.md`,
  or `docs/api.md`. Do not copy validation rules into a second parser; use the
  existing Theme implementation.

## Out of scope

- Full browser CSS, new theme tokens or grammar, arbitrary selectors, syntax
  highlighting, completion, color picker controls, or visual drag-and-drop
  theme design.
- Live theme replacement or hot reload in a running authored app; Preview
  starts/restarts a child process from the saved theme file.
- Editing the authored Python source automatically, embedding the preview
  window in the editor, or adding multi-window support to `App`.
- A separate general-purpose code editor or cross-platform support claim.

## Acceptance criteria

- Theme tab opens in the existing Playground without disrupting Python source,
  API Docs, output, or Run/Stop controls.
- Theme Open/Save/Save As handle UTF-8, BOM input, paths containing spaces, and
  independent unsaved state. Existing scratch data is not silently replaced.
- Validate reports success for `examples/lagoon.theme` and presents meaningful
  parser diagnostics for malformed, duplicate, unknown, and out-of-range
  declarations. Validation does not mutate source/theme text or child state.
- Preview launches a separate native sample application using the selected
  saved theme file. Its visible framework controls demonstrate the available
  theme tokens; reopening/saving a modified theme and previewing again reflects
  the new values.
- An invalid theme does not replace/stop the currently active child. A valid
  Preview clearly replaces the currently running authored app through the
  existing one-child lifecycle; Run relaunches the authored Python file.
- Closing with independent dirty Python/theme buffers offers safe handling for
  both. No data is discarded after Cancel; the editor remains responsive during
  child start/stop and shutdown.
- README instructions describe the new behavior and limits. No framework API,
  theme grammar, or public API documentation changes are made.
- The implementation report records platform/environment, commands and results,
  changed files, public API impact (none expected), limitations, branch, PR URL,
  and commit IDs. Do not claim manual UI or platform checks that were not run.

## Git and completion

Follow `docs/git-workflow.md` and `AGENTS.md`. This branch was created from the
latest `origin/main` after TASK-0013 merged. Continue on the named branch; do
not create a duplicate. Move this task from `ready/` to `in-progress/` when
implementation begins. Commit and push scoped changes, then create/update one
PR to `main`; never merge or move this task to `done/`. At implementation
completion, mark the report `Implementation complete; owner review pending`
and leave it in `tasks/in-progress/` until architecture and owner review.

## Implementation report — 2026-10-04

The Playground now has a Theme tab with an independent text buffer, path and
dirty marker. Open/Save/Save As operate on the selected text tab; Run always
saves/relaunches Python. The theme starter uses all eight existing tokens and
a distinct panel. New themes save to `.playground/scratch.theme`, with an
explicit confirmation before replacing an earlier scratch session.

Validate calls public `Theme.parse(text, source=...)`, displaying its diagnostic
without changing either buffer, files or child state. Preview validates before
offering Save/Cancel or requesting a process replacement. It also notices a
missing/externally changed saved file and offers Save/Cancel rather than
previewing different text. Invalid text can be saved for editing but never
reaches the preview launch action. Close checks Python and then Theme; Cancel
at either prompt preserves both buffers and keeps the child running.

The sample uses public `Theme.load(path)` and `App(window, theme=theme)` in a
separate process. Window/Labels inherit appearance; one Button shows the
gradient and another overrides only `gradient=None` to expose solid accent.
Both update a Label and print click output. It shares the existing runner,
pending-launch slot, Stop, bounded kill fallback and asynchronous shutdown.
The Theme pane and Output explain replacement and how Run returns to source.

### Changed files and API impact

- `tools/api_playground/theme_editor.py`, `ThemePane.qml`: theme buffer,
  file actions, public-parser validation and Save/Cancel preparation.
- `tools/api_playground/theme_preview.py`: representative public-API sample.
- `tools/api_playground/editor.py`, `runner.py`, `__main__.py`, `Main.qml`:
  tab integration, independent close handling and managed preview arguments.
- `tools/api_playground/README.md`: tab controls, scratch paths, validation,
  preview/replacement, source Run and limitations.
- `tests/test_playground_theme.py`, `playground_theme_probe.py`,
  `playground_theme_sample_probe.py`: buffer/error safety and visible flow.
- This task moved to `tasks/in-progress/`; `tasks/README.md` updated;
  `tasks/evidence/TASK-0014/` stores the observed results and five captures.

**Public framework API impact: none.** No changes to `src/pyui_framework/`,
the theme grammar, examples, `docs/themes.md` or `docs/api.md`.

### Verification actually performed

Windows 11 build 26200, AMD64; repository `.venv-framework`, Python 3.13.9,
PySide6 6.11.2 / Qt 6.11.2. Commands ran from the repository in PowerShell.

| Command | Observed result |
| --- | --- |
| `.venv-framework/Scripts/python.exe -m pytest tests/test_playground.py tests/test_playground_docs.py -q` | 15 passed; existing source runner and API Docs visible flows retained. |
| `.venv-framework/Scripts/python.exe tests/playground_theme_probe.py .playground/verification/TASK-0014` | Passed the visible Theme/editor/native-preview flow with synthetic Qt input. |
| `.venv-framework/Scripts/python.exe -m pytest -q` | 121 passed in 92.77 s. |
| `.venv-framework/Scripts/python.exe -m pytest tests/test_playground_theme.py -q` | 18 passed in 13.12 s after strengthening the shutdown probe to check the real interpreter PID exits. Only the probe and README wording changed after the full suite. |
| `git diff --check` | Passed. |
| `git diff --name-only origin/main -- src docs/api.md docs/themes.md examples` | Empty; excluded framework/API/theme-documentation paths unchanged. |

Focused checks cover UTF-8/BOM input, plain UTF-8 output, Cyrillic/spaced paths,
Save As filter/default suffix/overwrite-confirmation configuration, existing
scratch Cancel/confirm, failed reads/writes, and independent dirty state.
Malformed/duplicate/unknown/out-of-range declarations retain useful parser
source/line/token information. Validation and invalid Preview do not save or
request a lifecycle change. Close covers Python-only, Theme-only and both-dirty
Save/Discard/Cancel cases, including Discard followed by Cancel.

The visible probe edits both QML text areas and switches all three tabs. It
loads Lagoon with a BOM, preserves dirty Python and a sleeping authored child,
shows an invalid radius diagnostic without stopping it, tests Preview Cancel
and Save, and checks a separate visible native preview/PID. It then reopens,
edits, saves with Ctrl+S and previews again, and uses Run from Theme to save and
relaunch source. A timer continues firing during stop/start and close; Win32
checks confirm replaced and shutdown interpreter processes exit. The sample
probe renders the same `build(path)` for two palettes, checks resolved tokens
and native opacity 1.0/0.8, and activates both Buttons with QtTest mouse input.

Evidence: [results](../evidence/TASK-0014/results.json),
[valid Theme tab](../evidence/TASK-0014/theme-valid.png),
[invalid diagnostic](../evidence/TASK-0014/theme-invalid.png),
[560×440 editor](../evidence/TASK-0014/theme-narrow.png),
[Lagoon-style sample](../evidence/TASK-0014/preview-lagoon.png),
[modified sample](../evidence/TASK-0014/preview-modified.png).
Generated captures were visually inspected for text/control layout.

### Limitations and owner checks

UI evidence uses synthetic QtTest/QInputMethodEvent input; file selections and
question responses are stubbed. Native file-dialog interaction and physical
mouse/keyboard usability have not been manually exercised. Window opacity is
asserted through Qt; `grabWindow()` captures do not prove physical desktop
compositing/monitor perception. Other DPI/hardware, prolonged sessions and
non-Windows platforms remain unverified. No live replacement, file watching,
general CSS features or additional framework capabilities were introduced.
No implementation blockers remain; architecture/owner review is pending.

### Git delivery

- Branch: `task/TASK-0014-playground-theme-editor` (existing branch continued).
- Implementation commit: to be recorded after committing this scoped change.
- PR: to be recorded after pushing and creating the PR to `main`.
- Task remains in `tasks/in-progress/`; PR merge and Done transition await
  separate owner authorization in the architecture chat.
