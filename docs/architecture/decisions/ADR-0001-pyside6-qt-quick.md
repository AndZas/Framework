# ADR-0001: Use PySide6 and Qt Quick as the framework foundation

**Status:** Accepted
**Date:** 2026-10-04
**Decision owner:** Project owner
**Scope:** MVP rendering, windowing, and UI event foundation

## Context

The project aims to provide a modern, highly customizable Python UI framework. Its MVP targets Windows desktop applications, with possible later Linux, macOS, and Android support. The framework needs modern custom drawing, shaped controls, gradients and images, opacity, animation, multiple windows, input handling, and a path to optional media support. Implementing and maintaining a GPU rendering pipeline, window system, text stack, and event system from scratch would be a large undertaking.

The owner reviewed five experiments. They demonstrated a working Qt Quick graphics/window/input/media slice on Windows, a Python-only app-authoring surface, a workable internal-QML-backed component model, reusable controls and dynamic widgets, and a packaged interactive showcase. The owner launched and evaluated the showcase and accepted Qt Quick as the basis for the project.

## Decision

Use **PySide6 + Qt Quick** as the foundation of the MVP framework.

- Python is the framework user's authoring language.
- Qt Quick is the UI scene, rendering, windowing, and event foundation.
- Reusable QML and Qt Quick components may implement widgets internally; ordinary application code should not need to author QML.
- Qt's scene graph/RHI handles GPU rendering. The MVP will not build a separate renderer or replace Qt Quick with another UI engine.
- Windows is the first supported platform. Other platforms are future targets whose feasibility and support must be verified independently.

This selects a foundation, not a finished framework architecture. It does not freeze the public Python API, widget set, layout rules, theme file syntax, or packaging format.

## Alternatives considered

- **Custom renderer and window/input pipeline:** maximum control but substantially increases implementation, platform, and maintenance cost. Rejected for the MVP.
- **Pygame as the foundation:** flexible for drawing, but would leave more UI primitives, text/layout behavior, window integrations, and platform details to build and maintain in this project.
- **Other existing UI toolkits:** not selected after the completed Qt-focused feasibility sequence and owner review. They can be reconsidered only through a deliberate architecture change.

## Consequences

### Expected benefits

- Reuse Qt Quick's scene graph, GPU abstraction, window integration, input delivery, animation, shapes, controls, text/layout, and available multimedia modules.
- Keep the app-authoring surface Python-first while allowing QML as an internal presentation implementation.
- Support custom control geometry, hit testing, images, gradients, opacity, and animation using Qt Quick primitives.
- Allow Qt-supported graphics backends to be selected/configured where available; do not require one API such as Vulkan.

### Costs and boundaries

- PySide6, Qt, QML modules, deployment, and licensing become core project dependencies that need ongoing compatibility and license review.
- Some difficult or platform-specific requirements may need small Qt or native adapters. Such adapters extend integrations while keeping Qt Quick as the UI foundation.
- Qt feature availability and behavior vary by platform, backend, driver, codec, and device. The project must test and document its actual support matrix.
- The framework must manage the Python-to-Qt/QML boundary, error reporting, lifecycle, and mapping from Python widgets to rendered controls.
- A Qt Quick-specific implementation creates migration cost if the foundation is changed later.

## Evidence

- [TASK-0001: Qt Quick feasibility spike](../../tasks/done/TASK-0001-qt-quick-feasibility.md)
- [TASK-0002: Python-first API feasibility spike](../../tasks/done/TASK-0002-python-api-spike.md)
- [TASK-0003: Python API backend comparison](../../tasks/done/TASK-0003-python-api-backend-comparison.md)
- [TASK-0004: QML controls and dynamic Python tree](../../tasks/done/TASK-0004-qml-controls-dynamic-tree.md)
- [TASK-0005: Interactive Qt Quick user showcase](../../tasks/done/TASK-0005-interactive-qt-quick-showcase.md)

The verified showcase machine was Windows 11 Pro build 26200 with Python 3.13.9 and PySide6/Qt 6.11.2; Qt Quick reported Direct3D 11 by default. An optional prototype run also reported Vulkan. The owner personally launched and explored the packaged showcase. These observations support the MVP selection but do not establish support across hardware or operating systems.

## Revisit conditions

Revisit this ADR if a required MVP capability cannot be delivered with Qt Quick plus a bounded adapter, if required deployment/licensing constraints cannot be met, or if repeatable target-platform tests show the foundation cannot meet the project's needs. A graphics API change within Qt's supported RHI is not by itself a change to this decision. Any move to another UI foundation requires a new accepted ADR and a migration plan.
