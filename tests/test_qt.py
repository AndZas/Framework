import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.parametrize("shell", ["production", "theme"])
def test_scrollbar_edge_layout(shell, tmp_path):
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("scrollbar_edge_probe.py")),
                             "--app", shell, "--output", str(tmp_path / shell)],
                            capture_output=True, text=True, timeout=40)
    assert result.returncode == 0, result.stdout + result.stderr


def test_visible_interaction(tmp_path):
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("qt_probe.py")), str(tmp_path)],
                            capture_output=True, text=True, timeout=40)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("route", ["wheel", "scrollbar", "drag"])
def test_rapid_clicks_after_scroll(route, tmp_path):
    result = subprocess.run([sys.executable, str(Path(__file__).with_name("scroll_click_probe.py")),
                             "--route", route, "--output", str(tmp_path / (route + ".json"))],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


def test_callback_exception_is_reported():
    code = '''
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from pyui_framework import App, Button, Window
qt_app = QGuiApplication([])
def fail():
    raise ValueError("intentional callback failure")
app = App(Window("error test", Button("Fail", on_click=fail)))
def activate():
    app._runtime.bridge.activate("node-1")
    app._runtime.qt_app.quit()
QTimer.singleShot(200, activate)
raise SystemExit(app.run())
'''
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=20)
    assert result.returncode == 1
    assert "Callback node-1" in result.stderr
    assert "ValueError: intentional callback failure" in result.stderr


def test_qml_load_failure_is_reported():
    code = '''
from unittest.mock import patch
from pathlib import Path
from pyui_framework import App, Window
with patch("pyui_framework._runtime.Path", return_value=Path("missing-runtime.py")):
    App(Window("bad QML")).run()
'''
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=20)
    assert result.returncode != 0
    assert "RuntimeError: Internal QML load failed" in result.stderr
    assert "Main.qml" in result.stderr


def test_python_example_callbacks():
    example = Path(__file__).resolve().parents[1] / "examples" / "hello.py"
    code = '''
import runpy, sys
from PySide6.QtCore import QTimer, QPoint, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
from pyui_framework import App, Button, Label
qt_app = QGuiApplication([])
app = App(runpy.run_path(sys.argv[1])["build"]())
def verify():
    runtime = app._runtime
    def click(value):
        node = next(n for n in runtime.nodes if n.value is value)
        def find(root):
            if root.objectName() == node.nodeId:
                return root
            for child in root.childItems():
                match = find(child)
                if match is not None:
                    return match
        visual = find(runtime.quick.contentItem())
        p = visual.mapToScene(QPointF(visual.width()/2, visual.height()/2))
        QTest.mouseClick(runtime.window, Qt.MouseButton.LeftButton, pos=QPoint(round(p.x()), round(p.y())))
        QTest.qWait(50)
    try:
        for node in list(runtime.nodes):
            if isinstance(node.value, Button):
                click(node.value)
        dynamic = next(n.value for n in runtime.nodes if isinstance(n.value, Button) and n.value.text == "Added after startup")
        click(dynamic)
        status = next(n.value for n in runtime.nodes if isinstance(n.value, Label) and n.value.text.startswith("save:"))
        assert status.text == "save: 1 · reset: 1 · added: 1", status.text
        assert not runtime.errors
        qt_app.exit(0)
    except Exception:
        import traceback
        traceback.print_exc()
        qt_app.exit(1)
QTimer.singleShot(300, verify)
raise SystemExit(app.run())
'''
    result = subprocess.run([sys.executable, "-c", code, str(example)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
