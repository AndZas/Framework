# TASK-0013: Add an API documentation pane to the Playground

**Status:** Done — owner approved and merged to `main`
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

## Implementation report — 2026-10-04

The editor now has Python source and API Docs tabs above the shared output
panel. API Docs reads this checkout's canonical `docs/api.md` on startup and on
explicit Reload, using the repository path resolved by the existing launcher
and editor entry point. The view remains read-only and separate from the
source buffer and child runner. No public framework API, renderer, theme system,
dependency, or `docs/api.md` content changed.

### Changed files and behavior

- `tools/api_playground/docs.py`: repository-relative UTF-8/BOM loading,
  in-pane read failures/retry, literal case-insensitive rendered-text search
  using native Qt document positions, wrapping next/previous navigation,
  heading-link navigation, and display-only targets for other links.
- `tools/api_playground/ApiDocs.qml`: native Markdown `TextEdit`, independent
  two-axis scrolling, Reload, Find/Ctrl+F, Next/Enter/F3, Previous/Shift+F3,
  match count, Clear/Esc, error and reference text.
- `Main.qml`, `__main__.py`, and `editor.py`: connect the docs controller to
  the same editor window, retain the source editor and global file/process
  controls, and reserve readable docs space at the minimum window size.
- `tools/api_playground/README.md`: controls, canonical source path, explicit
  Reload, search, read-only behavior, errors/retry, and link behavior.
- `tests/test_playground_docs.py` and `tests/playground_docs_probe.py`: focused
  loading/failure checks and a visible synthetic Qt acceptance flow.
- This task moved from `tasks/ready/` to `tasks/in-progress/` and its index in
  `tasks/README.md` was updated. Captures and machine-readable observations are
  in [`evidence/TASK-0013/windows-docs`](../../evidence/TASK-0013/windows-docs/).

Native Qt Markdown handled the required constructs without an added Markdown
dependency. One observed Qt 6.11.2 issue needed a docs-only adapter: viewport
text culling hid the far-right part of a long fenced line in a long wrapped
document. The viewer disables `ItemObservesViewport` after text layout and lets
the Flickable clip the native text item. A regression check inspects painted
pixels at the far-right scroll position, in addition to verifying scroll
extents and selecting the last code-line match. This does not alter the
framework's renderer.

### Verification actually performed

Environment: Windows 11 build 26200 (`Windows-11-10.0.26200-SP0`), Python 3.13.9
64-bit, PySide6/Qt 6.11.2, repository `.venv-framework`. Checks used real visible
Qt Quick windows and real QProcess children. Mouse/key input was synthetic
QtTest/QInputMethodEvent; file-dialog selections were stubbed. Resize and
horizontal scrolling were programmatic. Captured images were visually inspected;
physical mouse/keyboard operation and actual file-dialog interaction were not
claimed.

| Command / check | Observed result |
| --- | --- |
| `& ./.venv-framework/Scripts/python.exe -m pytest -q` | 103 passed in 79.12 s on the final implementation. |
| `& ./.venv-framework/Scripts/python.exe -m pytest tests/test_playground_docs.py tests/test_playground.py -q` | 15 passed in 17.08 s after adding the final Enter/F3 and read-only input assertions. |
| `& ./.venv-framework/Scripts/python.exe tests/playground_docs_probe.py evidence/TASK-0013/windows-docs` | Exit 0; results and captures saved. Default startup from an unrelated temporary cwd loaded the real canonical document. Reload/failure mutations used a temporary checkout fixture, leaving canonical bytes untouched. |
| Native Markdown inspection and visible captures | 8 tables, 15 headings, 5 list blocks, 36 fenced-code lines, 2 link fragments, and 181 inline-code fragments. Tables, headings, lists, code indentation, links, and wrapped prose rendered visibly. |
| Search and Reload with a running child and unsaved source | Unicode-offset/case-insensitive search, table-cell search, next/previous/wrap, Enter/F3/Shift+F3, Ctrl+F, no-match, Clear/Esc, and Reload worked. Reload changed matches from 2 to 3; child PID, source text, and dirty state were preserved. A typing attempt did not modify the read-only document. |
| Resize/long-line check | At 560×440, docs retained at least 60 logical pixels of viewport and controls stayed inside the window. A 1,500-character fenced line rendered at the far-right horizontal position; search navigated to match 150 of 150. Vertical scrolling reached the end of the long document. |
| Read failures and retry | Missing file, directory in place of file, and invalid UTF-8 produced useful errors and recovered on Reload. PermissionError was injected in a focused test, then recovery verified; no real Windows ACL was modified. During a visible missing-file error, Stop, Save, Open, Run, and source-tab switching remained usable. |
| Existing Playground regression flow | Source editing, UTF-8 Open/Save/Save As, separate visible app process/window, rerun, Stop fallback, stdout/stderr, source-relative assets, Python/start errors, and asynchronous shutdown passed in `tests/test_playground.py`. |
| `git diff --check` and scoped diff checks | Passed. `docs/api.md`, `src/`, and `pyproject.toml` have no task changes. Canonical SHA-256 stayed `16d4f86b190a9ce478f5ea8c9290dc8e12388c01b120b5debc7f6a970027de6e`. |

### Limitations and review handoff

- Other Windows hardware/DPI, and Linux,
  macOS, and Android remain unverified. Tests do not establish platform support.
- Rendering the whole docs text item avoids the observed culling issue; very
  large future API documents have not been profiled. Current canonical content
  and the extended long-line fixture were checked.
- Other-file/external links display their target in the pane. External browsing,
  document editing, automatic file watching, generated docs, and theme editing
  remain outside scope.
- Public API changes: none. `docs/api.md` needs no update for this task.
- No acceptance blocker remains in the performed checks. The owner reviewed the
  running editor and reported that the API Docs tab,
  rendered reference, and search work correctly. The owner accepts the current
  tab arrangement and prefers not to add a right-side panel to this small
  developer tool at this stage. PR #11 was merged after owner review.

Git handoff: continued `task/TASK-0013-playground-api-docs-pane` at `15c9a60`,
the existing published specification branch, without creating a duplicate.
Implementation commit: `332c4b2b7559d0266f8d2fab3e5c73f7df708341`
(`TASK-0013: add canonical API docs pane to Playground`), pushed to the same
origin branch. A report-only follow-up records this Git/PR handoff; its commit
ID is available in the branch log and the implementation chat's completion
message. No task changes remain uncommitted after that handoff push.

PR: [#11](https://github.com/AndZas/Framework/pull/11), merged to `main` on
2026-10-04 as `2db859395532a1c3f418295882ecad73bb3fbfdb`. The owner reviewed the
running editor, confirmed that the API Docs tab and search work, and accepted
the tab-based layout. GitHub's Codex integration returned HTTP 403 for review
and merge writes; the owner merged the PR through GitHub. No framework/API
change was made.
