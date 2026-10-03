# TASK-0001: Qt Quick feasibility spike

**Status:** Done
**Type:** Experiment
**Depends on:** None
**Likely files:** `prototypes/qt_quick_spike/`, this task's findings section

## Goal

Build and run a small, isolated PySide6 + Qt Quick prototype on Windows to determine whether Qt Quick is a practical candidate for this project's visual, input, multimedia, windowing, and performance needs.

This is an evaluation only. It does not select Qt as the final backend or define the public framework API.

## Context to read

- `AGENTS.md`
- `docs/architecture/overview.md`
- `docs/development.md`

Do not read the architecture chat history as a substitute for this task. Ask the user only if a blocker cannot be resolved from the repository and task.

## Scope

Create a self-contained runnable prototype under `prototypes/qt_quick_spike/`. Keep it separate from any future production package. Use PySide6 to host a Qt Quick scene; QML may be used internally for this experiment.

Implement only enough UI to exercise the following:

1. A rounded control and a custom star-shaped control, including a gradient fill, border, partial transparency, and a click/tap interaction. Check whether the visible shape and clickable area can match.
2. A theme switch that changes several shared design values at runtime, plus a per-control override. Use a small CSS-inspired style input or document why a thin Python/theme mapping is a better first experiment; do not implement a general CSS engine.
3. A short property animation or keyframe sequence and a way to observe its behavior while the scene updates.
4. Two independently created top-level Qt Quick windows.
5. Keyboard and pointer input inside the application. If touch hardware is unavailable, document that touch remains unverified rather than claiming it works.
6. Audio playback and video playback in the scene if a local sample/media source is readily available. Enumerate available audio input/output and camera devices. If a device or media source is unavailable, record the API path and mark runtime behavior unverified.
7. Identify the active Qt Quick graphics backend at runtime. Attempt Vulkan only as an optional diagnostic if the installed Qt build and device support it; preserve the default-backend run as the baseline and record failures without making Vulkan mandatory.
8. A small repeatable rendering stress scenario: several hundred moving or animated visual items and a large image, with observations on frame pacing, CPU use, and visible stutter on the machine used. This is a qualitative spike, not a cross-machine benchmark or performance guarantee.

Provide a `README.md` with environment setup, run instructions, media source/license notes, and the exact observations collected. Pin the PySide6 dependency to the version actually used in the prototype's dependency file.

## Out of scope

- Building the framework's production API, widget library, theme language, or renderer.
- Shipping a reusable application or installer.
- Writing custom C++ renderer code, direct Vulkan rendering, global keyboard hooks, or arbitrary HID/gamepad support.
- Porting or packaging the prototype for Linux, macOS, or Android.
- Claiming support for every media codec, device, or GPU.
- Changing the provisional architecture decision without owner review.

## Acceptance criteria

- The prototype launches on the stated Windows environment and each implemented scenario can be demonstrated or its failure recorded.
- The star control has a documented hit-test result; no assumption is made that arbitrary visual geometry automatically defines input geometry.
- Theme switching and animation can be observed at runtime.
- The report distinguishes `works`, `works with extra implementation`, `not tested`, and `blocked/unsupported` for each scenario.
- The report includes Qt/PySide6/Python versions, Windows version, GPU/backend information, commands used, observed limitations, and whether any non-Qt dependency was needed.
- Findings are added to the section below. Do not edit the architecture overview to mark Qt adopted.

## Verification

Run the prototype on Windows and exercise each scenario above. Record actual results and commands in the prototype README and the findings section below. Do not report a scenario as verified if it was only reasoned about from documentation.

Android is not a required build target for this spike. In the report, assess packaging feasibility from current official PySide6 documentation, call out that Android packaging may need a Unix build host, and distinguish that assessment from a runtime test.

## Report

Summarize:

- Files created and exact environment used.
- Scenario-by-scenario results and evidence.
- Extra code or dependencies needed for each scenario.
- Performance observations and their hardware-specific limits.
- Android packaging assessment and untested behavior.
- Remaining risks and the next smallest experiment, if needed.
- A recommendation: keep evaluating Qt Quick, reject it, or gather more evidence. This recommendation is input to an owner decision, not the decision itself.

## Findings

Implemented under `prototypes/qt_quick_spike/`: `main.py`, `Main.qml`, `Secondary.qml`, pinned `requirements.txt`, a synthetic `sample.mp4`, probe captures, and a detailed `README.md`. No framework package or architecture decision record was changed.

**Actual environment (Windows, 2026-10-03):** Windows 11 Pro build 26200; Python 3.13.9; PySide6/Qt 6.11.2; Intel Core i3-12100F; 16 GB RAM; NVIDIA RTX 5060 Ti, driver 32.0.15.9636. Default graphics API reported Direct3D11. An optional Vulkan run reported Vulkan. No non-Qt runtime dependency was used. Local FFmpeg generated the included synthetic MP4; Python/PySide6 generated a WAV tone and 2048 × 2048 image at runtime.

**Commands actually run:**

```powershell
py -3.13 -m venv .venv-qt-quick
.\.venv-qt-quick\Scripts\python.exe -m pip install --disable-pip-version-check PySide6
ffmpeg -hide_banner -loglevel error -f lavfi -i testsrc2=size=320x180:rate=24 -f lavfi -i sine=frequency=440:sample_rate=22050 -t 2 -c:v libx264 -pix_fmt yuv420p -c:a aac -y prototypes\qt_quick_spike\sample.mp4
.\.venv-qt-quick\Scripts\python.exe prototypes\qt_quick_spike\main.py --probe
.\.venv-qt-quick\Scripts\python.exe prototypes\qt_quick_spike\main.py --probe --media prototypes\qt_quick_spike\sample.mp4
.\.venv-qt-quick\Scripts\python.exe prototypes\qt_quick_spike\main.py --vulkan --probe --media prototypes\qt_quick_spike\sample.mp4
```

**Scenario results:** Rounded and star controls **work with extra implementation**: explicit shape hit tests rejected transparent-corner clicks while accepting interior clicks (counts stayed `1` after the corner tests). Theme switch and per-control override **work**; the probe logged `dark=True` and the orange override remained visible. Position/rotation animation **works**, with a changed x value and captures. Two separately created top-level windows **work** (`distinct=True`). Qt-synthesized keyboard and pointer input **work** (`keys=1` with main window active, pointer events counted). Physical touch is **not tested**. Audio playback **works with extra implementation** using `QMediaPlayer`/`AudioOutput` and a generated WAV (`PlayingState` at 0.5 s); audibility is **not tested**. Video playback **works** using the synthetic MP4 and `VideoOutput`, with a frame visible in the capture. Device enumeration **works** (four outputs, four inputs, one `DroidCam Video` camera); actual capture is **not tested**. Default Direct3D11 and optional Vulkan API diagnostics **work** on this machine. Stress frame/CPU instrumentation **works**; visible stutter is **not tested** live.

**Stress observations:** Default video run used 400 animated circles and a 2048 × 2048 source image: 1990 `frameSwapped` callbacks in 9.95 s, median 5.0 ms, p95 5.6 ms, max 11.4 ms, and process CPU time 29.4% of one logical core. Optional Vulkan run: 1851 callbacks in 9.25 s, median 4.8 ms, p95 9.0 ms, max 14.6 ms, CPU 35.1% of one logical core. These callbacks are not a user-visible FPS measurement or cross-machine guarantee. Captures are in the prototype directory; they cannot establish whether stutter was visible.

**Limitations and next evidence:** Anti-aliased visual edges and stroke boundaries were not pixel-verified against input geometry. Touch, audio audibility, camera/microphone capture, other codecs, and physical input remain unverified. [Current official PySide6 Android packaging guidance](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-android-deploy.html) describes Android SDK/NDK and wheels, with `pyside6-android-deploy` currently requiring a Unix host; some wheel cross-compilation requires Linux. This is documentation assessment, not an Android build or runtime test. The next smallest experiment is edge-accurate hit testing and live frame-pacing observation on the intended display, then physical input/capture if required.

**Recommendation:** Keep evaluating Qt Quick. This is evidence for owner review, not selection of Qt as the framework backend. Full setup, results by scenario, media notes, and limitations are in `prototypes/qt_quick_spike/README.md`.
