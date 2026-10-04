"""Python declarations with single ownership and atomic validation."""
from .theme import _style
from .animation import Timeline, AnimationError


def _text(value):
    if not isinstance(value, str):
        raise TypeError("text must be a string")
    return value


class _Element:
    def __init__(self):
        self._owner = None
        self._runtime = None


class _Styled:
    def play(self, timeline):
        """Play a temporary appearance overlay on a live, presented widget."""
        if type(timeline) is not Timeline:
            raise AnimationError("play expects a Timeline")
        if self._runtime is None:
            raise AnimationError("play requires a live target inside App.run()")
        return self._runtime.play(timeline)

    def _init_style(self, style):
        self._style = _style(style, type(self).__name__)

    @property
    def style(self):
        return self._style.copy()

    def set_style(self, **tokens):
        """Replace local overrides atomically; an empty call restores inheritance."""
        values = _style(tokens, type(self).__name__)
        if self._runtime:
            self._runtime.check_thread()
        self._style = values
        if self._runtime:
            self._runtime.styleChanged.emit()


class _Container(_Element):
    def __init__(self, *children):
        super().__init__()
        self._children = []
        try:
            for child in children:
                self.add(child)
        except Exception:
            for child in self._children:
                child._owner = None
            self._children.clear()
            raise

    @property
    def children(self):
        return tuple(self._children)

    def add(self, child):
        if type(child) not in (Label, Button, Row, Column):
            raise TypeError("child must be Label, Button, Row or Column")
        ancestor = self
        while ancestor is not None:
            if ancestor is child:
                raise ValueError("a container cannot contain itself or an ancestor")
            ancestor = ancestor._owner
        if child._owner is not None:
            raise ValueError("child already belongs to a container")
        if self._runtime:
            self._runtime.check_thread()
        child._owner = self
        self._children.append(child)
        if self._runtime:
            self._runtime.append(child)
        return child


class Column(_Container):
    """Vertical insertion-order flow."""


class Row(_Container):
    """Horizontal group; children share the available width."""


class Window(_Styled, _Container):
    def __init__(self, title, *children, width=640, height=520, style=None):
        self._init_style(style)
        self.title = _text(title)
        for name, value, minimum in (("width", width, 280), ("height", height, 260)):
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} must be an integer >= {minimum}")
        self.width, self.height = width, height
        self._app = None
        super().__init__(*children)


class Label(_Styled, _Element):
    def __init__(self, text, *, heading=False, style=None):
        self._init_style(style)
        super().__init__()
        self._text = _text(text)
        if type(heading) is not bool:
            raise TypeError("heading must be bool")
        self.heading = heading

    @property
    def text(self):
        return self._text

    def set_text(self, text):
        text = _text(text)
        if self._runtime:
            self._runtime.check_thread()
        self._text = text
        if self._runtime:
            self._runtime.textChanged.emit()


class Button(_Styled, _Element):
    def __init__(self, text, *, on_click, style=None):
        self._init_style(style)
        super().__init__()
        self.text = _text(text)
        if not callable(on_click):
            raise TypeError("on_click must be callable")
        self.on_click = on_click
