# TASK-0013: Add an API documentation pane to the Playground

**Status:** Ready
**Type:** Implementation — repository developer tool; no framework API change
**Depends on:** TASK-0012 (merged to `main`); ADR-0001
**Likely files:** `tools/api_playground/`, focused files under `tests/`, `tasks/`
**Branch:** `task/TASK-0013-playground-api-docs-pane`

## Goal

Extend the API Playground so a framework developer can consult the current
public API reference inside the editor while writing an application. The pane
must load the canonical `docs/api.md` from this checkout; do not maintain or
generate a second copy of the API reference.

## Context to read

- `AGENTS.md`
- `docs/git-workflow.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/api.md` (source document to display; do not edit as part of this task)
- `tasks/README.md`
- `tools/api_playground/README.md`
- `tools/api_playground/Main.qml`
- `tools/api_playground/editor.py`

Inspect only additional files needed to wire and verify this feature. Keep the
Playground in `tools/api_playground/`; do not move it into the framework's
importable package.

## Scope

- Add an API Docs view inside the existing editor window. It must be possible to
  switch between editing code and reading documentation without opening a
  separate IDE or external window. Keep the source editor and child application
  behavior intact.
- Render the Markdown as formatted documentation, including headings, lists,
  tables, inline code, fenced code blocks, and links. Prefer Qt Quick's native
  Markdown support if the repository's bundled Qt version renders the required
  constructs correctly; do not add a Markdown dependency without a demonstrated
  limitation and a focused justification.
- Read `docs/api.md` from the current repository root when the Playground starts
  and provide a visible Reload action so edits to the canonical document can be
  loaded without restarting the editor. Resolve the path from the repository,
  not the current working directory or active user source file.
- Make the documentation readable at ordinary window sizes: provide its own
  scrolling, preserve code block formatting, and keep the view usable when the
  editor is resized. Choose a tab or split layout based on the existing QML
  structure; the code editor must retain enough room for normal use.
- Add in-pane text search with next/previous or equivalent navigation and a
  clear way to reset/close the search. Search must not modify the Markdown or
  the user's Python source buffer.
- Handle a missing or unreadable `docs/api.md` without crashing or disabling
  Run/Open/Save. Show a useful in-pane error and a way to retry Reload.
- Update `tools/api_playground/README.md` with the documentation view controls
  and its source-of-truth behavior. Do not change `docs/api.md` itself unless a
  separate public API documentation correction is explicitly requested.
- Keep this a read-only viewer. Editing/saving themes, rendering a separate
  docs window, external-site browsing, auto-watching files, and generated docs
  are out of scope.

## Acceptance criteria

- The Playground opens an API Docs view displaying the current content of the
  repository's `docs/api.md`, independent of the process working directory.
- The formatted view visibly renders the API document's tables, code examples,
  headings, lists, and links; long documents and code lines remain navigable.
- Reload displays changes made to `docs/api.md` after the editor started.
- Search finds text in the loaded document, moves between matches, and can be
  cleared; it does not alter editor source or start/stop the child application.
- If the document cannot be read, the editor remains usable and presents a
  useful error with a working retry after the file becomes available.
- Run/Stop, Open/Save/Save As, and separate-process app behavior continue to
  work from the same editor window.
- README instructions describe the new controls. No change is made to the
  importable framework API, renderer, theme system, or `docs/api.md` content.
- Record verification actually performed, platform/environment, changed files,
  limitations, branch name, and commit IDs in this task report. Do not claim
  manual UI behavior or a platform was verified unless it was actually checked.

## Git and completion

Follow `docs/git-workflow.md` and `AGENTS.md`. Start from the latest `origin/main`
or continue this named task branch if it already exists. Move this task from
`ready/` to `in-progress/` when implementation begins. Commit and push scoped
changes on this branch and create/update its PR to `main`; never merge it or
move it to `done/`. At implementation completion, mark the report
`Implementation complete; owner review pending` and leave it in
`tasks/in-progress/` for the architecture chat and owner review.
