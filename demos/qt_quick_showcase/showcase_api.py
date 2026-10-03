"""Small, deliberately provisional Python authoring surface for this demo."""

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Theme:
    accent: str = "#6c5ce7"
    surface: str = "#f5f6fb"
    ink: str = "#19213a"
    star: str = "#ffcc66"


@dataclass(frozen=True)
class Pulse:
    duration_ms: int = 900
    peak_scale: float = 1.10


@dataclass(frozen=True)
class Button:
    id: str
    text: str
    on_click: Callable[[], None]
    fill: str | None = None
    animation: Pulse | None = None


@dataclass(frozen=True)
class Star:
    id: str
    on_click: Callable[[], None]


@dataclass
class Window:
    title: str
    controls: list[Button | Star] = field(default_factory=list)

    def add(self, *controls: Button | Star) -> None:
        self.controls.extend(controls)


class App:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.windows: list[Window] = []

    def add(self, window: Window) -> Window:
        self.windows.append(window)
        return window

    def run(self) -> int:
        from showcase_runtime import run
        return run(self)
