"""Small Python-only authoring model for this isolated experiment."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Pulse:
    duration_ms: int = 420
    peak_scale: float = 1.06


@dataclass(frozen=True)
class Theme:
    surface: str = "#f4f1fa"
    ink: str = "#29243a"
    accent: str = "#7756d8"
    star: str = "#ffc857"


@dataclass(frozen=True)
class Control:
    id: str
    kind: str  # "button" or "star" in this bounded prototype
    text: str
    on_click: Callable[[], None]
    fill: str | None = None
    pulse: Pulse | None = None


@dataclass(frozen=True)
class Window:
    title: str
    children: tuple[Control, ...]
    width: int = 600
    height: int = 460
