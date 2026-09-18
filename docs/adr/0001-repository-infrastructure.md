# 0001: Repository infrastructure

Status: Accepted for the infrastructure bootstrap.

## Context

The project needs an installable Python package and repeatable checks before
UI implementation begins. This must not predetermine the graphics stack.

## Decision

Use a `src` layout with import package `framework`, distribution name
`andzas-framework`, and Hatchling for packaging. Require Python 3.13 or newer;
validate Python 3.13 and 3.14 on Windows. Use Ruff for linting and formatting,
strict mypy for typing, and pytest for tests. Keep runtime dependencies empty.

## Rationale and alternatives

The `src` layout exercises an installed package rather than accidentally importing
from the repository root. `framework` does not shadow a standard library module;
the distribution name is separate and does not imply a PyPI name reservation.
Hatchling supports this pure-Python package without a custom build script.
Setuptools would also work, but no legacy build integration is needed here.
Python 3.13 provides a modern baseline while CI also checks 3.14.

## Consequences and boundaries

Contributors install development tools into a virtual environment. Tool version
ranges allow compatible updates, so installations are not bit-for-bit locked.
CI checks both editable and wheel installations. Older Python versions and other
operating systems are not yet validated. Revisit the Python baseline if backend
research identifies a concrete compatibility constraint.

No UI contracts or subsystem ownership are defined by this decision. Backend,
rendering, windowing, and input decisions remain open. Licensing and public
package publication require separate decisions.
