import pytest
from pyui_framework import App, Button, Column, Label, Row, Window


def test_order_and_ownership():
    label = Label("first")
    row = Row(Button("action", on_click=lambda: None))
    window = Window("test", label, row)
    assert window.children == (label, row)
    with pytest.raises(ValueError, match="already belongs"):
        Column().add(label)
    with pytest.raises(TypeError, match="child"):
        window.add("invalid")
    assert window.children == (label, row)
    with pytest.raises(ValueError, match="ancestor"):
        row.add(row)
    outer, inner = Column(), Column()
    outer.add(inner)
    with pytest.raises(ValueError, match="ancestor"):
        inner.add(outer)
    orphan = Label("reusable after failed construction")
    with pytest.raises(TypeError):
        Column(orphan, "invalid")
    assert Column(orphan).children == (orphan,)


def test_validation_and_lifecycle():
    with pytest.raises(TypeError, match="callable"):
        Button("bad", on_click=None)
    with pytest.raises(TypeError, match="string"):
        Label(2)
    with pytest.raises(ValueError, match="width"):
        Window("small", width=100)
    label = Label("old")
    with pytest.raises(TypeError):
        label.set_text(None)
    assert label.text == "old"
    window = Window("owned")
    App(window)
    with pytest.raises(ValueError, match="already belongs"):
        App(window)
