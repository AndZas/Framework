# Qt Quick feasibility spike (Windows, 2026-10-03)

This is an isolated experiment, not a framework API or backend selection. `main.py` creates two independent QML `Window` instances. The main scene exercises shapes, styling, animation, input, multimedia, and a repeatable rendering load.

## Setup and commands

Run in PowerShell from the repository root. Python 3.13 was chosen for the experiment; the observed interpreter was **3.13.9**. The pinned PySide6 and Qt versions were **6.11.2**.

```powershell
py -3.13 -m venv .venv-qt-quick
.\.venv-qt-quick\Scripts\python.exe -m pip install -r prototypes\qt_quick_spike\requirements.txt
.\.venv-qt-quick\Scripts\python.exe prototypes\qt_quick_spike\main.py
.\.venv-qt-quick\Scripts\python.exe prototypes\qt_quick_spike\main.py --probe
.\.venv-qt-quick\Scripts\python.exe prototypes\qt_quick_spike\main.py --probe --media prototypes\qt_quick_spike\sample.mp4
.\.venv-qt-quick\Scripts\python.exe prototypes\qt_quick_spike\main.py --vulkan --probe --media prototypes\qt_quick_spike\sample.mp4
```

The interactive run starts with a generated one-second WAV tone. `--media` replaces that source with a local file. Click the theme button, rounded button, star, and stress panel; press a key while the main window has focus. `S` toggles stress. `--probe` sends Qt-synthesized pointer and keyboard events, saves window captures, measures ten seconds of stress, and exits. The images are in this directory. It is a repeatable diagnostic, not a benchmark.

The sample MP4 contains a two-second synthetic test pattern and sine tone generated for this experiment with local `ffmpeg`:

```powershell
ffmpeg -hide_banner -loglevel error -f lavfi -i testsrc2=size=320x180:rate=24 -f lavfi -i sine=frequency=440:sample_rate=22050 -t 2 -c:v libx264 -pix_fmt yuv420p -c:a aac -y prototypes\qt_quick_spike\sample.mp4
```

The sample has no third-party visual or audio content. FFmpeg was used only to make the sample; it is not needed to run the prototype. The large 2048 × 2048 image and WAV tone are generated with PySide6/Python at runtime. No non-Qt runtime package was needed.

## Environment and actual observations

- Windows 11 Pro, build 26200; Intel Core i3-12100F; 16 GB RAM; NVIDIA GeForce RTX 5060 Ti, driver 32.0.15.9636.
- Python 3.13.9; PySide6 6.11.2; Qt 6.11.2. Default run reported `Graphics API=Direct3D11`. Optional `--vulkan` run reported `Graphics API=Vulkan` and exited normally. No direct Vulkan rendering code was written.
- The runs reported four audio outputs (G435 headset and three virtual devices), four audio inputs (USB LCS microphone and three virtual devices), and one camera (`DroidCam Video`). Enumeration alone does not test capture or physical device operation.
- Default video probe: two distinct windows created; `PlaybackState.PlayingState` at 0.5 s; video test pattern visible in [default idle capture](probe-default-idle.png). The generated WAV probe also reported `PlayingState`. Audibility and captured audio output were not independently verified.
- Qt-synthesized input in the default probe: rounded count `1` after center and still `1` after transparent corner; star count `1` after visible interior and still `1` after empty corner; theme became dark; keyboard count `1` with main window active and `inputItem` focused; background pointer count `2`. The [default stress capture](probe-default-stress.png) shows the dark theme and animated items.
- Animation's logged x coordinate changed across the default video and WAV probes (596.5 and 603.8 at sampling); screenshot positions also changed. It remained active while the stress scene ran.
- Default video stress run: 400 animated circles over a generated 2048 × 2048 image, 9.95 s, 1990 `frameSwapped` signals, median interval 5.0 ms, p95 5.6 ms, maximum 11.4 ms, process CPU time 29.4% of one logical core. Optional Vulkan run: 9.25 s, 1851 signals, median 4.8 ms, p95 9.0 ms, maximum 14.6 ms, process CPU time 35.1% of one logical core. These are window swap callbacks, not a display refresh or user-visible frame rate. Visible stutter was not assessed live; still captures cannot establish it. These numbers apply only to this machine and scene.

| Scenario | Result | Evidence and extra implementation |
| --- | --- | --- |
| Rounded control, gradient, border, transparency, click area | works with extra implementation | `Rectangle` appearance plus explicit rounded-corner hit test in `MouseArea`; center click counted, transparent corner rejected. |
| Star control, gradient, border, transparency, click area | works with extra implementation | `Canvas` path and the same polygon points used for ray-cast hit testing; visible interior counted, empty corner rejected. Anti-aliased edge and stroked border precision remain unmeasured. Arbitrary visual geometry did not define its input region automatically. |
| Shared theme values and per-control override | works | Switch changed surface, ink, accent, gradients, and star color; orange override stayed fixed. A thin QML property mapping was used because it tests runtime propagation directly without building a general CSS parser. |
| Animation while scene updates | works | Infinite position/rotation animation observed through changing x value and captures. |
| Independent top-level windows | works | Python separately created `Main.qml` and `Secondary.qml`; log reported two distinct objects and both were shown. |
| Keyboard and pointer | works | Qt-synthesized `A` reached focused item; pointer clicks and hit tests logged. Physical keyboard/mouse operation was not separately observed. |
| Touch | not tested | No touch hardware or injected touch sequence used. |
| Audio playback | works with extra implementation | `QMediaPlayer` + `AudioOutput`, generated WAV; `PlayingState` observed. Audible output not verified. |
| Video playback | works | `QMediaPlayer` + `VideoOutput`, local synthetic MP4; playback state and frame in capture observed. Other codecs not tested. |
| Audio and camera devices | works for enumeration; not tested for capture | `QMediaDevices.audioOutputs()`, `audioInputs()`, `videoInputs()` returned devices; capture was not attempted. |
| Default graphics backend | works | Runtime `rendererInterface().graphicsApi()` returned Direct3D11. |
| Optional Vulkan diagnostic | works on this machine | Requested before app creation; runtime API returned Vulkan and probe completed. |
| Stress frame pacing and CPU | works for measurement | `frameSwapped` timestamps and `time.process_time()` over ~10 s. |
| Visible stutter under stress | not tested | A live visual assessment was unavailable; still captures show composition only. |

## Limits and next step

Hit testing currently duplicates geometry in script. The small rounded and star examples can match their visible interiors, but exact anti-aliased edge behavior and maintaining complex paths would need another experiment. The large image is displayed cropped in the 710 × 250 stress panel; its source remains 2048 × 2048. Frame swaps are uncapped on this setup, so the ~200/s counts are not a performance guarantee. Touch, capture, audio audibility, codec coverage, and deployment remain unverified.

For Android, current [official Qt for Python deployment guidance](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-android-deploy.html) describes `pyside6-android-deploy`, Android SDK/NDK and Android wheels; it says the tool currently requires a Unix (Linux or macOS) host. Cross-compiling some Android wheels currently requires Linux. This is a documentation assessment only; no Android build or runtime test was done.

**Recommendation:** keep evaluating Qt Quick. The next smallest experiment is an edge-accurate hit test and live frame-pacing observation on the intended display, followed separately by a physical touch and multimedia capture test if those become requirements. This is input to owner review, not an architecture decision.
