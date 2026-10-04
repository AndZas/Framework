from dataclasses import FrozenInstanceError
from pathlib import Path
import subprocess
import sys

import pytest
from pyui_framework import AnimationError, Button, Keyframe, Label, Timeline, Window


@pytest.mark.parametrize("time", [-1, 1.5, True, "10", 2_147_483_648])
def test_time_validation(time):
    with pytest.raises(AnimationError, match="integer milliseconds"):
        Keyframe(time, opacity=1)


@pytest.mark.parametrize("values", [dict(x=1), dict(gradient=None), dict(opacity=True),
    dict(opacity=1.01), dict(opacity=-.1), dict(opacity="1"), dict(radius=49),
    dict(radius=-1), dict(scale=2.01), dict(scale=-1), dict(scale=True),
    dict(scale=10**1000), dict(scale=float("inf")), dict(scale=float("nan")),
    dict(accent="#abc"), dict(accent="red"), dict(foreground=23), {}])
def test_value_validation(values):
    with pytest.raises(AnimationError):
        Keyframe(0, **values)


@pytest.mark.parametrize("easing", [None, [], 1, "Linear", "bounce"])
def test_easing_validation(easing):
    with pytest.raises(AnimationError, match="easing"):
        Keyframe(0, easing=easing, opacity=1)


@pytest.mark.parametrize("frames", [(), (Keyframe(0, opacity=1),),
    (Keyframe(0, opacity=1), "bad"),
    (Keyframe(2, opacity=1), Keyframe(2, opacity=0)),
    (Keyframe(2, opacity=1), Keyframe(1, opacity=0))])
def test_timeline_validation(frames):
    with pytest.raises(AnimationError):
        Timeline(*frames)


def test_immutable_and_sparse_plan():
    a = Keyframe(100, opacity=.2, accent="#ABCDEF")
    a.values["opacity"] = .9
    assert a.values == dict(opacity=.2, accent="#abcdef")
    with pytest.raises(FrozenInstanceError):
        a.time = 1
    timeline = Timeline(a, Keyframe(300, opacity=.8, easing="out_quad"), Keyframe(500, radius=20))
    with pytest.raises(FrozenInstanceError):
        timeline.keyframes = ()
    assert timeline.duration == 500
    plan = timeline._plan("Button", dict(opacity=1, accent="#000000", radius=10))
    tracks = {t["name"]: t for t in plan["tracks"]}
    assert tracks["opacity"]["segments"] == [
        dict(duration=100, start=1, end=.2, easing="linear"),
        dict(duration=200, start=.2, end=.8, easing="out_quad")]
    assert tracks["opacity"]["hold"] == 200
    assert tracks["accent"]["color"] and tracks["accent"]["hold"] == 400
    assert tracks["radius"]["segments"][0]["start"] == 10


@pytest.mark.parametrize("kind,allowed", [
    ("Window", {"opacity", "background"}),
    ("Label", {"opacity", "scale", "radius", "foreground", "panel"}),
    ("Button", {"opacity", "scale", "radius", "accent", "accent_text"})])
def test_property_restrictions(kind, allowed):
    values = dict(opacity=1, scale=1, radius=10, background="#000000",
                  foreground="#000000", panel="#000000", accent="#000000", accent_text="#000000")
    for name, value in values.items():
        timeline = Timeline(Keyframe(0, **{name: value}), Keyframe(10, **{name: value}))
        if name in allowed:
            assert timeline._plan(kind, values)["tracks"][0]["name"] == name
        else:
            with pytest.raises(AnimationError, match=kind + " animation"):
                timeline._plan(kind, values)


def test_prelaunch_rejection():
    timeline = Timeline(Keyframe(0, opacity=.2), Keyframe(10, opacity=1))
    for widget in (Window("test"), Label("test"), Button("test", on_click=lambda: None)):
        with pytest.raises(AnimationError, match="live target"):
            widget.play(timeline)
        with pytest.raises(AnimationError, match="Timeline"):
            widget.play(None)


def test_qt_playback_and_example(tmp_path):
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("animation_probe.py")), str(tmp_path)],
                            capture_output=True, text=True, timeout=75)
    assert result.returncode == 0, result.stdout + result.stderr
