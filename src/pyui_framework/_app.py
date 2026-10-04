"""Public lifecycle; the Qt adapter stays private."""
from ._model import Window
from .theme import _choice, _resolve


class App:
    def __init__(self, window, *, theme="light"):
        if type(window) is not Window:
            raise TypeError("App requires one Window")
        if window._app is not None:
            raise ValueError("Window already belongs to an App")
        self._theme = _choice(theme)
        self._resolved = None if theme == "system" else _resolve(self._theme)
        self._window = window
        self._runtime = None
        self._started = False
        window._app = self

    @property
    def theme(self):
        return self._theme

    @property
    def resolved_theme(self):
        """Canonical values; System is unavailable until the runtime starts."""
        if self._resolved is None:
            raise RuntimeError("System theme resolves when App.run() starts")
        return self._resolved.copy()

    def set_theme(self, theme):
        """Validate and replace appearance, preserving every widget's local style."""
        choice = _choice(theme)
        if self._runtime:
            self._runtime.set_theme(choice)
        else:
            values = None if choice == "system" else _resolve(choice)
            self._theme, self._resolved = choice, values

    def run(self):
        """Show the window and block until closed; return nonzero on UI errors."""
        if self._started:
            raise RuntimeError("App.run() may only be called once")
        self._started = True
        from ._runtime import Runtime
        self._runtime = Runtime(self._window, self)
        try:
            return self._runtime.run()
        finally:
            self._runtime.close()
            self._runtime = None
