"""Check that the installed package is importable."""

import importlib


def test_package_is_importable() -> None:
    package = importlib.import_module("framework")

    assert package.__name__ == "framework"
    assert package.__file__ is not None
