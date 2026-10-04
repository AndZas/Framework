# Tasks

Each task is a self-contained instruction for one implementation chat. Start with the named task and its referenced context; do not ask the executor to reconstruct requirements from chat history.

## Lifecycle

- `ready/` — agreed and ready to execute.
- `in-progress/` — currently being implemented.
- `done/` — implementation reviewed by the owner and task record completed.

Use IDs such as `TASK-0001`. Keep the task file with the code history. The task author should specify a goal, context, scope, acceptance criteria, verification, and report format. A task's completion does not automatically approve an architectural decision. Once reviewed and moved to `done/`, keep it as a record; create a new linked task for follow-up work instead of reopening it.

Implementation branches, commits, pull requests, iterative review, and owner approval follow [`docs/git-workflow.md`](../docs/git-workflow.md). The implementation chat creates the PR after implementation and updates that same PR for requested changes. It never merges. After review and explicit owner approval, the architecture chat completes the task record in that PR and merges it.

## In progress

- [TASK-0012: Build the API Playground editor and separate-process runner](in-progress/TASK-0012-api-playground-foundation.md)

## Completed and reviewed

- [TASK-0001: Qt Quick feasibility spike](done/TASK-0001-qt-quick-feasibility.md)
- [TASK-0002: Python-first API feasibility spike](done/TASK-0002-python-api-spike.md)
- [TASK-0003: Python API backend comparison](done/TASK-0003-python-api-backend-comparison.md)
- [TASK-0004: QML controls and dynamic Python tree](done/TASK-0004-qml-controls-dynamic-tree.md)
- [TASK-0005: Interactive Qt Quick user showcase](done/TASK-0005-interactive-qt-quick-showcase.md)
- [TASK-0006: Compare default flow layout with explicit containers](done/TASK-0006-layout-api-comparison.md)
- [TASK-0007: Build the first production Python UI vertical slice](done/TASK-0007-core-vertical-slice.md)
- [TASK-0008: Prototype hybrid theme authoring and widget overrides](done/TASK-0008-theme-api-spike.md)
- [TASK-0009: Place the vertical scrollbar at the window edge](done/TASK-0009-scrollbar-edge-layout.md)
- [TASK-0010: Implement production theme support](done/TASK-0010-production-themes.md)
- [TASK-0011: Implement a first Python keyframe animation API](done/TASK-0011-keyframe-animations.md)

TASK-0012 is in progress. The owner approved TASK-0009 after checking both application variants, merged TASK-0010 after reviewing production themes and the theme studio, and merged TASK-0011 after trying the animation examples. TASK-0008's hybrid theme prototype informed the accepted initial contract in [ADR-0003](../docs/architecture/decisions/ADR-0003-theme-model.md); production themes and the first keyframe animation API are implemented and recorded in [TASK-0010](done/TASK-0010-production-themes.md) and [TASK-0011](done/TASK-0011-keyframe-animations.md). Exact public names remain experimental while the package is version 0.x. The selected foundation, layout and theme contracts remain ADR-0001, ADR-0002 and ADR-0003.
