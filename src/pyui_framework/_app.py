"""Public lifecycle; the Qt adapter stays private."""
from ._model import Window


class App:
    def __init__(self, window):
        if type(window) is not Window:
            raise TypeError("App requires one Window")
        if window._app is not None:
            raise ValueError("Window already belongs to an App")
        self._window = window
        self._runtime = None
        self._started = False
        window._app = self

    def run(self):
        """Show the window and block until closed; return nonzero on UI errors."""
        if self._started:
            raise RuntimeError("App.run() may only be called once")
        self._started = True
        from ._runtime import Runtime
        self._runtime = Runtime(self._window)
        try:
            return self._runtime.run()
        finally:
            self._runtime.close()
