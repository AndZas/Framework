"""The small, deliberately shared Python authoring surface for both experiments."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Theme:
    surface: str = "#f4f1fa"
    ink: str = "#29243a"
    accent: str = "#7756d8"
    star: str = "#ffc857"


@dataclass(frozen=True)
class Pulse:
    duration_ms: int = 420
    peak_scale: float = 1.08


@dataclass
class Label:
    text: str


@dataclass
class Button:
    text: str
    on_click: Callable[[], None]
    fill: str | None = None
    pulse: Pulse | None = None


@dataclass
class Star:
    on_click: Callable[[], None]


@dataclass
class Window:
    title: str
    children: tuple[Label | Button | Star, ...]
    width: int = 420
    height: int = 350
