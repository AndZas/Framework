# TASK-0014: Add a theme editor and preview to the API Playground

**Status:** Ready
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
