"""Focused checks use real QProcess children and the repository environment."""
from pathlib import Path
import subprocess
import sys
import time

import pytest
from PySide6.QtCore import QProcess, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from tools.api_playground.editor import EditorController
from tools.api_playground.runner import ChildRunner


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    return app


def wait_until(predicate, timeout=8000):
    deadline = time.monotonic() + timeout / 1000
    while not predicate() and time.monotonic() < deadline:
        QTest.qWait(10)
    assert predicate(), "Timed out waiting for asynchronous child state"


@pytest.fixture
def runner(qt_app):
    child = ChildRunner(stop_timeout_ms=120)
    yield child
    child.shutdown()
    wait_until(lambda: not child.active)
    child.deleteLater()
    qt_app.processEvents()


def write_source(tmp_path, text, name="app.py"):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_real_launch_arguments_cwd_and_utf8_output(runner, tmp_path):
    folder = tmp_path / "source folder with spaces"
    source = write_source(folder,
        "from pathlib import Path\nimport sys\n"
        "print(Path('relative.txt').read_text(encoding='utf-8'))\n"
        "print(sys.executable)\nprint('ошибка', file=sys.stderr)\n",
        "пример с пробелами.py")
    (folder / "relative.txt").write_text("данные — UTF-8", encoding="utf-8")
    output = []
    runner.output.connect(output.append)
    runner.run(source)
    assert runner.process.program() == sys.executable
    assert runner.process.arguments() == ["-u", str(source.resolve())]
    assert Path(runner.process.workingDirectory()) == folder.resolve()
    wait_until(lambda: not runner.active)
    assert runner.status == "Exited (code 0)"
    text = "".join(output)
    assert "данные — UTF-8" in text and "ошибка" in text
    assert sys.executable in text


def test_nonzero_and_start_error_keep_runner_reusable(runner, tmp_path):
    output = []
    runner.output.connect(output.append)
    source = write_source(tmp_path, "raise ValueError('intentional Python error')\n")
    runner.run(source)
    wait_until(lambda: not runner.active)
    assert runner.status == "Exited (code 1)"
    assert "ValueError: intentional Python error" in "".join(output)
    runner._executable = str(tmp_path / "missing interpreter.exe")
    runner.run(source)
    wait_until(lambda: not runner.active)
    assert runner.status == "Failed to start"
    assert "Process error:" in "".join(output)
    runner._executable = sys.executable
    source.write_text("print('recovered')\n", encoding="utf-8")
    runner.run(source)
    wait_until(lambda: not runner.active)
    assert runner.status == "Exited (code 0)"
    assert "recovered" in "".join(output)


def test_rerun_waits_for_exit_and_only_launches_latest(runner, tmp_path):
    output, started, finished = [], [], []
    runner.output.connect(output.append)
    runner.process.started.connect(lambda: started.append(runner.process.processId()))
    runner.process.finished.connect(lambda *_: finished.append(True))
    first = write_source(tmp_path, "import time\nprint('first-ready')\ntime.sleep(30)\n", "first.py")
    second = write_source(tmp_path, "print('obsolete-buffer')\n", "second.py")
    latest = write_source(tmp_path, "print('latest-buffer')\n", "latest.py")
    runner.run(first)
    wait_until(lambda: "first-ready" in "".join(output))
    runner.run(second)
    runner.run(latest)
    assert len(started) == 1
    wait_until(lambda: "latest-buffer" in "".join(output) and not runner.active)
    assert len(started) == 2 and len(finished) == 2
    assert started[0] != started[1]
    assert "obsolete-buffer" not in "".join(output)


def test_stop_fallback_does_not_block_and_cancels_rerun(runner, tmp_path):
    output, pulses = [], []
    runner.output.connect(output.append)
    source = write_source(tmp_path,
        "import signal, time\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "print('stuck-ready')\nwhile True: time.sleep(1)\n")
    runner.run(source)
    wait_until(lambda: "stuck-ready" in "".join(output))
    runner.run(write_source(tmp_path, "print('must-not-run')\n", "cancelled.py"))
    start = time.monotonic()
    runner.stop()
    assert time.monotonic() - start < .1
    timer = QTimer()
    timer.setInterval(10)
    timer.timeout.connect(lambda: pulses.append(True))
    timer.start()
    wait_until(lambda: not runner.active)
    timer.stop()
    assert pulses, "The event loop must continue during termination"
    assert runner.status.startswith("Stopped")
    assert "Child did not stop in time; killing it." in "".join(output)
    assert "must-not-run" not in "".join(output)


def test_shutdown_during_startup_cannot_launch_pending(runner, tmp_path):
    idle = []
    runner.idle.connect(lambda: idle.append(True))
    source = write_source(tmp_path, "import time\ntime.sleep(30)\n")
    runner.run(source)
    runner.run(source)
    runner.shutdown()
    wait_until(lambda: not runner.active and bool(idle))
    assert runner.process.state() == QProcess.ProcessState.NotRunning
    runner.run(source)
    assert not runner.active


def test_run_saves_current_buffer_and_save_failure_never_launches(qt_app, tmp_path, monkeypatch):
    editor = EditorController(tmp_path)
    editor.source = "print('точный текущий текст')\n"
    editor.run()
    assert editor.path == tmp_path / ".playground" / "scratch.py"
    assert editor.path.read_bytes() == editor.source.encode("utf-8")
    wait_until(lambda: not editor.runner.active)
    assert "точный текущий текст" in editor.output
    editor.path = tmp_path  # A directory cannot be saved as Python source.
    monkeypatch.setattr(QMessageBox, "warning", lambda *_: None)
    editor.source = "print('must not launch')\n"
    editor.run()
    assert not editor.runner.active and "Save failed:" in editor.output
    assert editor.dirty


def test_open_utf8_bom_and_failed_open_preserve_buffer(qt_app, tmp_path, monkeypatch):
    editor = EditorController(tmp_path)
    path = tmp_path / "текст с пробелами.py"
    text = "print('Привет 🌍')\n"
    path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    assert editor.open_file(path)
    assert editor.source == text and not editor.dirty
    editor.source += "# changed\n"
    saved = tmp_path / "saved.py"
    assert editor.save_to(saved)
    assert saved.read_bytes() == editor.source.encode("utf-8")
    bad = tmp_path / "bad.py"
    bad.write_bytes(b"\xff")
    monkeypatch.setattr(QMessageBox, "warning", lambda *_: None)
    assert not editor.open_file(bad)
    assert editor.path == saved and editor.source == text + "# changed\n"


def test_existing_scratch_and_close_cancellation(qt_app, tmp_path, monkeypatch):
    editor = EditorController(tmp_path)
    editor.scratch.parent.mkdir()
    editor.scratch.write_text("# previous experiment\n", encoding="utf-8")
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Cancel)
    editor.run()
    assert not editor.runner.active
    assert editor.scratch.read_text(encoding="utf-8") == "# previous experiment\n"
    editor.source += "# unsaved edit\n"
    editor.requestClose()
    assert not editor.canClose
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Discard)
    editor.requestClose()
    assert editor.canClose


def test_visible_editor_acceptance_flow(tmp_path):
    probe = Path(__file__).with_name("playground_probe.py")
    result = subprocess.run([sys.executable, str(probe), str(tmp_path)],
                            capture_output=True, text=True, encoding="utf-8", timeout=45)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "results.json").exists()
