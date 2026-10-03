# Development workflow

1. Discuss product and architecture questions in the architecture chat.
2. Write an implementation-ready Markdown task in `tasks/ready/` after agreeing on scope and acceptance criteria.
3. Give the implementation chat the task path. It should also follow `AGENTS.md` and read only the referenced context and relevant code.
4. The implementation chat moves the task from `tasks/ready/` to `tasks/in-progress/` when work starts. When implementation is complete, it records evidence and limitations but leaves the file in progress for review. After the owner explicitly approves, the architecture chat merges the PR and moves the task to `tasks/done/`. Keep findings with the task.
5. Run independent coding tasks in separate Git worktrees once the repository has a committed baseline. Avoid concurrent edits in one checkout.
6. Review the implementation report and diff in the architecture chat; record accepted architectural changes in `docs/architecture/decisions/`.
7. Use `docs/git-workflow.md`: implement on a task branch, commit and push it for owner review. Once the owner approves, the architecture chat opens and merges the PR through GitHub.

Follow accepted ADRs as the current architectural direction. A task may add Qt Quick modules, QML components, or bounded platform adapters without changing the foundation. A proposed replacement foundation requires explicit owner discussion, a migration plan, and a new accepted ADR before implementation.

For parallel tasks, declare dependencies and likely file ownership in each task. If two tasks touch the same files or depend on one another, run them sequentially or split their scopes before dispatch.
