# TASK-0010: Implement production theme support

**Status:** Ready  
**Type:** Implementation  
**Depends on:** TASK-0007, TASK-0008, TASK-0009; ADR-0003  
**Likely files:** `src/pyui_framework/`, `tests/`, `examples/`, `README.md`, package resource configuration  
**Branch:** `task/TASK-0010-production-themes`

## Goal

Implement the first production theme runtime in the existing Python + PySide6/Qt Quick framework. Deliver the hybrid authoring model accepted in [ADR-0003](../../docs/architecture/decisions/ADR-0003-theme-model.md): built-in Light/Dark/System themes, custom CSS-like theme files, equivalent Python theme objects, and widget-local style overrides that resolve consistently and update live.

## Context to read

- `AGENTS.md`
- `docs/git-workflow.md`
- `docs/architecture/overview.md`
- `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`
- `docs/architecture/decisions/ADR-0002-layout-defaults.md`
- `docs/architecture/decisions/ADR-0003-theme-model.md`
- `tasks/done/TASK-0007-core-vertical-slice.md`
- `tasks/done/TASK-0008-theme-api-spike.md`
- `tasks/done/TASK-0009-scrollbar-edge-layout.md`

Inspect only the relevant production package, prototype theme reference, tests, and example files after reading these documents. Treat the prototype as behavioral evidence, not production code to import.

## Scope

- Implement a validated semantic theme model and a small documented CSS-inspired parser in the production package. Python-authored themes and parsed files must produce the same canonical values.
- Provide built-in Light, Dark, and System choices, plus loading/using custom themes from both supported authoring forms. Follow the API and precedence contract in ADR-0003; pick and document concise public names/signatures consistent with the existing API.
- Apply appearance to the existing production Window, Label, and Button components. Preserve layout behavior and the scrollbar edge placement from TASK-0009.
- Support a local per-widget style at construction and runtime update/clear. App-theme changes must update existing widgets while preserving local overrides; clearing a local override must resume inheritance.
- Keep theme parsing, token conversion, and validation in Python; pass resolved presentation state through the existing internal QML boundary. Do not require application-authored QML.
- Reject malformed files, unknown declarations, invalid types, and out-of-range values with useful errors. Failed loads/updates must leave the previously active appearance intact.
- Add a runnable, focused theme example that lets the owner compare built-in and custom themes, switch appearance while running, and observe a local override. Keep it consistent with the framework's concise Python authoring goal.
- Document public API, supported grammar and token ranges, precedence, System behavior, and current limits in README or focused docs. Update the project status and task index as needed.

## Out of scope

- Full browser CSS syntax, selectors, inheritance or cascade semantics.
- New widgets, layout changes, animation APIs, media, image/shader fills, custom geometry, or renderer replacement.
- Cross-platform support claims, a final 1.x API guarantee, or renaming the temporary `pyui_framework` package.
- Importing prototype modules into the production package.
- Merging this branch or moving this task into `tasks/done/`.

## Acceptance criteria

- The existing example and the new theme example launch on Windows using the project's documented environment.
- Light, Dark, and System resolve predictably. Theme changes update already-visible controls without recreating the window or losing widget-local overrides.
- A CSS-like file and an equivalent Python Theme object produce the same canonical token values and visible result.
- Local style creation, runtime replacement, and clearing work on supported widgets; unrelated widgets continue to inherit the app theme.
- Invalid input reports the source/declaration clearly and does not partially change the active theme or widget appearance.
- Focused automated tests cover parsing and validation, Python/file equivalence, precedence, local override update/clear, live app-theme change, and failed-update rollback.
- The documented production API and grammar agree with implementation; the theme parser is explicitly described as CSS-inspired rather than browser CSS.
- The report states whether a real Windows system light/dark transition was tested. If it cannot be automated reliably, test Qt's available system-scheme path where feasible and clearly record the unverified OS transition.
- Verification evidence includes commands/results for focused tests, full project tests, and manual Windows launch. Any unavailable check is recorded as unverified, not passed.

## Verification

- Use the task branch from current `origin/main`; do not modify `main`.
- Run focused theme tests, then the full project test suite in the project environment.
- Launch the ordinary example and theme example on Windows. Resize and scroll the example to confirm TASK-0009 behavior remains intact.
- While each example runs, switch among Light, Dark, System, and a custom theme; change and clear a local Button or Label style; verify existing controls update and local overrides retain precedence.
- Try malformed syntax, unknown tokens, wrong value types, and values outside allowed ranges; confirm a useful error and unchanged visible state.
- Inspect the final diff, run `git diff --check`, commit scoped changes, and push this task branch. Do not create or merge a PR unless the owner has separately approved review/merge in the architecture chat.

## Report

- Summarize the public API and supported grammar/tokens.
- List changed files and the branch/commit IDs.
- Record exact verification commands, results, Windows environment, and manual scenarios.
- State system-theme transition coverage, limitations, and unresolved design questions.
