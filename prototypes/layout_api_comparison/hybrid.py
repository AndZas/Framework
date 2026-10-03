"""Experimental hybrid: window children flow vertically in insertion order."""
from api import Row, Window, run
from content import Screen


def build():
    screen = Screen()
    window = Window("Layout API comparison")
    window.add(screen.heading)
    window.add(screen.explanation)
    window.add(Row(screen.save_button, screen.reset_button))
    window.add(screen.long_label)
    window.add(screen.add_button)
    window.add(screen.status)
    screen.target = window  # Runtime insertion: window.add(button).
    return window, screen


if __name__ == "__main__":
    window, _ = build()
    raise SystemExit(run(window))
