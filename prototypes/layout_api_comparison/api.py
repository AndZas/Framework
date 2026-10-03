"""Experimental authoring surface; deliberately bounded to this comparison."""


class Container:
    def __init__(self, *children):
        self.children = list(children)
        self._append = None

    def add(self, child):
        if self._append:
            self._append(child)
        self.children.append(child)
        return child


class Column(Container):
    pass


class Row(Container):
    pass


class Window(Container):
    def __init__(self, title, *children, width=640, height=520):
        super().__init__(*children)
        self.title, self.width, self.height = title, width, height


class Label:
    def __init__(self, text, *, heading=False):
        self.text, self.heading = text, heading
        self._update = None

    def set_text(self, text):
        self.text = text
        if self._update:
            self._update()


class Button:
    def __init__(self, text, *, on_click):
        self.text, self.on_click = text, on_click


def run(window):
    from runtime import App
    return App(window).run()
