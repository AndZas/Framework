"""A short preview of the intended Python authoring experience (provisional API)."""

from showcase_api import App, Button, Pulse, Star, Theme, Window


def main() -> int:
    app = App(theme=Theme(accent="#6c5ce7", star="#ffcc66"))
    window = app.add(Window("Qt Quick showcase · Python preview"))

    def greet() -> None:
        print("Hello from a Python callback")

    window.add(
        Button("hello", "Say hello", on_click=greet, animation=Pulse()),
        Button("orange", "Independent orange button", on_click=lambda: print("Orange!"), fill="#ed8757"),
        Star("star", on_click=lambda: print("Star activated")),
    )
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
