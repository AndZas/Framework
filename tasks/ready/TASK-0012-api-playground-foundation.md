# TASK-0012: Build the API Playground editor and separate-process runner

**Status:** Ready
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
