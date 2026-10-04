# ADR-0003: Use one semantic theme model with CSS-like and Python authoring

**Status:** Accepted
**Date:** 2026-10-04
**Decision owners:** Project owner

## Context

The framework needs reusable application-wide themes, live theme changes, and precise per-widget appearance overrides. TASK-0008 explored a CSS-like theme file, an equivalent Python theme object, and widget-local styles. The owner launched the prototype, tried its built-in and additional palettes, and accepted this hybrid authoring direction. A production implementation now needs a stable conceptual model without claiming browser CSS compatibility or freezing every public API detail while the package remains version 0.x.

## Decision

1. A theme is a validated set of semantic visual tokens consumed by the framework's Qt Quick presentation layer. CSS-like text and Python objects are two authoring forms for the same model; they must resolve to equivalent visual values.
2. The file format is a deliberately small CSS-inspired theme syntax. It is not browser CSS: layout, arbitrary selectors, DOM semantics, and general CSS cascade behavior are out of scope.
3. Resolution order is built-in component defaults, then the selected application theme, then a widget's local style override. A widget can receive a local style at creation and update or clear that local override at runtime. Clearing it restores inheritance from the active app theme.
4. The app can choose built-in Light, Dark, or System appearance, or a custom theme authored in either supported form. System appearance follows Qt's available platform color-scheme information; behavior on a real Windows OS theme transition must be verified and documented rather than assumed.
5. The initial production token set covers the visual properties demonstrated by TASK-0008: background, foreground, panel, accent, accent text, corner radius, opacity, and a two-stop horizontal gradient. The production task may map these to the existing Window, Label, and Button controls. Layout containers remain layout-only unless implementation evidence requires otherwise.
6. Invalid syntax, unknown tokens, and out-of-range values are reported clearly. A failed theme load or style update must not leave the running application partially styled; preserve the last valid state.
7. Keep the parser, validation, resolution, and Qt Quick rendering behind the Python framework API. Do not require application authors to write QML for ordinary theming.

## Consequences

- A single validated token model avoids divergent semantics between Python themes and theme files.
- Applications can use a ready-made palette, load a reusable file, build a theme in Python, or make a dynamic local override.
- The restricted grammar is easier to validate and evolve than an attempted partial implementation of all CSS.
- The initial token set is intentionally modest. Widget interaction-state tokens (hover, pressed, focused, disabled), typography policies, image/shader fills, custom shapes, CSS grammar compatibility, and schema versioning remain future design work.
- Public names and exact constructor/method signatures remain experimental while the package is version 0.x. Implementations should choose a small coherent API consistent with this contract and document it.

## Alternatives considered

- **Python objects only:** straightforward to validate but less approachable for designers and less portable as a theme asset.
- **CSS files only:** familiar for styling, but poor for dynamic programmatic themes and widget-specific runtime styling.
- **Full CSS support:** substantially expands parser and cascade complexity and would imply compatibility the framework does not need.
- **Independent theme engines per input form:** rejected because the two authoring formats could drift in validation and appearance.

## Evidence and references

- [TASK-0008: Prototype hybrid theme authoring and widget overrides](../../../tasks/done/TASK-0008-theme-api-spike.md)
- [TASK-0009: Place the vertical scrollbar at the window edge](../../../tasks/done/TASK-0009-scrollbar-edge-layout.md)
- [ADR-0001: PySide6 and Qt Quick foundation](ADR-0001-pyside6-qt-quick.md)

## Revisit when

Revisit if production profiling or user feedback shows that token-based styling cannot express common designs, if cross-platform system appearance behaves differently than this contract permits, or before a stable 1.x public API is declared.
