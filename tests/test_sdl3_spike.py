"""Deterministic lifetime tests; no SDL import, DLL, desktop or network required."""

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

import pytest


@pytest.fixture
def spike() -> dict[str, Any]:
    return runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "examples" / "sdl3_windowing.py")
    )


@pytest.fixture
def sdl() -> SimpleNamespace:
    return SimpleNamespace(
        SDL_INIT_VIDEO=32,
        SDL_INIT_EVENTS=16384,
        SDL_WINDOW_HIGH_PIXEL_DENSITY=8192,
        SDL_WINDOW_RESIZABLE=32,
        SDL_EVENT_QUIT=256,
        SDL_EVENT_WINDOW_FIRST=512,
        SDL_EVENT_WINDOW_LAST=540,
        SDL_EVENT_WINDOW_CLOSE_REQUESTED=528,
        SDL_Init=Mock(return_value=True),
        SDL_CreateWindow=Mock(side_effect=[101, None]),
        SDL_GetWindowID=Mock(return_value=1),
        SDL_GetCurrentVideoDriver=Mock(return_value=b"fake"),
        SDL_GetError=Mock(return_value=b"injected failure"),
        SDL_DestroyWindow=Mock(),
        SDL_Quit=Mock(),
    )


def test_import_does_not_load_sdl(spike: dict[str, Any]) -> None:
    assert "sdl3" not in sys.modules
    assert callable(spike["main"])


def test_close_only_target_and_ignore_duplicate(
    spike: dict[str, Any], sdl: SimpleNamespace
) -> None:
    windows = {1: 101, 2: 102}
    event = SimpleNamespace(
        type=sdl.SDL_EVENT_WINDOW_CLOSE_REQUESTED,
        window=SimpleNamespace(windowID=1, data1=0, data2=0),
    )
    assert spike["handle_event"](sdl, event, windows)
    assert windows == {2: 102}
    assert spike["handle_event"](sdl, event, windows)
    sdl.SDL_DestroyWindow.assert_called_once_with(101)
    event.window.windowID = 2
    assert spike["handle_event"](sdl, event, windows)
    assert windows == {}
    assert sdl.SDL_DestroyWindow.call_count == 2
    sdl.SDL_Quit.assert_not_called()


def test_quit_requests_loop_exit_without_destroying_inside_handler(
    spike: dict[str, Any], sdl: SimpleNamespace
) -> None:
    windows = {1: 101, 2: 102}
    assert not spike["handle_event"](
        sdl, SimpleNamespace(type=sdl.SDL_EVENT_QUIT), windows
    )
    assert windows == {1: 101, 2: 102}  # run's finally owns cleanup.
    sdl.SDL_DestroyWindow.assert_not_called()


def test_partial_creation_failure_releases_first_window(
    spike: dict[str, Any], sdl: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = spike["run"]
    for name in ("report_window", "windows_hwnd", "set_opacity"):
        monkeypatch.setitem(run.__globals__, name, Mock(return_value=42))
    args = spike["parser"]().parse_args(["--binary-dir", ".", "--windows", "2"])
    with pytest.raises(RuntimeError, match="SDL_CreateWindow.*injected failure"):
        run(sdl, args)
    sdl.SDL_DestroyWindow.assert_called_once_with(101)
    sdl.SDL_Quit.assert_called_once()


def test_init_failure_still_quits(spike: dict[str, Any], sdl: SimpleNamespace) -> None:
    sdl.SDL_Init.return_value = False
    with pytest.raises(RuntimeError, match="SDL_Init"):
        spike["run"](sdl, argparse.Namespace())
    sdl.SDL_CreateWindow.assert_not_called()
    sdl.SDL_Quit.assert_called_once()


def test_loop_exception_releases_all_windows(
    spike: dict[str, Any], sdl: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = spike["run"]
    for name in ("report_window", "windows_hwnd", "set_opacity"):
        monkeypatch.setitem(run.__globals__, name, Mock(return_value=42))
    sdl.SDL_CreateWindow.side_effect = [101, 102]
    sdl.SDL_GetWindowID.side_effect = [1, 2]
    sdl.SDL_Event = Mock(side_effect=RuntimeError("event allocation failed"))
    args = spike["parser"]().parse_args(["--binary-dir", ".", "--windows", "2"])
    with pytest.raises(RuntimeError, match="event allocation failed"):
        run(sdl, args)
    assert [call.args[0] for call in sdl.SDL_DestroyWindow.call_args_list] == [101, 102]
    sdl.SDL_Quit.assert_called_once()


@pytest.mark.parametrize("value", ["nan", "inf", "-0.1", "1.1"])
def test_invalid_opacity_rejected(spike: dict[str, Any], value: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        spike["unit_interval"](value)


def test_hwnd_is_not_truncated(
    spike: dict[str, Any], sdl: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    sdl.SDL_GetWindowProperties = Mock(return_value=7)
    sdl.SDL_PROP_WINDOW_WIN32_HWND_POINTER = b"SDL.window.win32.hwnd"
    sdl.SDL_GetPointerProperty = Mock(return_value=0x123456789ABC)
    assert spike["windows_hwnd"](sdl, 101) == 0x123456789ABC
    sdl.SDL_GetPointerProperty.return_value = None
    with pytest.raises(RuntimeError, match="HWND"):
        spike["windows_hwnd"](sdl, 101)


def test_hwnd_platform_guard(
    spike: dict[str, Any], sdl: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    with pytest.raises(RuntimeError, match="Windows-only"):
        spike["windows_hwnd"](sdl, 101)
