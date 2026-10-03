# ADR-0002: Use vertical flow by default with explicit layout groups

**Status:** Accepted
**Date:** 2026-10-04
**Decision owner:** Project owner
**Scope:** Default layout authoring model for the MVP Python API

## Context

The framework aims to make common UI construction concise while still allowing application authors to control composition. Two styles were compared in TASK-0006 using the same Qt Quick backend and equivalent content:

1. Add direct children to a window, which arranges them in a deterministic vertical flow, and use explicit `Row`/`Column` containers for grouping.
2. Express the complete hierarchy explicitly through `Row`/`Column` containers.

The owner ran both examples, found their appearance and behavior equivalent and satisfactory, verified resizing and runtime content updates, and preferred the hybrid style for its more convenient authoring.

## Decision

For the MVP, use **deterministic vertical flow for direct children by default, with explicit layout containers available for composition**.

- Direct children added to a window or flow container appear top-to-bottom in insertion order.
- Authors can introduce horizontal grouping with `Row` and nested vertical grouping with `Column`.
- Layout must not guess intent from a widget's label, type, or visual content.
- Runtime additions target the container explicitly addressed by the API call and append according to that container's rules.

This records the layout model, not final class names or a stable API. The public Python syntax remains subject to the production vertical slice.

## Alternatives considered

- **Require a fully explicit layout tree:** predictable and clear for complex hierarchy, but adds a root container and more code to simple screens. The owner found the hybrid style more convenient.
- **Infer arbitrary layout from widget content:** potentially concise in trivial cases, but ambiguous and difficult to predict or override. Rejected.

## Consequences

- Simple screens can be authored by adding widgets one by one without positions or a mandatory root container.
- More involved screens retain explicit grouping and nesting through layout containers.
- The default flow axis, insertion order, and dynamic append semantics must be documented and stable.
- Initial support can remain narrow: vertical flow, rows, columns, spacing, sizing, and resizing behavior. Grid, overlay, constraints, and absolute positioning are separate future decisions.
- The system does not promise automatic semantic or visual design inference.

## Evidence

- [TASK-0006: Compare default flow layout with explicit containers](../../tasks/done/TASK-0006-layout-api-comparison.md)

Both prototype variants used PySide6 6.11.2 and Qt 6.11.2 on Windows 11 build 26200. They rendered matching geometry at the tested sizes and exercised grouped controls, callbacks, runtime insertion, and narrow-window scrolling. The owner also manually launched and inspected both variants.

## Revisit conditions

Revisit if implementing common layouts with the default flow plus explicit groups proves confusing, if dynamic tree changes cannot remain predictable, or if owner experience with the first production vertical slice contradicts the prototype. Any change should be recorded in a new ADR; layout implementation details may evolve without changing the policy if they preserve its behavior.
