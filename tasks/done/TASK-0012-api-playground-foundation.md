# TASK-0012: Build the API Playground editor and separate-process runner

**Status:** Done — owner approved and merged to `main`
**Type:** Implementation — repository developer tool; no framework API change
**Depends on:** TASK-0007, TASK-0010, TASK-0011; ADR-0001
**Likely files:** `tools/api_playground/`, `run-playground.cmd`, `.gitignore`, `README.md`, focused files under `tests/`
**Branch:** `task/TASK-0012-api-playground-foundation`

## Goal

Build a small Windows developer app for experimenting with the currently
implemented `pyui_framework` API. It must let the owner edit Python source and
run that source without opening a full IDE or preparing another Python
environment. The authored application opens in its own normal top-level window,
separate from the editor.

This is the first slice of a larger API Playground. Future tasks can add an API
documentation pane and a dedicated theme-file editor after the owner has tried
this foundation.

## Context to read

- `AGENTS.md`
- `docs/git-workflow.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/api.md`
- `README.md`
- `pyproject.toml`
- `tasks/README.md`
- `examples/hello.py` and the existing Windows launcher pattern

After reading those, inspect only the relevant package startup and example
files. Do not read tests or prototype sources unless a concrete implementation
question requires one; keep this tool outside `src/pyui_framework/`.

## Scope

- Add a small standalone editor host under `tools/api_playground/`, using the
  repository's existing PySide6 + Qt Quick dependencies. Keep it a developer
  tool, separate from the importable framework package.
- Provide a basic multi-line Python source editor with a monospace font and
  simple Run, Stop, Open, Save, and Save As actions. Syntax highlighting,
  completion, a debugger, and project navigation are not needed.
- Start with a short working example that imports only public names from
  `pyui_framework`, creates a Window with a Label and Button, and calls
  `App.run()`.
- Keep the default scratch workspace in a root `.playground/` directory and
  ignore that directory in Git so personal experiments are not accidentally
  committed. Open/save Python files as UTF-8. Run must use the current editor
  buffer: save it first and do not launch stale file contents. A new unsaved
  buffer must be saved to the default scratch file or a path selected by the
  owner before launch.
- Add `run-playground.cmd`, rooted at its own location, using the existing
  `.venv-framework` environment. If setup has not been run, show the existing
  `setup.cmd` instruction; do not silently create another environment or
  install packages globally.
- Launch the edited application as a child Python process with Qt's process
  facilities. Use the same project environment, pass executable and arguments
  separately (no shell command string), and set the child's working directory
  to the active source file's parent so relative files behave predictably.
- Keep the child app in its own native window. Do not embed, reparent, or
  simulate the framework window inside the editor. Capture the child's standard
  output and errors in an editor output panel, and show whether it is running,
  exited, or failed to start.
- Keep at most one child app process active. Run again stops the previous
  process before launching the latest saved buffer. Stop and closing the editor
  cleanly stop the child. Keep process handling asynchronous so a slow or stuck
  app does not freeze the editor; use a bounded terminate-then-kill fallback.
- Add concise launch/control notes in the README or a tool-specific README.
  Do not change the public framework API reference unless an actual public API
  change becomes necessary and is separately accepted.

## Out of scope

- An API documentation viewer; the next slice will load the canonical
  `docs/api.md` directly into the editor as read-only help.
- A dedicated `.theme` editor, file watching, or live theme replacement; a
  later slice can add these on top of Run/Stop.
- Re-running automatically on every keystroke, preserving application state
  across launches, or compiling a standalone executable.
- Syntax highlighting, auto-completion, debugging, a general-purpose IDE, or a
  security sandbox for untrusted Python code. The child process protects the
  editor from ordinary crashes and hangs; it does not restrict file/system
  access by user code.
- Embedding the app window, changing the framework renderer/API, or adding
  multiple-window support to `App`. The current public API owns one Window per
  App; this task only ensures the Playground and the authored app are separate
  windows/processes.
- Cross-platform claims. Windows remains the MVP target.

## Acceptance criteria

- `run-playground.cmd` opens the editor using the existing local environment,
  including when launched from a different current directory.
- The editor opens with the starter code, supports editing and UTF-8
  open/save/save-as, and Run saves and launches the exact text currently shown.
- The authored framework app appears in a separate top-level window while the
  editor remains usable and visible.
- The editor captures child stdout/stderr and reports normal exit, nonzero exit,
  and process-start errors without closing itself.
- Run replaces an existing child with the latest version; Stop and closing the
  editor stop the child without blocking the editor's event loop.
- Paths containing spaces work. Relative files used by authored code resolve
  from its source folder.
- The README or tool README explains the one-time setup, launch command,
  controls, and current limitations. No framework behavior is claimed beyond
  what the public API currently implements.
- A focused automated check covers the runner's process lifecycle or command
  construction where practical. On Windows, launch the tool and manually
  exercise edit/run, output, a Python error, rerun, Stop, and editor shutdown.
  Record which checks actually ran; do not claim physical interaction that was
  not performed.

## Planned follow-up slices

1. Show `docs/api.md` inside the Playground, loaded from the repository so the
   display cannot drift from the canonical public API reference.
2. Add a dedicated editor for CSS-inspired `.theme` files and a clear way to
   relaunch the authored app with the latest theme.
3. Use owner feedback from the first two slices to decide whether workspace
   management or optional debounced re-run is worth adding.

Do not implement these follow-ups as hidden scope in TASK-0012.

## Verification and Git

- Continue on the named task branch if it exists; otherwise create it from the
  latest `origin/main`. Move this task to `tasks/in-progress/` and update the
  index before implementation.
- Run focused checks for the runner and the relevant existing suite using the
  repository environment. Launch the Playground on Windows and manually
  exercise the acceptance flow above.
- Review the scoped diff and `git diff --check`. Commit and push this branch,
  then open a pull request to `main` with the task ID in its title. Keep review
  fixes on the same branch and PR.
- Leave the task in `tasks/in-progress/` with status
  `Implementation complete; owner review pending`. Do not merge it or move it
  to `tasks/done/`; the architecture chat handles owner review and merge.

## Report

- Describe the editor controls, workspace/file behavior, process boundary, and
  how the child uses the framework environment.
- List changed files, task branch, commit IDs, PR URL, actual checks and Windows
  launch results, plus limitations and unresolved items.

## Implementation report — 2026-10-04

### Result and API impact

Implemented a repository-only Qt Quick editor in `tools/api_playground/` with
a monospace multi-line Python buffer, Run/Stop/Open/Save/Save As, keyboard
shortcuts, and a resizable output panel. The initial example imports only
public `App`, `Button`, `Label`, and `Window` names. Qt Widgets supplies native
file/confirmation dialogs only; both editor and framework presentation remain
Qt Quick. No public framework API was added, changed, or removed; neither
`src/pyui_framework/` nor `docs/api.md` was changed.

Run saves the exact current text before starting the child. A new buffer saves
to root `.playground/scratch.py`; Save As selects an alternative active file.
The scratch directory is ignored by Git. Existing scratch content requires
confirmation before a fresh starter can replace it. Open accepts UTF-8 with
or without BOM, and Save writes plain UTF-8. Unsaved edits prompt on Open and
close; failed file operations preserve the buffer and prevent a new launch.
The unchanged starter can be closed without a save prompt.

The runner passes `sys.executable`, `-u`, and the absolute source path separately
to `QProcess`, with the source's parent as working directory and UTF-8,
unbuffered stdout/stderr. The existing editable framework environment is used;
no package installation or new environment is performed. The authored app
has its own normal top-level window in a different process, with no embedding.
Status distinguishes startup, running, stopped, normal/nonzero exit, crash,
and failed start. The output panel retains 120,000 recent characters.

Rerun queues only the latest source and waits for the previous process to exit.
Stop cancels pending reruns. Shutdown prevents further edits/runs and keeps the
window alive until child exit. Terminate and the 1.5-second kill fallback use
signals/timers, with no blocking `waitForFinished` in the tool. The Windows
venv redirector can have a different PID from the actual interpreter: the
visible probe checks that actual interpreter exits after rerun, Stop, and
editor close as well as checking `QProcess` state. Fallback termination was
observed in the Windows flow; the editor's event loop continued responding.

### Changed files

- `tools/api_playground/{__init__.py,__main__.py,editor.py,runner.py,Main.qml,README.md}`:
  editor host, file controls, child lifecycle, and setup/control/limitation notes.
- `run-playground.cmd`, `.gitignore`, `README.md`: root-relative launcher using
  `.venv-framework`, ignored scratch workspace, and the entry-point documentation.
- `tests/test_playground.py`, `tests/playground_probe.py`,
  `tests/playground_launch_probe.ps1`: focused runner/file checks, visible QtTest
  acceptance flow, and actual Windows launcher checks.
- `evidence/TASK-0012/`: visible editor/child captures, flow JSON, launcher JSON.
- This task moved from `ready/` to `in-progress/`; `tasks/README.md` links to
  its current location. It stays in progress for review.

### Verification performed

Environment: Windows 11 build 26200, Python 3.13.9 (64-bit), PySide6/Qt 6.11.2,
using `F:\Files\PythonProjects\Framework\.venv-framework\Scripts\python.exe`.

| Command/check | Observed result |
| --- | --- |
| `.\.venv-framework\Scripts\python.exe -m pytest -q` | Final complete run: 97 passed in 73.30 seconds; includes the existing framework suite and 9 Playground tests. |
| `.\.venv-framework\Scripts\python.exe -m pytest -q tests/test_playground.py` | Final focused run: 9 passed in 10.09 seconds. Covers real launches, separate executable/arguments, UTF-8 stdout/stderr, spaced/Unicode paths, relative files, nonzero exit, failed start/recovery, latest-only rerun, asynchronous kill fallback, cancellation, shutdown during startup, current-buffer save, failed save/open, BOM, and unsaved/scratch protection. |
| `.\.venv-framework\Scripts\python.exe tests/playground_probe.py evidence/TASK-0012/windows-flow` | Passed on visible Windows Qt windows with synthetic QtTest mouse/key and text-input events: edit, Save As, Run, separate top-level child, rerun, Stop, Save, relative-file/stdout/stderr output, Python error, failed start, UTF-8 Open, and editor shutdown. Actual child interpreter PIDs were checked for exit. File/confirmation dialogs were stubbed for determinism. |
| `.\tests\playground_launch_probe.ps1` | Actual `run-playground.cmd` launched from `%TEMP%`, opened a visible native editor window, and exited 0 after programmatic window close; final stderr empty. A copied launcher in a spaced folder without the environment exited 1 and printed `Run setup.cmd first.` |
| `git check-ignore .playground/scratch.py` | Scratch path is ignored. |
| `git diff --check` and scoped diff inspection | Passed; no framework/API/prototype changes or generated environments staged. |

Screenshots and JSON are under [Windows flow](../../evidence/TASK-0012/windows-flow/)
and [launcher evidence](../../evidence/TASK-0012/launch/launch.json). Captures were
visually inspected. QML shortcut warnings and teardown null-context warnings
found in the first launcher check were fixed; final launcher stderr is empty.

### Limitations and owner review

The owner explicitly requested in this implementation chat to leave manual
Windows interaction for review. No physical/manual input is claimed. Native
Open/Save As dialogs, physical keyboard/mouse usability, appearance on the
owner's display, and hardware/DPI coverage remain owner checks; synthetic input
and stubbed dialogs do not establish those results. The functional acceptance
flow above has automated evidence. No remaining automated failures are known.

Only one direct child is managed. User code that spawns additional processes
must manage them itself. Forced stop can skip Python cleanup handlers. This is
not a sandbox, IDE, executable packager, or a cross-platform support claim.
No API-help pane, theme editor, file watching, or automatic rerun was added.

### Owner review — 2026-10-04

The owner opened the Playground, edited code, opened previously created Python
files, and launched them. They reported that the files opened and ran as before,
without observed errors, and approved the editor as ready. This is owner-observed
Windows coverage; it does not extend platform or hardware support claims.

### Git and review handoff

- Branch: `task/TASK-0012-api-playground-foundation` (continued from the
  already-published branch; no duplicate branch).
- Implementation commit: `d6618be645ff27ff2f0189327db8781cb8e43858`
  (`TASK-0012: build API Playground editor and process runner`).
- PR: [#10](https://github.com/AndZas/Framework/pull/10), targeting `main`,
  attached to this Codex chat. The GitHub connector's creation call returned
  `403 Resource not accessible by integration`; PR creation succeeded through
  the owner's already-authenticated GitHub browser session. No permissions or
  repository settings were changed.
- This report's PR/commit handoff update is committed and pushed separately
  on the same branch; its commit ID is included in the chat completion report.
- The scoped branch is pushed to `origin`. No uncommitted task work remains
  after the handoff update; local scratch verification artifacts are ignored.
- The owner approved the result after manual use, then merged PR #10 to `main`
  from the authenticated GitHub browser session. The merged baseline is
  `8b582b4` (`TASK-0012: add API Playground editor and separate-process runner`).
  The GitHub integration returned `403 Resource not accessible by integration`
  for PR creation/review/merge operations; the owner completed the merge in the
  browser. No release or repository-setting change was made.
