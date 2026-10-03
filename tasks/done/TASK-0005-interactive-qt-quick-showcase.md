# TASK-0005: Interactive Qt Quick user showcase

**Status:** Done — implementation and owner review complete
**Type:** Implementation / owner evaluation
**Depends on:** TASK-0001, TASK-0002, TASK-0003, TASK-0004 (completed experiments)
**Likely files:** `demos/qt_quick_showcase/`, `artifacts/qt_quick_showcase/`, this task's findings section

## Goal

Deliver a Windows showcase that the project owner can launch and explore without manually assembling a Python environment. It should combine the useful behaviors validated across TASK-0001–TASK-0004 in one visible application and include a compact, readable Python example that previews how an application author may use the future framework.

This is a user-evaluation demo, not production framework code and not a final architecture decision. The owner must be able to use mouse and keyboard to explore the controls and judge the visual quality and perceived performance directly.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `tasks/done/TASK-0001-qt-quick-feasibility.md`
- `tasks/done/TASK-0002-python-api-spike.md`
- `tasks/done/TASK-0003-python-api-backend-comparison.md`
- `tasks/done/TASK-0004-qml-controls-dynamic-tree.md`
- Relevant prototype READMEs and source under `prototypes/qt_quick_spike/`, `prototypes/python_api_spike/`, `prototypes/api_backend_comparison/`, and `prototypes/qml_tree_spike/`.

Do not assume the existing `.venv-qt-quick` is available or usable by the owner. Diagnose Python launcher/version issues and build the showcase in a dedicated environment or package.

## Scope

Create a self-contained showcase project under `demos/qt_quick_showcase/`. Keep app-author-facing example code separate from framework/demo internals. The example should be short and abstract enough to communicate the intended Python experience, even if the demo temporarily hardcodes some implementation details.

### Interactive application

Provide a clear, polished test window with sections or tabs for:

1. **Controls and shapes:** rounded buttons plus a star-shaped control; gradients, stroke, partial opacity, hover/pressed/focus states, and click behavior. The star's interactive region should follow its shape and visibly respond to activation.
2. **Themes:** light/dark (and a system-following option if reliable), a runtime theme switch, and one per-control style override. Include a small CSS-inspired theme file or token example if practical; do not build a general CSS engine.
3. **Animation:** a repeatable property animation or keyframe sequence with controls to start/stop or replay it.
4. **Dynamic controls and windows:** several buttons of the same type with independent actions/IDs, adding/removing at least one control at runtime, and a second independent window.
5. **Input:** normal physical mouse and keyboard behavior, tab focus and keyboard activation. Show the active focused control where practical. Touch should be demonstrated only when hardware is available; otherwise label it unverified.
6. **Media and devices:** play a small bundled synthetic video and audio sample; enumerate audio inputs/outputs and cameras. Make the current device list and playback status visible. Offer camera/microphone capture only if it can be made reliable and clear that permissions/hardware are needed; otherwise explain the status without failing the whole showcase.
7. **Performance playground:** a repeatable switch between modest and heavier visual scenes (include at least 50 and 400 animated simple elements plus a large image, or explain an evidence-based alternative). Display the selected item count and clearly labeled approximate frame-swap timing/CPU observations. Do not label `frameSwapped` callbacks as true monitor FPS. Let the owner switch the load on/off and visually judge responsiveness; record that perception is hardware-specific.
8. **Diagnostics:** show Python, PySide6, Qt, active graphics backend, and any failed media/device/QML initialization in an in-app log or readable error dialog. The demo should fail gracefully when optional devices are absent.

Use reusable Qt Quick Controls and Qt Quick Shapes for ordinary controls and the star. Keep QML internal to the demo; the app-author example must be Python-only.

### Python API example

Provide a standalone, syntax-highlightable `example_app.py` (or similarly named file) containing the concise app-author-facing example. It should declare a theme, window, controls, callbacks, and animation, then run the app. Include the source in the demo folder and point to it from the UI or start guide. Keep private Qt/QML bridge details out of this example.

### Launch and packaging

Provide `START_HERE.md` and a double-clickable Windows launcher. The owner should not need to activate or locate `.venv-qt-quick`.

First attempt a portable Windows deployment using the current official Qt for Python deployment tool (`pyside6-deploy`) or another justified Qt-aware bundler. Prefer a folder containing the EXE and required Qt/QML/media files over a fragile single-file EXE. Place the runnable package under `artifacts/qt_quick_showcase/` and verify it from outside the source directory without relying on the development virtual environment or an installed Qt SDK.

Also provide a source fallback launcher that detects a supported Python installation, creates a dedicated local virtual environment, installs only the pinned requirements, and starts the demo. It must report a clear, actionable message if Python or network access is unavailable. Never install packages into the global Python environment.

If a self-contained package cannot be completed, record the exact blocker, preserve the best runnable fallback, and state precisely what the owner must install or click. Do not call a package portable unless the clean-environment launch was actually verified.

## Out of scope

- Implementing the full framework or moving code into its production package.
- Selecting Qt Quick as the final framework architecture; this showcase supplies owner-review evidence only.
- Building a full CSS parser, generalized layout inference, or a broad widget catalog.
- Promising Android/Linux/macOS support or testing those builds.
- Requiring cameras, microphones, touch hardware, internet media streams, or third-party media downloads for the main demo to launch.
- Claiming broad device, codec, or performance coverage from one machine.

## Acceptance criteria

- `demos/qt_quick_showcase/START_HERE.md` clearly tells the owner which file to double-click and what to expect.
- A portable Windows package is produced and launches successfully from a clean location without using `.venv-qt-quick`, when the available toolchain permits. Otherwise the task report clearly identifies the blocker and the source fallback is launchable using its documented prerequisites.
- The source fallback uses its own pinned environment and does not alter global Python packages.
- The owner-facing Python example is short, readable, and shows the intended abstraction without leaking QML or bridge internals.
- The application exposes interactive demonstrations for shapes/hit testing, themes/overrides, animation, repeated and dynamic controls, multiple windows, input, media/device enumeration, and a performance playground. Optional hardware-dependent cases fail gracefully and are clearly labeled.
- The demo has been exercised with an automated/synthetic smoke scenario and with an actual visible launch on Windows. Report separately what Codex verified and what still needs the owner's physical interaction or subjective judgment.
- Any performance numbers are described as machine- and scene-specific observations; no screenshot or swap callback is presented as a universal FPS guarantee.
- `README.md` or `START_HERE.md` records tested environment, exact launch instructions, package contents, known limitations, and recovery steps.
- Findings are added below. Do not change the architecture overview to mark Qt adopted.

## Verification

On Windows, run the app through the packaged launch path and the source fallback. Exercise the major sections using synthetic input where reliable, capture representative screens, and inspect logs for QML/media errors. Test the portable package from a clean directory with the development venv and Qt SDK paths unavailable. Run the stress levels and record timings plus hardware details, but do not treat them as a cross-machine benchmark.

Leave a concise manual checklist for the owner to check physical mouse/keyboard, audible output, perceived animation smoothness, optional devices, and visual preferences. Clearly separate those owner checks from Codex's automated verification.

## Report

Summarize:

- Source files and the owner-facing API shape.
- Exact double-click launch path and whether the EXE was verified independently.
- Exact source-fallback requirements and behavior.
- Scenarios exercised, evidence, and unverified hardware-dependent behavior.
- Performance observations with machine details and measurement limits.
- Any packaging or QML deployment issues.
- Manual checklist for the owner.
- Whether the result is ready for personal evaluation; do not make the architecture decision for the owner.

## Findings

Implemented the isolated Windows owner-evaluation showcase under `demos/qt_quick_showcase/`, with a folder package under `artifacts/qt_quick_showcase/`. The Python-only [`example_app.py`](../../demos/qt_quick_showcase/example_app.py) declares `App`, `Theme`, `Window`, two `Button`s, a `Star`, callbacks and `Pulse`, then runs the app. `showcase_api.py` is a bounded preview; the eight-page layout remains internal QML. `ButtonControl.qml` uses Qt Quick Controls with gradients, stroke/focus/hover/press states; `StarControl.qml` uses Qt Quick Shapes and polygon hit testing. `showcase_runtime.py` owns theme switching, per-control override, dynamic IDs, second window, media/device diagnostics and approximate performance instrumentation. No code was moved into the framework package, and no architecture decision was made.

**Owner launch:** Double-click `artifacts/qt_quick_showcase/START_SHOWCASE.cmd`, keeping the complete `QtQuickShowcase.dist/` folder beside it. The runnable EXE is `QtQuickShowcase.dist/example_app.exe`. The approximately 207 MB folder includes the Python runtime, PySide6/Qt/QML and multimedia files, local QML controls, and a synthetic MP4. The source fallback is `demos/qt_quick_showcase/START_SOURCE.cmd`: it detects 64-bit Python 3.13/3.12 via `py` or `python`, creates `.venv-showcase` locally, installs only `PySide6==6.11.2` there if missing, and starts the demo. It reports Python/setup/network failures without installing into global Python. [`START_HERE.md`](../../demos/qt_quick_showcase/START_HERE.md) contains the exact click paths, recovery steps, contents and manual checklist.

**Actual platform and commands:** Windows 11 Pro build 26200, Python 3.13.9, PySide6/Qt 6.11.2, Intel Core i3-12100F (8 logical processors), 16 GB RAM, NVIDIA RTX 5060 Ti driver 32.0.15.9636; active Qt Quick backend Direct3D11. `cmd /c demos\qt_quick_showcase\START_SOURCE.cmd --probe` exited 0. A fresh copy of the source outside the repository was run through `START_SOURCE.cmd --probe`; it created a dedicated venv, installed the pinned dependency and exited 0. `pyside6-deploy` in `standalone` mode built the package in a clean staging directory, using Nuitka 4.2.2. A copy of the final package under `%TEMP%\qt_quick_showcase_final_test_0005\` was launched through `START_SHOWCASE.cmd --probe` with `PATH` limited to Windows folders and Python/Qt/QML environment overrides removed; it exited 0 with `failures=[]`. This verifies independent launch on this Windows machine without the development venv or a Qt SDK path, not on another computer or clean VM.

**Scenarios and evidence:** The visible QtTest smoke clicked three distinct Python callbacks and the star interior; its empty corner did not activate. Synthetic Space and Enter activated focused button/star. Dark theme, animation changes/stop/replay, adding and removing an independent dynamic control, a visible second top-level window, local MP4/WAV playback states, audio/camera enumeration, 50 and 400 animated elements with a generated 2048 × 2048 image, and QML diagnostics were exercised. Both final smoke runs reported no QML errors; no media error was logged. Representative window grabs and machine-readable source/package reports are in `demos/qt_quick_showcase/captures/`. A video frame is visible in the media capture. PlaybackState reached PlayingState for both local samples, but audibility was not checked.

**Performance observation, not FPS:** In the final source run, 50 items yielded 112 `frameSwapped` intervals, median 13.33 ms and p95 13.70 ms, with a one-second process CPU observation of about 6.2% of one logical core. With 400 items, 136 intervals had median 13.35 ms and p95 13.60 ms, with CPU about 18.7%. In the final packaged run, medians were 13.33 ms for both levels; CPU samples were about 6.2% and 11.0%. These values depend on the machine, scene and momentary system load; swap callbacks are not true monitor FPS and do not establish perceived smoothness.

**Packaging issues:** An initial `pyside6-deploy` run failed at Nuitka's noninteractive Dependency Walker download prompt; rerunning with `--assume-yes-for-downloads` succeeded. `dumpbin` was unavailable, so the tool skipped its dependency scan. The first built folder lacked `Qt6Test.dll` for the optional smoke mode, although its normal UI loaded; the final folder includes it and the clean-path packaged smoke passed. A readable QML load failure dialog was added but its failure path was not exercised. Package reproduction on another PC, alternate graphics hardware, codecs and Windows versions remains unverified.

**Owner review at task completion:** The owner launched and explored the packaged showcase, liked its appearance and animations, and reported no notable functional problems beyond the observations recorded below. Their report supports personal evaluation of the Windows demo; it does not verify audio audibility, optional device capture, touch hardware, screen readers, DPI variation, another-PC launch, or perceived smoothness under every load. The owner subsequently accepted Qt Quick as the MVP foundation in ADR-0001.

**Owner review notes (2026-10-03):** The owner launched and explored the showcase, reported that it looked polished and responsive, and did not notice other functional problems. They observed a contrast bug in the bottom status strip when Windows is in dark mode and the app uses “Follow system”: the strip becomes pale while its text remains light. Source review confirms this is a demo palette-selection bug: `statusPillColor()` checks the selected mode (`Dark`) instead of the resolved system palette, while `bridge.ink` correctly follows the system palette. This is not a Qt Quick limitation. The owner also noticed the performance dots seeming to reverse in groups. The demo animates each dot between fixed coordinates using independent looping `NumberAnimation`s, with modulo-wrapped targets; it does not implement boundary reflection. That motion can look like groups wrapping/restarting and is a demo-scene behavior, not evidence of a Qt rendering limitation. Both observations are recorded for follow-up; the owner considers the showcase successful and did not request a fix in this task. This evaluation deliverable is therefore complete. Any follow-up fix should be a new task linked to TASK-0005.
