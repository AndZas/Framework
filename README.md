# Framework

Experimental Python framework for modern desktop interfaces.

**Current status: infrastructure bootstrap only.** The package can be installed
and imported, but does not provide GUI functionality yet. Renderer, windowing,
and input technologies have not been selected.

## Development setup (Windows / PowerShell)

Install Python 3.13 or newer. From the repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe examples/import_smoke.py
```

No virtual environment activation is required. The distribution is named
`andzas-framework`; the Python import is `framework`.

## Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m build
```

GitHub Actions runs these checks on Windows with Python 3.13 and 3.14, runs the
example, and tests the built wheel after replacing the editable installation.
Development dependency ranges are in `pyproject.toml`; no runtime dependencies
are required.

## Project notes

- [Architecture status](docs/architecture/README.md)
- [Decision records](docs/adr/README.md)
- [Contributor and agent instructions](AGENTS.md)

Changes are developed in task branches and reviewed through pull requests into
`main`. The next stage is requirements and backend research for a small usable
vertical slice. Licensing has not yet been decided; no license is included.
