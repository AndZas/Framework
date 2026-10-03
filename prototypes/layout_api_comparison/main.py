"""Select an example; optional bounded Windows synthetic verification."""
import argparse
import json
import platform
import sys
import traceback
from pathlib import Path

from PySide6 import __version__
from PySide6.QtCore import QObject, QPoint, QPointF, Qt, QTimer, qVersion
from PySide6.QtTest import QTest

from api import Button, Column, Label, Row
from runtime import App


def probe(app, screen, style):
    failures = []
    evidence = {"style": style, "environment": {
        "platform": platform.platform(), "python": sys.version.split()[0],
        "PySide6": __version__, "Qt": qVersion()}, "layouts": {}}
    output = Path(__file__).with_name("evidence")
    output.mkdir(exist_ok=True)

    def check(name, passed):
        print(f"CHECK {name} pass={passed}", flush=True)
        if not passed:
            failures.append(name)

    def item_for(value):
        node = next(node for node in app.nodes if node.value is value)

        def search(item):
            if item.objectName() == node.nodeId:
                return item
            for child in item.childItems():
                found = search(child)
                if found is not None:
                    return found
            return None

        item = search(app.quick.contentItem())
        if item is None:
            raise RuntimeError(f"Missing visual item {node.nodeId}")
        return item

    def click(value):
        item = item_for(value)
        viewport = app.window.findChild(QObject, "viewport")
        viewport.setProperty("contentY", 0)
        app.qt_app.processEvents()
        point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
        scroll = max(0, point.y() - app.window.height() + 70)
        maximum = max(0, viewport.property("contentHeight") - viewport.property("height"))
        viewport.setProperty("contentY", min(scroll, maximum))
        app.qt_app.processEvents()
        point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
        check("click-in-viewport", 20 <= point.y() <= app.window.height() - 20)
        QTest.mouseClick(app.window, Qt.MouseButton.LeftButton,
                         pos=QPoint(round(point.x()), round(point.y())))
        app.qt_app.processEvents()

    def layout(name, capture=True):
        leaves = [node.value for node in app.nodes if isinstance(node.value, (Label, Button))]
        bounds = []
        within_width, enough_height, no_overlap = True, True, True
        for value in leaves:
            item = item_for(value)
            p = item.mapToScene(QPointF(0, 0))
            rect = [round(p.x(), 2), round(p.y(), 2), round(item.width(), 2), round(item.height(), 2)]
            bounds.append({"text": value.text, "rect": rect})
            within_width &= rect[0] >= 19.9 and rect[0] + rect[2] <= app.window.width() - 19.9
            if isinstance(value, Label):
                enough_height &= item.height() + 0.1 >= item.implicitHeight()
            else:
                text = item.property("contentItem")
                enough_height &= item.height() + 0.1 >= text.implicitHeight() + 24
        # Overlap test includes the two horizontally grouped actions.
        for i, first in enumerate(bounds):
            x, y, w, h = first["rect"]
            for second in bounds[i + 1:]:
                a, b, c, d = second["rect"]
                no_overlap &= min(x+w, a+c) - max(x, a) <= 0.1 or min(y+h, b+d) - max(y, b) <= 0.1
        check(f"{name}-horizontal-bounds", within_width)
        check(f"{name}-text-height", enough_height)
        check(f"{name}-no-overlap", no_overlap)
        save, reset = bounds[2]["rect"], bounds[3]["rect"]
        check(f"{name}-grouped-row", save[1] == reset[1] and save[0] < reset[0] and save[2] == reset[2])
        check(f"{name}-vertical-order", all(bounds[i]["rect"][1] < bounds[j]["rect"][1]
                                               for i, j in ((0, 1), (1, 2), (3, 4), (4, 5), (5, 6))))
        evidence["layouts"][name] = bounds
        if capture:
            check(f"{name}-capture", app.quick.grabWindow().save(str(output / f"{style}-{name}.png")))

    def guarded(function):
        def call():
            try:
                function()
            except Exception:
                failures.append("probe-exception")
                traceback.print_exc()
                finish()
        return call

    def initial():
        check("visible", app.window.isVisible())
        check("initial-seven-leaves", sum(isinstance(node.value, (Label, Button)) for node in app.nodes) == 7)
        window = app.root_node.value
        if style == "hybrid":
            check("hybrid-direct-children", len(window.children) == 6 and isinstance(window.children[2], Row))
        else:
            check("explicit-root-and-row", len(window.children) == 1 and isinstance(window.children[0], Column)
                  and isinstance(window.children[0].children[2], Row))
        layout("initial", capture=False)
        click(screen.save_button)
        click(screen.reset_button)
        click(screen.add_button)
        QTimer.singleShot(250, guarded(dynamic))

    def dynamic():
        click(screen.dynamic)
        click(screen.save_button)
        existing = item_for(screen.save_button)
        click(screen.add_button)  # Repeated addition is deliberately idempotent.
        check("existing-instance-preserved", item_for(screen.save_button) is existing)
        check("independent-callbacks", screen.counts == {"save": 2, "reset": 1, "add": 2, "dynamic": 1})
        check("one-runtime-button", sum(node.value is screen.dynamic for node in app.nodes) == 1)
        QTimer.singleShot(250, guarded(normal))

    def normal():
        layout("normal")
        app.window.resize(300, 520)
        QTimer.singleShot(300, guarded(narrow))

    def narrow():
        layout("narrow")
        check("narrow-label-wrap", item_for(screen.long_label).height() > 50)
        click(screen.save_button)
        click(screen.reset_button)
        click(screen.dynamic)
        check("narrow-callbacks", screen.counts == {"save": 3, "reset": 2, "add": 2, "dynamic": 2})
        app.window.resize(280, 260)
        QTimer.singleShot(300, guarded(short))

    def short():
        click(screen.dynamic)
        check("short-scroll-runtime-callback", screen.counts["dynamic"] == 3)
        check("qml-and-callback-errors", not app.errors)
        finish()

    def finish():
        evidence.update(counts=screen.counts, errors=app.errors, failures=failures)
        (output / f"{style}-probe.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        print(f"RESULT failures={failures}", flush=True)
        app.close()
        app.qt_app.exit(1 if failures else 0)

    QTimer.singleShot(500, guarded(initial))
    QTimer.singleShot(20000, lambda: (failures.append("timeout"), finish()))
    return app.run()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=("hybrid", "explicit"), default="hybrid")
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    if args.style == "hybrid":
        from hybrid import build
    else:
        from explicit import build
    window, screen = build()
    app = App(window)
    return probe(app, screen, args.style) if args.probe else app.run()


if __name__ == "__main__":
    raise SystemExit(main())
