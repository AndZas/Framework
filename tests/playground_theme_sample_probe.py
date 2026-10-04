"""Instrument the real preview sample with synthetic Qt input in its own process."""
from pathlib import Path
import json
import os
import sys

from PySide6.QtCore import QPoint, QPointF, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

from pyui_framework import Button, Label, Theme
from tools.api_playground.theme_preview import build


def main(path, output):
    qt_app = QGuiApplication([])
    sample = build(path)
    failure = []

    def verify():
        try:
            # Private Qt objects are inspected only by this test probe.
            runtime = sample._runtime
            assert runtime.window.isVisible() and runtime.window.parent() is None
            expected = Theme.load(path).tokens
            assert sample.resolved_theme.items() >= expected.items()
            assert runtime.window.opacity() == expected.get("opacity", 1)

            def visual(root, name):
                if root.objectName() == name:
                    return root
                for child in root.childItems():
                    match = visual(child, name)
                    if match is not None:
                        return match

            buttons = [n for n in runtime.nodes if isinstance(n.value, Button)]
            assert len(buttons) == 2
            assert buttons[0].appearance["hasGradient"] == (expected.get("gradient") is not None)
            assert not buttons[1].appearance["hasGradient"]
            assert buttons[1].appearance["accent"] == sample.resolved_theme["accent"]
            for count, node in enumerate(buttons, start=1):
                item = visual(runtime.quick.contentItem(), node.nodeId)
                point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
                QTest.mouseClick(runtime.window, Qt.MouseButton.LeftButton,
                                 pos=QPoint(round(point.x()), round(point.y())))
                QTest.qWait(50)
                assert any(isinstance(n.value, Label) and f"Sample clicked {count} time(s)" in n.value.text
                           for n in runtime.nodes)
            assert runtime.window.grabWindow().save(str(output))
            print("SAMPLE " + json.dumps(dict(pid=os.getpid(), title=runtime.window.title(),
                  visible=runtime.window.isVisible(), parent_none=runtime.window.parent() is None,
                  tokens=sample.resolved_theme, clicks=2), ensure_ascii=False), flush=True)
        except Exception as error:
            failure.append(str(error))
            import traceback
            traceback.print_exc()
        finally:
            qt_app.quit()

    QTimer.singleShot(500, verify)
    result = sample.run()
    return 1 if failure else result


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
