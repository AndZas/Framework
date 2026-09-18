"""Spike A: direct SDL3 calls, deliberately outside the framework package.

See docs/spikes/sdl3-windowing.md for setup and the manual smoke procedure.
"""

import argparse
import ctypes
import importlib
import math
import os
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any


def load_sdl(binary_dir: Path) -> ModuleType:
    """Load explicitly provisioned binaries without import-time network access."""
    binary_dir = binary_dir.resolve(strict=True)
    if not binary_dir.is_dir():
        raise ValueError("--binary-dir must be a directory containing SDL3")
    if "sdl3" in sys.modules:
        raise RuntimeError("Run this spike in a fresh Python process")
    os.environ.update(
        SDL_BINARY_PATH=str(binary_dir),
        SDL_DISABLE_METADATA="1",
        SDL_DOWNLOAD_BINARIES="0",
        SDL_FIND_BINARIES="0",
        SDL_CHECK_VERSION="0",
        SDL_DOC_GENERATOR="0",
    )
    sdl = importlib.import_module("sdl3")
    if sdl.SDL_GET_BINARY("SDL3") is None:
        raise RuntimeError(f"SDL3 binary not loaded from {binary_dir}")
    print(f"PySDL3={sdl.__version__} SDL={sdl.SDL_GetVersion()}")
    print(f"SDL revision={sdl.SDL_GetRevision()!r} binary_dir={binary_dir}")
    return sdl


def error(sdl: ModuleType, operation: str) -> RuntimeError:
    return RuntimeError(f"{operation}: {sdl.SDL_GetError()!r}")


def windows_hwnd(sdl: ModuleType, window: Any) -> int:
    """Borrow an HWND; SDL owns it and invalidates it on window destruction."""
    if sys.platform != "win32":
        raise RuntimeError("HWND acquisition is Windows-only")
    properties = sdl.SDL_GetWindowProperties(window)
    if not properties:
        raise error(sdl, "SDL_GetWindowProperties")
    hwnd = sdl.SDL_GetPointerProperty(
        properties, sdl.SDL_PROP_WINDOW_WIN32_HWND_POINTER, None
    )
    if not hwnd:
        raise error(sdl, "SDL_GetPointerProperty(HWND)")
    return int(hwnd)


def report_window(sdl: ModuleType, window: Any) -> None:
    width, height, pixels_w, pixels_h = (ctypes.c_int() for _ in range(4))
    if not sdl.SDL_GetWindowSize(window, ctypes.byref(width), ctypes.byref(height)):
        raise error(sdl, "SDL_GetWindowSize")
    if not sdl.SDL_GetWindowSizeInPixels(
        window, ctypes.byref(pixels_w), ctypes.byref(pixels_h)
    ):
        raise error(sdl, "SDL_GetWindowSizeInPixels")
    print(
        f"window={sdl.SDL_GetWindowID(window)} "
        f"size={width.value}x{height.value} pixels={pixels_w.value}x{pixels_h.value} "
        f"density={sdl.SDL_GetWindowPixelDensity(window):g} "
        f"display_scale={sdl.SDL_GetWindowDisplayScale(window):g} "
        f"flags={sdl.SDL_GetWindowFlags(window):#x}"
    )


def set_opacity(sdl: ModuleType, window: Any, value: float) -> None:
    if not sdl.SDL_SetWindowOpacity(window, value):
        print(error(sdl, f"SDL_SetWindowOpacity({value}) unsupported/failed"))
        return
    actual = sdl.SDL_GetWindowOpacity(window)
    if actual < 0:
        raise error(sdl, "SDL_GetWindowOpacity")
    print(f"opacity requested={value:g} reported={actual:g}; visual check pending")


def close_window(sdl: ModuleType, windows: dict[int, Any], window_id: int) -> None:
    window = windows.pop(window_id, None)
    if window is not None:
        sdl.SDL_DestroyWindow(window)
        print(f"closed window={window_id}; remaining={len(windows)}")


def handle_event(sdl: ModuleType, event: Any, windows: dict[int, Any]) -> bool:
    """Return False only for an application-wide quit. Close is per-window."""
    kind = event.type
    if kind == sdl.SDL_EVENT_QUIT:
        print("SDL_EVENT_QUIT: exiting application")
        return False
    if sdl.SDL_EVENT_WINDOW_FIRST <= kind <= sdl.SDL_EVENT_WINDOW_LAST:
        window_id = int(event.window.windowID)
        window = windows.get(window_id)
        if window is None:
            return True  # Late events for an already destroyed window.
        name = next(
            (
                name
                for name in dir(sdl)
                if name.startswith("SDL_EVENT_WINDOW_") and getattr(sdl, name) == kind
            ),
            str(kind),
        )
        print(
            f"{name} window={window_id} data={event.window.data1},{event.window.data2}"
        )
        if kind == sdl.SDL_EVENT_WINDOW_CLOSE_REQUESTED:
            close_window(sdl, windows, window_id)
        elif kind in (
            sdl.SDL_EVENT_WINDOW_RESIZED,
            sdl.SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED,
            sdl.SDL_EVENT_WINDOW_DISPLAY_SCALE_CHANGED,
            sdl.SDL_EVENT_WINDOW_DISPLAY_CHANGED,
        ):
            report_window(sdl, window)
    elif kind in (sdl.SDL_EVENT_KEY_DOWN, sdl.SDL_EVENT_KEY_UP):
        key = event.key
        print(
            f"key window={key.windowID} down={key.down} key={key.key} "
            f"scan={key.scancode} mod={key.mod} repeat={key.repeat}"
        )
        window = windows.get(int(key.windowID))
        if window is not None and kind == sdl.SDL_EVENT_KEY_DOWN and not key.repeat:
            if key.key == sdl.SDLK_ESCAPE:
                close_window(sdl, windows, int(key.windowID))
            elif key.key == sdl.SDLK_O:
                current = sdl.SDL_GetWindowOpacity(window)
                if current < 0:
                    print(error(sdl, "SDL_GetWindowOpacity"))
                else:
                    set_opacity(sdl, window, 0.65 if current > 0.9 else 1.0)
            elif key.key in (sdl.SDLK_B, sdl.SDLK_R):
                flags = sdl.SDL_GetWindowFlags(window)
                if key.key == sdl.SDLK_B:
                    ok = sdl.SDL_SetWindowBordered(
                        window, bool(flags & sdl.SDL_WINDOW_BORDERLESS)
                    )
                else:
                    ok = sdl.SDL_SetWindowResizable(
                        window, not bool(flags & sdl.SDL_WINDOW_RESIZABLE)
                    )
                if not ok:
                    print(error(sdl, "window style toggle"))
                report_window(sdl, window)
    elif kind == sdl.SDL_EVENT_MOUSE_MOTION:
        mouse = event.motion
        print(f"motion window={mouse.windowID} xy={mouse.x:g},{mouse.y:g}")
    elif kind in (sdl.SDL_EVENT_MOUSE_BUTTON_DOWN, sdl.SDL_EVENT_MOUSE_BUTTON_UP):
        button = event.button
        print(
            f"button window={button.windowID} button={button.button} "
            f"down={button.down} xy={button.x:g},{button.y:g}"
        )
    elif kind == sdl.SDL_EVENT_MOUSE_WHEEL:
        wheel = event.wheel
        print(
            f"wheel window={wheel.windowID} xy={wheel.x:g},{wheel.y:g} "
            f"direction={wheel.direction}"
        )
    return True


def run(sdl: ModuleType, args: argparse.Namespace) -> None:
    """Main thread owns SDL, the event queue and all window lifetimes."""
    windows: dict[int, Any] = {}
    try:
        if not sdl.SDL_Init(sdl.SDL_INIT_VIDEO | sdl.SDL_INIT_EVENTS):
            raise error(sdl, "SDL_Init")
        print(f"video_driver={sdl.SDL_GetCurrentVideoDriver()!r}")
        flags = sdl.SDL_WINDOW_HIGH_PIXEL_DENSITY
        if not args.fixed_size:
            flags |= sdl.SDL_WINDOW_RESIZABLE
        if args.borderless:
            flags |= sdl.SDL_WINDOW_BORDERLESS
        if args.transparent:
            flags |= sdl.SDL_WINDOW_TRANSPARENT
        if args.hidden:
            flags |= sdl.SDL_WINDOW_HIDDEN
        for index in range(args.windows):
            title = (
                f"SDL3 spike {index + 1} | Esc close / B border / R resize / O opacity"
            )
            window = sdl.SDL_CreateWindow(
                title.encode(),
                640,
                420,
                flags,
            )
            if not window:
                raise error(sdl, "SDL_CreateWindow")
            window_id = int(sdl.SDL_GetWindowID(window))
            if not window_id:
                sdl.SDL_DestroyWindow(window)
                raise error(sdl, "SDL_GetWindowID")
            windows[window_id] = window
            report_window(sdl, window)
            if sys.platform == "win32":
                print(f"window={window_id} HWND={windows_hwnd(sdl, window):#x}")
            set_opacity(sdl, window, args.opacity)
            if args.transparent:
                accepted = bool(
                    sdl.SDL_GetWindowFlags(window) & sdl.SDL_WINDOW_TRANSPARENT
                )
                print(
                    f"transparent flag reported={accepted}; "
                    "per-pixel transparency NOT visually verified (no renderer)"
                )
        print("No renderer: blank client areas are expected. Keyboard/mouse go to log.")
        deadline = time.monotonic() + args.seconds if args.seconds else None
        event = sdl.SDL_Event()
        while windows:
            if deadline is not None and time.monotonic() >= deadline:
                break
            sdl.SDL_ClearError()
            if sdl.SDL_WaitEventTimeout(ctypes.byref(event), 50):
                if not handle_event(sdl, event, windows):
                    break
            elif sdl.SDL_GetError():
                raise error(sdl, "SDL_WaitEventTimeout")
    finally:
        for window_id in list(windows):
            close_window(sdl, windows, window_id)
        sdl.SDL_Quit()


def unit_interval(value: str) -> float:
    result = float(value)
    if not math.isfinite(result) or not 0 <= result <= 1:
        raise argparse.ArgumentTypeError("expected a finite number between 0 and 1")
    return result


def duration(value: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise argparse.ArgumentTypeError("expected finite seconds >= 0")
    return result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--binary-dir", type=Path, required=True)
    result.add_argument("--windows", type=int, choices=(1, 2), default=1)
    result.add_argument("--borderless", action="store_true")
    result.add_argument("--fixed-size", action="store_true")
    result.add_argument("--transparent", action="store_true")
    result.add_argument("--opacity", type=unit_interval, default=1.0)
    result.add_argument(
        "--seconds",
        type=duration,
        default=0.0,
        help="exit after this many seconds; 0 waits for close",
    )
    result.add_argument(
        "--hidden",
        action="store_true",
        help="API smoke only; does not verify visual behavior",
    )
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        run(load_sdl(args.binary_dir), args)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        print(f"SDL3 spike failed: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
