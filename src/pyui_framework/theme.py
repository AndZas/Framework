"""Small CSS-inspired semantic themes; no browser CSS or Qt dependency."""
from dataclasses import dataclass
from pathlib import Path
import math
import re


class ThemeError(ValueError):
    """Invalid theme declaration; active state is never changed by validation."""


_COLORS = {"background", "foreground", "panel", "accent", "accent_text"}
_TOKENS = _COLORS | {"radius", "opacity", "gradient"}
_LOCAL = {
    "Window": {"background", "opacity"},
    "Label": {"foreground", "panel", "radius", "opacity"},
    "Button": {"accent", "accent_text", "radius", "opacity", "gradient"},
}


def _color(value, where):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ThemeError(f"{where}: expected #RRGGBB")
    return value.lower()


def _validate(values, source, allowed=_TOKENS):
    result = {}
    for key, value in values.items():
        where = f"{source}: {key}={value!r}"
        if key not in allowed:
            raise ThemeError(f"{where}: unsupported token; allowed: {', '.join(sorted(allowed))}")
        if key in _COLORS:
            value = _color(value, where)
        elif key == "gradient":
            if value is not None:
                if not isinstance(value, (tuple, list)) or len(value) != 2:
                    raise ThemeError(f"{where}: expected None or two #RRGGBB colors")
                value = tuple(_color(stop, where) for stop in value)
        else:
            maximum = 48 if key == "radius" else 1
            if type(value) not in (int, float):
                raise ThemeError(f"{where}: expected finite number in 0..{maximum}")
            try:
                valid = math.isfinite(value) and 0 <= value <= maximum
            except OverflowError:
                valid = False
            if not valid:
                raise ThemeError(f"{where}: expected finite number in 0..{maximum}")
            value = float(value)
        result[key] = value
    return result


def _style(values, kind):
    if values is None:
        values = {}
    if not isinstance(values, dict):
        raise ThemeError(f"{kind} style: expected a token dictionary or None")
    return _validate(values, f"{kind} style", _LOCAL[kind])


@dataclass(frozen=True, init=False)
class Theme:
    """Immutable partial theme. Missing values always use Light defaults."""
    name: str
    _values: tuple

    def __init__(self, name="Custom", **tokens):
        if not isinstance(name, str) or not name.strip():
            raise ThemeError("Theme name: expected a nonempty string")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "_values", tuple(sorted(_validate(tokens, name).items())))

    @property
    def tokens(self):
        """A defensive copy of explicitly authored canonical values."""
        return dict(self._values)

    @classmethod
    def load(cls, path):
        path = Path(path)
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            raise ThemeError(f"{path}: cannot read theme: {exc}") from exc
        return cls.parse(text, source=str(path))

    @classmethod
    def parse(cls, text, *, source="<theme>"):
        if not isinstance(text, str):
            raise ThemeError(f"{source}: expected theme text")
        block = re.fullmatch(r"\s*:theme\s*\{([^{}]*)\}\s*", text)
        if not block:
            raise ThemeError(f"{source}: expected exactly one :theme {{ ... }} block; comments/selectors unsupported")
        tokens = {}
        offset = block.start(1)
        parts = block.group(1).split(";")
        for declaration in parts[:-1]:
            start = offset + len(declaration) - len(declaration.lstrip())
            where = f"{source}:{text.count(chr(10), 0, start) + 1}"
            offset += len(declaration) + 1
            pair = re.fullmatch(r"\s*([a-z][a-z-]*)\s*:\s*(.*?)\s*", declaration, re.DOTALL)
            if not pair:
                raise ThemeError(f"{where}: malformed declaration {declaration!r}")
            css_key, value = pair.groups()
            key = css_key.replace("-", "_")
            if key not in _TOKENS:
                raise ThemeError(f"{where}: {css_key}: unknown token")
            if key in tokens:
                raise ThemeError(f"{where}: {css_key}: duplicate declaration")
            if key in ("radius", "opacity"):
                if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
                    raise ThemeError(f"{where}: {css_key}={value!r}: expected unitless decimal")
                value = float(value)
            elif key == "gradient":
                if value == "none":
                    value = None
                else:
                    match = re.fullmatch(r"linear-gradient\(\s*(#[0-9a-fA-F]{6})\s*,\s*(#[0-9a-fA-F]{6})\s*\)", value)
                    if not match:
                        raise ThemeError(f"{where}: gradient={value!r}: expected none or linear-gradient(#RRGGBB, #RRGGBB)")
                    value = match.groups()
            tokens.update(_validate({key: value}, where))
        if parts[-1].strip():
            line = text.count("\n", 0, offset) + 1
            raise ThemeError(f"{source}:{line}: {parts[-1].strip()!r}: final declaration requires a semicolon")
        return cls(str(source), **tokens)


LIGHT = Theme("Light", background="#f1f4f9", foreground="#23324d", panel="#f1f4f9",
              accent="#365a94", accent_text="#ffffff", radius=10, opacity=1, gradient=None)
DARK = Theme("Dark", background="#131a2a", foreground="#e5eafa", panel="#202c42",
             accent="#819bff", accent_text="#131a2a", radius=10, opacity=1, gradient=None)


def _choice(theme):
    if isinstance(theme, Theme):
        return theme
    if isinstance(theme, str) and theme in ("light", "dark", "system"):
        return theme
    raise ThemeError("App theme: expected Theme or 'light', 'dark', 'system'")


def _resolve(theme, scheme=None):
    if theme == "system":
        if scheme not in ("light", "dark"):
            raise ThemeError("System theme: Qt color scheme is Unknown; choose Light/Dark explicitly")
        theme = scheme
    if isinstance(theme, str):
        theme = {"light": LIGHT, "dark": DARK}[theme]
    return LIGHT.tokens | theme.tokens
