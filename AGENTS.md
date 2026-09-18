# Repository instructions

## Project and scope

Build a Python desktop UI framework with a small, obvious public API and modern
defaults. Prioritize a usable MVP, API simplicity, separation of responsibilities,
visual quality, then measured performance and extensibility.

The repository currently contains infrastructure only. Renderer, windowing,
input, layout, styling, and animation technologies are undecided. Do not choose
a backend or add architectural abstractions unless the task explicitly asks for
that decision. Do not add a license without the owner's explicit decision.

## Workflow

- Inspect the current code and applicable instructions before editing.
- Implement small, complete, reviewable changes in a task branch; use pull
  requests into `main`. Do not merge without an explicit request.
- Keep `src/framework` for package code, `tests` for automated tests, and
  `examples` for runnable examples. Do not manipulate `sys.path` to import code.
- Keep runtime dependencies minimal; explain new dependencies and tradeoffs.
- Separate the public API from internals. Avoid global mutable state, god
  objects, and mixing rendering, layout, input, styling, and widget state.
- Record significant accepted decisions in `docs/adr/`. Explain the problem,
  decision, rationale, alternatives, ownership/contracts, and limitations.
- Prefer local refactoring over rewrites. Optimize from measurements, not guesses.
- Include relevant tests and update documentation. Report checks that could not
  run, and ask the owner to verify GUI behavior when automated checks cannot.
- Never commit credentials, generated environments, caches, or build artifacts.

## Setup and checks

Use Python 3.13 or newer in a virtual environment. Install with
`python -m pip install -e ".[dev]"`, then run:

```text
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest
python examples/import_smoke.py
python -m build
```

CI validates Python 3.13 and 3.14 on Windows, including installation of the wheel
and a smoke test against that installation. Keep CI and documented checks aligned.
