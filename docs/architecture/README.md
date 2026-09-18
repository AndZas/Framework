# Architecture status

This is an infrastructure bootstrap, not a UI architecture implementation.

The package is importable but has no window, renderer, widget tree, layout,
input, style, or animation API. No renderer/windowing backend has been selected.
There are no runtime dependencies or import-time resource allocations.

## Current boundaries

- `src/framework/`: installable package; no public UI contracts yet.
- `tests/`: automated package smoke test.
- `examples/`: import smoke and isolated SDL3 research demo (not framework API).
- `.github/workflows/ci.yml`: Windows quality and packaging checks.
- `docs/adr/`: accepted decisions with rationale and consequences.
- `docs/spikes/`: experimental evidence, including
  [SDL3 windowing feasibility](../spikes/sdl3-windowing.md); no backend accepted.

## Next design stage

Agree on the first usable vertical slice and its acceptance criteria. Investigate
renderer, windowing, and input options against multi-window support, text,
graphics, Python integration, distribution, licensing, and measured performance.
Document decisions before implementing the agreed slice. Windows CI is an
initial validation target, not a commitment to Windows-only runtime support.
