# Git and GitHub workflow

## Branch model

- `main` is the shared, reviewable baseline. Do not implement tasks directly on `main` and do not force-push it.
- In GitHub repository settings, protect `main`: require pull requests for changes, block force pushes and deletion, and require applicable checks once CI checks exist. Repository branch protection cannot be enforced by local Git files.
- Use one branch per implementation task: `task/TASK-0006-short-slug` (replace the ID and slug). Fix or follow-up work gets its own new task and branch.
- If the task's named branch already exists because its Ready specification was published there, continue on that branch; do not create a duplicate. Otherwise create the named branch from the latest `origin/main`.
- Start from the latest `origin/main`. If the checkout is dirty or another task is running there, use a separate Git worktree; do not switch branches underneath other work.
- Run independent tasks in separate worktrees. Declare dependencies in task files and merge dependent work in order.

## Commits and remote pushes

- Keep commits focused and use readable messages, preferably `TASK-0006: short description`.
- Before finishing, review `git status` and the diff, run the checks required by the task, and ensure generated environments, credentials, and unrelated user changes are not staged.
- The implementation agent commits its task branch and pushes it to `origin`. Never push task work directly to `main`.
- After implementation and required checks pass, the implementation agent creates a pull request from the task branch to `main` without waiting for a separate request. Include the task ID in the title, summarize implementation and verification in the description, link the task record, and attach/report the PR URL.
- Push each review revision to the same task branch and update the existing PR. Do not rewrite commits already pushed to a shared branch or use force-push; add follow-up commits. Do not close the PR and open a duplicate for requested fixes.
- Report the branch name, PR URL, commit IDs, checks, and any uncommitted work in the task report.
- Keep the task in `tasks/in-progress/` while implementation, PR review, requested revisions, or owner checks are pending. The implementation agent never merges and never moves a task to `tasks/done/`.
- The architecture chat reviews the existing PR diff, task report, and available checks. Use a GitHub PR review with **Request changes** for blocking issues and actionable inline comments where possible; use ordinary PR comments for discussion or non-blocking observations. Explain any visual or physical checks that still need the owner's eyes.
- For requested fixes, the implementation agent continues on the same task branch and updates the existing PR with new commits. It responds to review comments, resolves threads only after addressing them, reruns relevant checks, and reports updated commit IDs. The architecture chat reviews the updated PR and may request another revision.
- The owner may report findings from launching the app in the architecture chat. Record those findings on the same PR and ask the owner to continue the existing implementation chat on that PR. Repeat review and owner checks until all blocking findings are resolved.
- After the owner approves the final result and explicitly authorizes merge, the architecture agent marks the task Done and updates indexes in the same PR branch, rechecks the final diff/check status, and merges that PR through GitHub. The implementation agent must not self-approve or merge. Without final owner approval, leave the PR open and the task in progress.
- If PR creation or updates are blocked by missing CLI/connector permissions, do not bypass branch protection. Keep the task branch pushed, report the exact limitation, and provide its GitHub compare link.
- Do not create a release, publish a package, or change repository settings unless the owner explicitly requests that operation.

## What belongs in Git

Commit source, task specifications and reports, documentation, small test assets, and useful captures that document behavior. Do not commit virtual environments, Python caches, credentials, machine-specific settings, or generated build directories.

The Qt Quick showcase's prebuilt `QtQuickShowcase.dist/` folder is deliberately excluded by `artifacts/qt_quick_showcase/.gitignore`. It is about 207 MB and contains many Qt runtime files. Keep the reproducible source, launchers, package notes, and smoke evidence in Git. Share a prebuilt Windows package through a versioned GitHub Release asset if distribution is needed; do not add the runtime bundle to normal source history.

## Owner review

The owner reviews the PR in the architecture chat, tests the runnable app when relevant, and gives explicit approval before merge. Review feedback stays on the same PR through any number of fix-and-review rounds. `main` should contain only reviewed, integrated work. Tags/releases are for deliberate versions, not ordinary task completion.
