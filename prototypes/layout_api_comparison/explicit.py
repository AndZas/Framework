"""Experimental explicit tree: the author supplies the root Column."""
from api import Column, Row, Window, run
from content import Screen


def build():
    screen = Screen()
    body = Column(
        screen.heading,
        screen.explanation,
        Row(screen.save_button, screen.reset_button),
        screen.long_label,
        screen.add_button,
        screen.status,
    )
    window = Window("Layout API comparison", body)
    screen.target = body  # Runtime insertion: body.add(button).
    return window, screen


if __name__ == "__main__":
    window, _ = build()
    raise SystemExit(run(window))
