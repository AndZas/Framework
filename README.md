# Framework

Personal Python UI framework project. The MVP targets Windows; Linux, macOS, and Android are future targets to evaluate.

The selected MVP foundation is **PySide6 + Qt Quick**, recorded in [ADR-0001](docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md). Python is the planned public authoring language, with Qt Quick/QML used internally for presentation and rendering. This establishes the foundation while leaving the public API and implementation plan open for design.

## Project map

- `AGENTS.md` — instructions for Codex working in this repository.
- `docs/architecture/overview.md` — current goals and architecture summary.
- `docs/architecture/decisions/` — decisions and recorded experiments.
- `docs/git-workflow.md` — branch, commit, push, and review workflow.
- `tasks/ready/` — tasks ready for an implementation chat.
- `tasks/in-progress/` — tasks currently being implemented.
- `tasks/done/` — completed task records.
- `prototypes/` — experiments that are not yet part of the framework.

Python package and application code can live in the repository root as the project grows; experiments belong under `prototypes/` until adopted.

## Current status

See [the architecture overview](docs/architecture/overview.md), accepted [ADR-0001](docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md), and completed evidence: [Qt Quick feasibility](tasks/done/TASK-0001-qt-quick-feasibility.md), [Python-first API](tasks/done/TASK-0002-python-api-spike.md), [Python API backend comparison](tasks/done/TASK-0003-python-api-backend-comparison.md), [QML controls and dynamic Python tree](tasks/done/TASK-0004-qml-controls-dynamic-tree.md), and the [interactive owner-evaluation showcase](tasks/done/TASK-0005-interactive-qt-quick-showcase.md).
