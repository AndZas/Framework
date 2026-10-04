"""Experimental, immutable animation descriptions; Qt Quick owns playback."""
from dataclasses import dataclass
import math
import weakref

from .theme import _validate, ThemeError


class AnimationError(ValueError):
    """Invalid descriptor, unsupported target, or unavailable presentation."""


_EASINGS = {"linear", "in_quad", "out_quad", "in_out_quad"}
_PROPERTIES = {"opacity", "scale", "radius", "background", "foreground",
               "panel", "accent", "accent_text"}
_SUPPORTED = {
    "Window": {"opacity", "background"},
    "Label": {"opacity", "scale", "radius", "foreground", "panel"},
    "Button": {"opacity", "scale", "radius", "accent", "accent_text"},
}


@dataclass(frozen=True, init=False)
class Keyframe:
    """Values at an integer millisecond timestamp; easing applies on arrival."""
    time: int
    easing: str
    _values: tuple

    def __init__(self, time, *, easing="linear", **values):
        if type(time) is not int or not 0 <= time <= 2_147_483_647:
            raise AnimationError("keyframe time: expected integer milliseconds in 0..2147483647")
        if not isinstance(easing, str) or easing not in _EASINGS:
            raise AnimationError("easing: expected linear, in_quad, out_quad or in_out_quad")
        if not values:
            raise AnimationError("keyframe must specify at least one property")
        result = {}
        for key, value in values.items():
            if key not in _PROPERTIES:
                raise AnimationError(f"keyframe {time}: unsupported property {key!r}")
            if key == "scale":
                try:
                    valid = type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 2
                except OverflowError:
                    valid = False
                if not valid:
                    raise AnimationError(f"keyframe {time}: scale: expected finite number in 0..2")
                result[key] = float(value)
            else:
                try:
                    result.update(_validate({key: value}, f"keyframe {time}"))
                except ThemeError as exc:
                    raise AnimationError(str(exc)) from exc
        object.__setattr__(self, "time", time)
        object.__setattr__(self, "easing", easing)
        object.__setattr__(self, "_values", tuple(sorted(result.items())))

    @property
    def values(self):
        return dict(self._values)


@dataclass(frozen=True, init=False)
class Timeline:
    """Two or more strictly increasing keyframes; properties have independent tracks."""
    keyframes: tuple

    def __init__(self, *keyframes):
        if len(keyframes) < 2 or any(type(frame) is not Keyframe for frame in keyframes):
            raise AnimationError("Timeline requires at least two Keyframe objects")
        if any(a.time >= b.time for a, b in zip(keyframes, keyframes[1:])):
            raise AnimationError("keyframe times must be strictly increasing (no duplicates)")
        object.__setattr__(self, "keyframes", tuple(keyframes))

    @property
    def duration(self):
        return self.keyframes[-1].time

    def _plan(self, kind, appearance):
        names = set().union(*(frame.values for frame in self.keyframes))
        unsupported = names - _SUPPORTED[kind]
        if unsupported:
            raise AnimationError(f"{kind} animation: unsupported properties: {', '.join(sorted(unsupported))}")
        tracks = []
        for name in sorted(names):
            points = [(frame.time, frame.values[name], frame.easing)
                      for frame in self.keyframes if name in frame.values]
            if points[0][0] != 0:
                points.insert(0, (0, 1.0 if name == "scale" else appearance[name], "linear"))
            segments = [dict(duration=b[0]-a[0], start=a[1], end=b[1], easing=b[2])
                        for a, b in zip(points, points[1:])]
            tracks.append(dict(name=name, color=name not in {"opacity", "scale", "radius"},
                               initial=points[0][1], segments=segments,
                               hold=self.duration-points[-1][0]))
        return dict(duration=self.duration, tracks=tracks)


class Playback:
    """A run's state and controls. No Qt objects or per-frame Python callbacks."""
    def __init__(self, target, timeline):
        self._target = weakref.ref(target)
        self._timeline = timeline
        self._state = "pending"

    @property
    def state(self):
        return self._state

    @property
    def running(self):
        return self.state == "running"

    def stop(self):
        target = self._target()
        if target is not None and target._runtime is not None:
            target._runtime.stop_animation(self)

    def restart(self):
        """Return a new Playback of the same description, with a fresh base snapshot."""
        target = self._target()
        if target is None:
            raise AnimationError("animation target no longer exists")
        return target.play(self._timeline)
