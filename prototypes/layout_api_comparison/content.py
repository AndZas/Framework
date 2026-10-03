"""Shared content and independent callbacks; no presentation internals."""
from api import Button, Label


class Screen:
    def __init__(self):
        self.counts = {key: 0 for key in ("save", "reset", "add", "dynamic")}
        self.status = Label("Ready. Each action has its own Python callback.")
        self.target = None
        self.dynamic = None
        self.heading = Label("Layout API comparison", heading=True)
        self.explanation = Label("The same screen, authored in two ways. Resize the window, use the grouped actions, then add a control.")
        self.save_button = Button("Save draft", on_click=self.save)
        self.reset_button = Button("Reset draft", on_click=self.reset)
        self.long_label = Label("A longer label stays readable as the window narrows: text wraps, the two grouped actions share the available width, and taller content can be scrolled vertically.")
        self.add_button = Button("Add runtime control", on_click=self.add)

    def record(self, key):
        self.counts[key] += 1
        self.status.set_text(" / ".join(f"{name}: {count}" for name, count in self.counts.items()))
        print(f"CALLBACK {key} count={self.counts[key]}", flush=True)

    def save(self):
        self.record("save")

    def reset(self):
        self.record("reset")

    def add(self):
        self.record("add")
        if self.dynamic is None:
            self.dynamic = Button("Runtime action", on_click=self.dynamic_action)
            self.target.add(self.dynamic)

    def dynamic_action(self):
        self.record("dynamic")
