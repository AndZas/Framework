# Tasks

Each task is a self-contained instruction for one implementation chat. Start with the named task and its referenced context; do not ask the executor to reconstruct requirements from chat history.

## Lifecycle

- `ready/` — agreed and ready to execute.
- `in-progress/` — currently being implemented.
- `done/` — implementation reviewed by the owner and task record completed.

Use IDs such as `TASK-0001`. Keep the task file with the code history. The task author should specify a goal, context, scope, acceptance criteria, verification, and report format. A task's completion does not automatically approve an architectural decision. Once reviewed and moved to `done/`, keep it as a record; create a new linked task for follow-up work instead of reopening it.

Implementation branches, commits, pushes, and owner review follow [`docs/git-workflow.md`](../docs/git-workflow.md). Implementation agents push task branches but do not merge them. After the owner explicitly approves a reviewed result, the architecture chat creates and merges the PR, then marks the task done.

Completed and reviewed:

- [TASK-0001: Qt Quick feasibility spike](done/TASK-0001-qt-quick-feasibility.md)
- [TASK-0002: Python-first API feasibility spike](done/TASK-0002-python-api-spike.md)
- [TASK-0003: Python API backend comparison](done/TASK-0003-python-api-backend-comparison.md)
- [TASK-0004: QML controls and dynamic Python tree](done/TASK-0004-qml-controls-dynamic-tree.md)
- [TASK-0005: Interactive Qt Quick user showcase](done/TASK-0005-interactive-qt-quick-showcase.md)
- [TASK-0006: Compare default flow layout with explicit containers](done/TASK-0006-layout-api-comparison.md)
- [TASK-0007: Build the first production Python UI vertical slice](done/TASK-0007-core-vertical-slice.md)
- [TASK-0008: Prototype hybrid theme authoring and widget overrides](done/TASK-0008-theme-api-spike.md)
- [TASK-0009: Place the vertical scrollbar at the window edge](done/TASK-0009-scrollbar-edge-layout.md)

There are currently no ready tasks. The owner approved TASK-0009 after checking both application variants. TASK-0008's theme prototype is complete; its proposed public API and token schema remain undecided. TASK-0007 adds the first installable Python UI slice on the selected Qt Quick foundation; its temporary `pyui_framework` import name must be revisited before public release. The project foundation and selected layout policy are recorded in [ADR-0001](../docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md) and [ADR-0002](../docs/architecture/decisions/ADR-0002-layout-defaults.md). TASK-0005 delivered an owner-validated evaluation app. Create a linked follow-up task for production theme implementation after its API contract is approved.
