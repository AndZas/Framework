# Architecture overview

## Product goal

Build a personal Python UI framework that makes it quick to create Windows applications with a short, approachable API while allowing detailed control over appearance and behavior.

The framework should support customizable shapes, color and image fills, gradients, transparency, app-wide themes, per-widget overrides, animation timelines, windows, and common input. Audio/video and broader device support can be provided by Qt modules or optional integrations where appropriate.

## Accepted foundation

**Selected for the MVP: PySide6 + Qt Quick.** This decision is recorded in [ADR-0001](decisions/ADR-0001-pyside6-qt-quick.md). Python is the application-authoring language. Qt Quick is the scene, rendering, windowing, and UI event foundation; reusable QML/Qt Quick components are internal implementation details behind the framework's Python API.

The first supported target is Windows. Linux and macOS are reasonable future desktop targets, and Android remains a future target to evaluate. This choice does not promise that every Qt module, graphics backend, input device, codec, packaging path, or platform feature works identically. Support for each additional target must be verified and documented.

## Intended layers

1. **Public Python API:** windows, widgets, themes, layout, events, media hooks, and animation descriptions. Prefer concise defaults with explicit escape hatches. The MVP layout policy is deterministic vertical flow for direct children, with explicit `Row`/`Column` composition ([ADR-0002](decisions/ADR-0002-layout-defaults.md)); exact class names and advanced layout APIs remain to be designed.
2. **Python framework/runtime:** owns the app model, IDs, callbacks, theme resolution, lifecycle, validation, and conversion of public declarations into renderable state.
3. **Qt Quick presentation:** QML components and Qt Quick Controls/Shapes render the scene and provide Qt's layout, text, animation, and standard UI behavior. Application authors should not need QML for ordinary use.
4. **Qt/platform integrations:** PySide6/Qt supplies windows, graphics integration, input events, multimedia, and platform services when the relevant module supports the target. Narrow native or third-party adapters may supplement a capability when needed; they should not replace Qt Quick as the UI foundation.

This is a direction for the MVP, not a claim that these layers or the public API are already implemented. Experiments and demos stay outside the production package until implementation tasks explicitly adopt their code.

## Rendering and appearance

Qt Quick's scene graph and Qt Rendering Hardware Interface (RHI) are the rendering basis; the framework will not implement a GPU renderer from scratch for the MVP. Qt may select a graphics API such as Direct3D on Windows, with other APIs available depending on Qt build, configuration, and hardware. The prototype observed Direct3D 11 by default and also completed an optional Vulkan run. This does not make Vulkan a required or guaranteed backend.

The framework's components should support custom geometry and hit testing, rounded or non-rectangular shapes, solid and gradient fills, images, opacity, and animation. Use Qt Quick Shapes, scene-graph-native items, or other suitable Qt Quick primitives based on profiling. Avoid routing ordinary high-volume UI drawing through a CPU-painted item without evidence that it meets performance needs.

Themes should expose shared semantic tokens with runtime switching, system-following light/dark behavior, and local widget overrides. A CSS-inspired token syntax is a product goal; full CSS parsing or browser CSS compatibility is not part of the decision. Animation descriptions should let application authors express durations and keyframes without hand-writing rendering mechanics for common cases.

## Input and media

Qt Quick/Qt event delivery is the default path for keyboard, pointer, focus, and standard window events. Device-specific needs such as gamepads, specialized input, capture, or OS-only events can use Qt modules or optional adapters. The framework should report unsupported or unavailable devices clearly instead of claiming universal parity.

Audio/video playback and device enumeration are optional capabilities for the MVP, likely backed by Qt Multimedia where supported. Capture, codecs, permissions, and device availability are platform-dependent and require separate verification. Core widget rendering must remain usable if optional media or hardware initialization fails.

## Platform direction

- **MVP:** Windows desktop.
- **Future:** Linux and macOS desktop; Android if the Python packaging, Qt modules, input model, and framework API prove viable.
- Keep platform-only features behind adapters and make capability gaps explicit.
- Do not claim cross-platform support until there are repeatable builds and runtime checks on each target.

## Evidence and remaining design work

The decision is supported by the completed experiments: [TASK-0001](../../tasks/done/TASK-0001-qt-quick-feasibility.md) exercised rendering, windows, simulated input, themes, animation, media, and graphics backend selection on Windows; [TASK-0002](../../tasks/done/TASK-0002-python-api-spike.md) showed a Python-only authoring surface; [TASK-0003](../../tasks/done/TASK-0003-python-api-backend-comparison.md) compared direct Qt Quick item construction with an internal-QML-backed Python tree; [TASK-0004](../../tasks/done/TASK-0004-qml-controls-dynamic-tree.md) validated reusable controls, dynamic identity, layout, text, and shape hit testing; and [TASK-0005](../../tasks/done/TASK-0005-interactive-qt-quick-showcase.md) produced a packaged app the owner launched and evaluated.

The showcase included two recorded demo issues: Follow System status-strip contrast, and performance dots that loop between modulo-wrapped coordinates. They are implementation details of the showcase, not evidence of a Qt Quick limitation. Physical device coverage, accessibility, long-run/perceived performance, alternate Windows hardware, and non-Windows targets remain to be validated as relevant tasks are implemented.

The first production Python API and runtime vertical slice is recorded in [TASK-0007](../../tasks/done/TASK-0007-core-vertical-slice.md). The next planned work is to prototype the owner's preferred hybrid theme model—CSS-like theme files, equivalent Python theme objects, and per-widget overrides—in [TASK-0008](../../tasks/ready/TASK-0008-theme-api-spike.md). Its exact grammar and API remain undecided until owner review. Advanced layout behavior, packaging/distribution policy, license review, and per-platform support commitments also remain open decisions; they do not reopen the selected rendering foundation or accepted default-flow layout policy by themselves.
