"""Visible Windows flow with synthetic Qt input; no physical-input claim."""
from pathlib import Path
import json
import os
import platform
import sys
import tempfile
import time
from unittest.mock import patch

import shiboken6

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QCoreApplication, QObject, QPoint, QPointF, QTimer, Qt
from PySide6.QtGui import QInputMethodEvent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

from tools.api_playground.__main__ import create_editor
from tools.api_playground.editor import STARTER


def wait_until(predicate, timeout=8000):
    deadline = time.monotonic() + timeout / 1000
    while not predicate() and time.monotonic() < deadline:
        QTest.qWait(20)
    assert predicate(), "Timed out waiting for visible Playground flow"


def process_exists(pid):
    # Read-only Windows check of the real interpreter (venv redirector PID differs).
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    try:
        code = wintypes.DWORD()
        assert kernel.GetExitCodeProcess(handle, ctypes.byref(code))
        return code.value == 259  # STILL_ACTIVE
    finally:
        kernel.CloseHandle(handle)


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    workspace = tempfile.TemporaryDirectory(prefix="playground source folder with spaces ")
    folder = Path(workspace.name)
    path = folder / "пример с пробелами.py"
    (folder / "relative.txt").write_text("относительный файл", encoding="utf-8")
    QQuickStyle.setStyle("Basic")
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    editor, engine, window = create_editor(app, repository=output)
    wait_until(lambda: window.isExposed())
    results = {
        "platform": platform.platform(), "python": sys.version,
        "executable": sys.executable, "pyside": pyside_version,
        "input": "synthetic QtTest mouse/key and QInputMethodEvent; file dialogs stubbed",
        "editor_pid": os.getpid(), "checks": [],
    }

    def click(name):
        item = window.findChild(QObject, name)
        assert item is not None, name
        point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
        QTest.mouseClick(window, Qt.MouseButton.LeftButton,
                         pos=QPoint(round(point.x()), round(point.y())))
        QTest.qWait(30)

    def edit(text):
        source = window.findChild(QObject, "sourceEditor")
        source.forceActiveFocus()
        QTest.keyClick(window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        event = QInputMethodEvent()
        event.setCommitString(text)
        QCoreApplication.sendEvent(window, event)
        QTest.qWait(30)
        assert source.property("text") == text
        assert editor.source == text

    pulses = []
    timer = QTimer()
    timer.setInterval(20)
    timer.timeout.connect(lambda: pulses.append(True))
    timer.start()

    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
        try:
            assert editor.source == STARTER and editor.path is None
            results["checks"].append("starter uses only public framework imports")
            window.grabWindow().save(str(output / "editor-starter.png"))

            # Child-only instrumentation proves its window and saves its own capture.
            instrumentation = '''
import json, os
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
qt_app = QGuiApplication([])
def report_window():
    top = next(w for w in qt_app.topLevelWindows() if w.isVisible())
    top.grabWindow().save(CHILD_CAPTURE)
    print('CHILD_WINDOW ' + json.dumps(dict(pid=os.getpid(), title=top.title(),
          parent_none=top.parent() is None, visible=top.isVisible())))
QTimer.singleShot(400, report_window)
'''.replace("CHILD_CAPTURE", repr(str(output / "child-window.png")))
            text = "print('старт — UTF-8')\n" + STARTER.replace(
                "raise SystemExit(App(window).run())", instrumentation + "\nraise SystemExit(App(window).run())")
            edit(text)
            with patch.object(QFileDialog, "getSaveFileName", return_value=(str(path), "")):
                click("saveAsButton")
            assert path.read_bytes() == text.encode("utf-8")
            click("runButton")
            wait_until(lambda: "CHILD_WINDOW " in editor.output)
            child = json.loads(next(line.split("CHILD_WINDOW ", 1)[1]
                                    for line in editor.output.splitlines() if line.startswith("CHILD_WINDOW ")))
            assert child["pid"] != os.getpid() and child["parent_none"] and child["visible"]
            assert window.isVisible() and window.isExposed() and editor.runner.active
            assert "старт — UTF-8" in editor.output
            window.grabWindow().save(str(output / "editor-running.png"))
            results["child_window"] = child
            results["checks"].append("edit, UTF-8 Save As, Run, separate visible top-level child, editor usable")

            # Run must save the changed buffer, terminate the old app, then run it.
            text = "import os, time\nprint('latest-buffer', os.getpid())\ntime.sleep(30)\n"
            edit(text)
            before = len(pulses)
            click("runButton")
            wait_until(lambda: "latest-buffer" in editor.output)
            if sys.platform == "win32":
                wait_until(lambda: not process_exists(child["pid"]))
            latest_pid = int(next(line.split()[1] for line in editor.output.splitlines()
                                 if line.startswith("latest-buffer ")))
            assert path.read_bytes() == text.encode("utf-8")
            assert editor.runner.process.processId() != child["pid"]
            assert len(pulses) > before
            results["checks"].append("rerun replaces child with exact latest buffer; event loop stays responsive")
            click("stopButton")
            wait_until(lambda: not editor.runner.active)
            if sys.platform == "win32":
                wait_until(lambda: not process_exists(latest_pid))
            assert editor.runner.status.startswith("Stopped")
            results["checks"].append("Stop ends sleeping child through bounded fallback")

            text = "from pathlib import Path\nimport sys\nprint(Path('relative.txt').read_text(encoding='utf-8'))\nprint('stderr marker', file=sys.stderr)\n"
            edit(text)
            click("saveButton")
            assert path.read_bytes() == text.encode("utf-8")
            click("runButton")
            wait_until(lambda: not editor.runner.active)
            assert editor.runner.status == "Exited (code 0)"
            assert "относительный файл" in editor.output and "stderr marker" in editor.output
            results["checks"].append("Save, relative file from spaced source folder, stdout/stderr, normal exit")

            edit("raise RuntimeError('probe Python error')\n")
            click("runButton")
            wait_until(lambda: not editor.runner.active)
            assert "RuntimeError: probe Python error" in editor.output
            assert editor.runner.status == "Exited (code 1)" and window.isVisible()
            window.grabWindow().save(str(output / "editor-python-error.png"))
            results["checks"].append("Python error and nonzero exit preserve editor")

            editor.runner._executable = str(folder / "missing interpreter.exe")
            click("runButton")
            wait_until(lambda: not editor.runner.active)
            assert editor.runner.status == "Failed to start" and window.isVisible()
            editor.runner._executable = sys.executable
            results["checks"].append("failed process start reported without closing editor")

            opened = folder / "open UTF-8.py"
            opened.write_text("print('Открыто 🌍')\n", encoding="utf-8")
            with patch.object(QFileDialog, "getOpenFileName", return_value=(str(opened), "")):
                click("openButton")
            assert editor.source == opened.read_text(encoding="utf-8")
            results["checks"].append("Open loads UTF-8 source into visible editor")

            edit("import os, time\nprint('shutdown-ready', os.getpid())\ntime.sleep(30)\n")
            click("runButton")
            wait_until(lambda: "shutdown-ready" in editor.output)
            shutdown_pid = int(next(line.split()[1] for line in editor.output.splitlines()
                                   if line.startswith("shutdown-ready ")))
            before = len(pulses)
            window.close()
            wait_until(lambda: editor.canClose and not window.isVisible())
            assert not editor.runner.active and len(pulses) > before
            if sys.platform == "win32":
                wait_until(lambda: not process_exists(shutdown_pid))
            results["checks"].append("window close asynchronously stops child before editor disappears")
            results["event_loop_pulses"] = len(pulses)
            results["output"] = editor.output
            (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        finally:
            timer.stop()
            editor.runner.shutdown()
            wait_until(lambda: not editor.runner.active)
            window.close()
            QTest.qWait(50)
            shiboken6.delete(engine)
            workspace.cleanup()
    print(json.dumps({"checks": results["checks"], "output": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]).resolve()))
