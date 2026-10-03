# Git and GitHub workflow

## Branch model

- `main` is the shared, reviewable baseline. Do not implement tasks directly on `main` and do not force-push it.
- In GitHub repository settings, protect `main`: require pull requests for changes, block force pushes and deletion, and require applicable checks once CI checks exist. Repository branch protection cannot be enforced by local Git files.
- Use one branch per implementation task: `task/TASK-0006-short-slug` (replace the ID and slug). Fix or follow-up work gets its own new task and branch.
- Start from the latest `origin/main`. If the checkout is dirty or another task is running there, use a separate Git worktree; do not switch branches underneath other work.
- Run independent tasks in separate worktrees. Declare dependencies in task files and merge dependent work in order.

## Commits and remote pushes

- Keep commits focused and use readable messages, preferably `TASK-0006: short description`.
- Before finishing, review `git status` and the diff, run the checks required by the task, and ensure generated environments, credentials, and unrelated user changes are not staged.
- The implementation agent may commit its task branch and push it to `origin`. Never push task work directly to `main`.
- Push the task branch after committing and report the branch name, commit IDs, checks, and any uncommitted work in the task report.
- Do not rewrite commits already pushed to a shared branch or use force-push. Add a follow-up commit unless the owner coordinates otherwise.
- Keep the task in `tasks/in-progress/` for owner review. Do not merge the branch or move the task to `done/`; the owner reviews the diff and report, then merges via GitHub and moves the task to `done/`.
- Do not create a release, publish a package, or change repository settings unless the owner explicitly requests that operation.

## What belongs in Git

Commit source, task specifications and reports, documentation, small test assets, and useful captures that document behavior. Do not commit virtual environments, Python caches, credentials, machine-specific settings, or generated build directories.

The Qt Quick showcase's prebuilt `QtQuickShowcase.dist/` folder is deliberately excluded by `artifacts/qt_quick_showcase/.gitignore`. It is about 207 MB and contains many Qt runtime files. Keep the reproducible source, launchers, package notes, and smoke evidence in Git. Share a prebuilt Windows package through a versioned GitHub Release asset if distribution is needed; do not add the runtime bundle to normal source history.

## Owner review

The owner reviews the pushed branch and task report in the architecture chat. Merge only after review, preferably through a GitHub pull request so the diff and checks remain visible. `main` should contain reviewed, integrated work. Tags/releases are for deliberate versions, not ordinary task completion.
