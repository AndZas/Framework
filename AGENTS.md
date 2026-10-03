# Instructions for Codex

## Project intent

This repository is a personal Python UI framework, initially targeting Windows. Its accepted MVP foundation is PySide6 + Qt Quick, as recorded in `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`. The long-term goal is a concise Python API for customizable, animated desktop UI, with Linux, macOS, and Android as possible future targets to evaluate.

## Working rules

- Read the task file explicitly named by the user first. Read only the referenced project documents and relevant code needed for that task.
- Treat accepted ADRs as the current architectural direction. Do not describe Qt Quick as undecided or merely a candidate; do not replace the selected UI foundation in implementation tasks unless the task explicitly changes architecture and an accepted ADR records that change.
- Add functionality through the Python framework/runtime, Qt Quick components, and bounded Qt/native adapters as needed. An adapter may supplement Qt for a specific capability, but do not silently substitute a different UI/rendering foundation.
- Keep future-platform claims evidence-based. Windows is the MVP target; Linux, macOS, and Android remain to be evaluated and verified.
- Keep technology experiments isolated under `prototypes/`. Do not move prototype code into the framework package without an explicit task.
- Follow `docs/git-workflow.md` for all Git work. For an implementation task, continue on the branch named in the task if it already exists; otherwise create that dedicated branch from current `origin/main`. Commit the scoped changes and push the task branch to `origin` when complete. Never work directly on or push task code to `main`; never merge, force-push, publish a release, or change repository settings without a separate owner instruction.
- Follow the task's scope and acceptance criteria. Record platform, environment, commands, observed results, limitations, and unverified cases in the task's requested report.
- Do not silently expand a feasibility spike into a production framework, custom rendering engine, or cross-platform port.
- Preserve unrelated user changes. Do not stage or commit changes outside the assigned task.
- Do not claim a behavior was tested unless it was actually run on the stated platform.

## Task completion

When starting a task, move its file from `tasks/ready/` to `tasks/in-progress/` and update its status. At implementation completion, record the evidence, limitations, and unresolved items, mark it `Implementation complete; owner review pending`, and leave it in `tasks/in-progress/`. The implementation agent must not move a task to `tasks/done/`; after the owner explicitly approves the result, the architecture chat merges the PR and completes the task record. If the work is blocked or incomplete, report that state accurately and leave the task in progress.

At completion, summarize changed files, verification actually performed, and unresolved limitations. Mark implementation complete only when acceptance criteria have evidence; otherwise record the blocker or unverified item.
Include the task branch name and commit ID(s) in the completion report. Leave the task in `tasks/in-progress/` for owner review; the architecture chat handles the approved PR merge and moves the task to `tasks/done/`.
