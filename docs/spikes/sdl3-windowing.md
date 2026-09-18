# Spike A: SDL3 windowing feasibility

Status: **Experimental research; no backend decision accepted.**
Date: 2026-09-19. Baseline: main `70f3fe2` (merged bootstrap PR).

## Question and provisional conclusion

Can SDL3 serve as a Windows-first Python platform/windowing layer?
The API-level evidence supports proceeding to a bounded renderer spike after
the Windows 11 manual smoke below. Two native windows, independent destruction,
window properties, resizing and SDL event delivery work with the selected pair.
This is not acceptance of SDL3 or PySDL3 for the framework. Visual behavior,
real input, mixed-DPI behavior and packaging remain gates. Per-pixel transparency
is explicitly **not visually confirmed**.

## Binding choice and dependency observations

The [SDL3 bindings catalogue](https://wiki.libsdl.org/SDL3/LanguageBindings)
lists [PySDL3](https://github.com/Aermoss/PySDL3) for Python. At research time
[PyPI](https://pypi.org/project/PySDL3/0.9.12b1/) offers `0.9.12b1`, released
2026-09-03, with Python 3.13/3.14 classifiers. It is a beta ctypes wrapper, not
an SDL-maintained Python API. Pin it in `examples/sdl3-requirements.txt` only.
Its binding headers identify SDL 3.4.16; use the matching official SDL runtime.

Alternatives considered: a hand-written ctypes subset reduces dependencies but
makes us responsible for ABI declarations and event union layouts; a custom
compiled extension adds a compiler and wheel matrix before feasibility is known.
Neither is justified for this experiment. SDL2 bindings would test a different
API and do not answer this task. The catalogue is not an exhaustive ecosystem audit.

The installed wheel declares `requests`, `aiohttp` and `packaging`, with further
transitive dependencies. Despite the pure-Python wheel, deployment needs a native
DLL matching process architecture. This is a reasonable research dependency,
not yet a minimal production dependency stack. Inspection of the installed
loader found update checks, automatic downloads and stub functions for missing
native symbols. Thus import success alone does not prove SDL loaded successfully.
The demo verifies the core binary and uses an explicit binary directory; it
disables metadata, downloading, system search, update checks and doc generation
before importing the binding. No network is needed at demo runtime.

[Upstream installation guidance](https://pysdl3.readthedocs.io/en/latest/install.html)
describes custom binaries. Pinning the wrapper alone does not pin the native
runtime or transitive dependencies. Frozen executables, clean-machine installs,
ARM64, macOS and Linux were not tested. PySDL3 is MIT; SDL is zlib-licensed.
Preserve upstream notices when redistributing; this does not choose a license
for Framework.

## Setup and runnable demo (Windows 11 x64 / PowerShell)

Run from the repository root with 64-bit Python 3.13 or 3.14:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip install -r examples/sdl3-requirements.txt
New-Item -ItemType Directory -Force .venv/sdl3 | Out-Null
Invoke-WebRequest https://github.com/libsdl-org/SDL/releases/download/release-3.4.16/SDL3-3.4.16-win32-x64.zip -OutFile .venv/sdl3/SDL3-3.4.16-win32-x64.zip
```

Before extraction, compare `Get-FileHash .venv/sdl3/SDL3-3.4.16-win32-x64.zip`
with the SHA256 observed for the official release download:
`4217944b4e51457af4a59c82d883f8443b3e65964b2acd8943484c492756c4b6`.
This is a reproducibility fingerprint of the fetched archive, not an independently
verified signature. [Official release and assets](https://github.com/libsdl-org/SDL/releases/tag/release-3.4.16).

```powershell
Expand-Archive .venv/sdl3/SDL3-3.4.16-win32-x64.zip -DestinationPath .venv/sdl3/runtime
.\.venv\Scripts\python.exe examples/sdl3_windowing.py --binary-dir .venv/sdl3/runtime
.\.venv\Scripts\python.exe examples/sdl3_windowing.py --binary-dir .venv/sdl3/runtime --windows 2
```

Windows can initially overlap; move the first aside or use the taskbar to select
the second. The client area is intentionally unrendered. Do not interpret its
contents as a rendering or transparency test. Keyboard controls affect only the
window receiving the event: **Esc** closes it, **B** toggles the native border,
**R** toggles resizability, **O** toggles whole-window opacity between 1 and 0.65.
Key releases, repeats, scancodes/modifiers, pointer motion, buttons and wheel are
logged. Borderless dragging/hit-testing is not implemented; use B to restore
the caption. Opacity 0 may make interaction difficult; use `--seconds 10` when
testing fully invisible windows.

Additional modes:

```powershell
.\.venv\Scripts\python.exe examples/sdl3_windowing.py --binary-dir .venv/sdl3/runtime --borderless --fixed-size --opacity 0.65
.\.venv\Scripts\python.exe examples/sdl3_windowing.py --binary-dir .venv/sdl3/runtime --transparent --seconds 15
# Non-visual API smoke, not a substitute for the checklist below:
.\.venv\Scripts\python.exe examples/sdl3_windowing.py --binary-dir .venv/sdl3/runtime --windows 2 --hidden --seconds 1
```

`--help` and deterministic tests require neither PySDL3 nor a DLL. A missing
binding, missing DLL or initialization failure produces a nonzero exit and an
error. Unsupported opacity/style operations are reported without killing the
demo so remaining capabilities can still be explored. Keep DLLs inside `.venv`;
no binaries or generated files belong in Git.

## Implementation boundaries and SDL findings

`examples/sdl3_windowing.py` is an executable experiment, not an importable
framework Window API. `src/framework`, its runtime requirements and wheel are
unchanged. `run` owns SDL initialization, a dictionary of window IDs to native
pointers, the one process event queue, and cleanup in `finally`, including partial
creation failures. SDL operations and event pumping stay on the main thread.
The binding exposes dynamically typed ctypes values; `Any` is limited to these
experimental native handles/events rather than introducing a wrapper hierarchy.

- `SDL_Init` returns a boolean in SDL3. Window creation returns a pointer;
  SDL errors are retrieved immediately when a call fails.
- `SDL_EVENT_WINDOW_CLOSE_REQUESTED` destroys only its named window. The loop
  continues while the dictionary is nonempty; `SDL_EVENT_QUIT` exits the entire
  application. Late window events for destroyed IDs are ignored.
- Resize, focus and other SDL window events are logged by name and ID. On size,
  pixel-size, display or scale changes, query dimensions and scaling again.
  [SDL DPI guidance](https://wiki.libsdl.org/SDL3/README-highdpi) distinguishes
  window coordinates, pixel density and display scale. On the tested Windows
  display all dimensions were physical pixels, density 1 and display scale 1;
  that does not imply all machines use scale 1. There is no invented separate
  pixel-density event: pixel-size/display-scale changes trigger fresh queries.
- `SDL_SetWindowBordered` and `SDL_SetWindowResizable` allow runtime toggles;
  startup flags support borderless and fixed-size experiments. A resizable flag
  does not supply resize grips for a custom borderless titlebar.
- [Opacity](https://wiki.libsdl.org/SDL3/SDL_SetWindowOpacity) is a whole-window
  scalar and can be unsupported. Setting 0.65 succeeded and read back as 0.65
  here. API success/readback is distinct from a visual compositor check.
- [Transparent window creation](https://wiki.libsdl.org/SDL3/SDL_CreateWindow)
  accepts `SDL_WINDOW_TRANSPARENT`, also exposed as
  `SDL_PROP_WINDOW_CREATE_TRANSPARENT_BOOLEAN` by property-based creation.
  Creation succeeded and the flag was reported. Without alpha-bearing rendered
  content, this cannot demonstrate per-pixel transparency, edge blending,
  compositor behavior or click-through. A renderer spike must draw opaque,
  partially transparent and zero-alpha regions over a contrasting background
  and verify presentation separately from whole-window opacity. No renderer was
  added here.
- The Windows-only `windows_hwnd` function uses
  [SDL_GetWindowProperties](https://wiki.libsdl.org/SDL3/SDL_GetWindowProperties)
  and `SDL_GetPointerProperty(..., SDL_PROP_WINDOW_WIN32_HWND_POINTER, NULL)`.
  It preserves pointer width and rejects a null handle. This is a borrowed HWND:
  do not destroy it through Win32, retain it after SDL destruction or assume its
  numeric value is never reused. No Win32 lifecycle logic leaks into the loop.
- The demo logs raw keyboard/mouse SDL events, not text composition. IME,
  accessibility, text input, drag/drop, capture, touch and event-loop embedding
  are future investigations. Logging every mouse event is diagnostic overhead,
  so this demo must not be used as a performance benchmark.

## Evidence and limits

Local API probes: Windows build `10.0.26200.0`, x64 Python 3.13.9,
PySDL3 0.9.12b1, official SDL 3.4.16, `windows` video driver.

| Check | Result / strength of evidence |
| --- | --- |
| Deterministic pytest | 13 tests including existing import smoke; lifecycle, duplicate/last close, quit, partial failure, cleanup, invalid opacity, HWND guard and pointer-width handling; no native SDL |
| Ruff, formatting, strict mypy | Passed locally |
| Import example, build and wheel smoke | Passed locally; see PR for final CI results |
| One/two hidden native windows | Passed; distinct nonzero HWNDs, clean shutdown |
| Fixed-size/borderless/transparent creation | Native calls succeeded; reported flags matched |
| Whole-window opacity | Set/get 0.65 succeeded; visual result unverified |
| Resize and runtime border/resize toggles | One-off local native probe passed; sizes 720x480 then 800x500, flags updated |
| HWND native validity | One-off local probe used Win32 IsWindow: both valid initially; first invalid after its destruction while second stayed valid |
| SDL event queue | One-off local probe pushed synthetic keyboard, motion, button, wheel, focus and close events; dispatch succeeded; survivor could still resize |
| Physical input, actual focus changes | Not manually verified; synthetic events do not establish OS input routing |
| Mixed-DPI / monitor transitions | Not verified; only initial density/scale and actual resize/pixel-size events observed |
| Per-pixel transparency | Flag/API available; not visually verified |

The one-off native probe is local research evidence, not part of pytest or CI.
CI retains the bootstrap Windows 3.13/3.14 matrix, including wheel validation;
it exercises the deterministic tests without installing SDL. Desktop checks are
manual to avoid depending on hosted runner compositor/focus/monitor state.

## Manual smoke acceptance (Windows 11)

Record OS build, Python architecture/version, printed binding/SDL versions,
video driver, monitor scaling and pass/fail notes. Repeat with Python 3.14.

1. Start the single-window command. Expect an OS window and nonzero HWND in the
   console. Resize via native edges; check `RESIZED`/`PIXEL_SIZE_CHANGED` and
   updated dimensions. Close via X; process should return exit code 0.
2. Start two windows, move them apart. Click/Alt-Tab between them; expect distinct
   IDs in `FOCUS_GAINED`/`FOCUS_LOST`. Type, hold/release keys, move/click the mouse
   and scroll over each. Verify routing, coordinates, repeats and button states.
3. Close the first via X or Alt-F4. The second must remain responsive to resize
   and input. Close the last; process exits. Repeat in reverse order and with Esc.
4. Press B, R, then B/R again. Confirm border and resizing behavior changes only
   for the selected window and matches logged flags. Also run startup
   `--borderless --fixed-size`. Restore border with B to use native edge dragging.
5. Press O twice with another application behind the window. Compare 0.65 with
   1.0 visually; retain the return/readback logs. Record unsupported/failure
   messages. This only validates uniform opacity.
6. Move between monitors at different scale settings (e.g. 100% and 150%/200%).
   Record display, scale and pixel-size events plus queried values. If only one
   monitor is available, mark this untested rather than passed.
7. Run `--transparent`, optionally with `--borderless`. Record creation and flag
   results or the exact error. Mark per-pixel transparency **unverified**, whatever
   the blank client area appears to show. It requires a later renderer probe.
8. Close after toggles, rerun the demo and interrupt from the console. Check that
   no demo windows remain. Do not infer full resource-leak freedom from this.

## Next decision

No blocker was found in the tested windowing APIs. Proceed conditionally with
a small renderer/presentation experiment once real-input, multi-window and DPI
smoke results are reviewed. That experiment should validate alpha composition,
surface resize and independent presentation on two HWNDs before accepting a
backend. Resolve native binary provisioning and binding maintenance risks before
production packaging. No Accepted SDL3 ADR or final Window contract is created.
