"""Visible Windows editor/preview flow: synthetic Qt input, file dialogs stubbed."""
from pathlib import Path
import ctypes
from ctypes import wintypes
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

import shiboken6
from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QCoreApplication, QObject, QPoint, QPointF, QTimer, Qt, qVersion
from PySide6.QtGui import QInputMethodEvent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

from tools.api_playground.__main__ import create_editor
from playground_probe import process_exists


def wait_until(predicate, timeout=8000):
    deadline = time.monotonic() + timeout / 1000
    while not predicate() and time.monotonic() < deadline:
        QTest.qWait(20)
    assert predicate(), "Timed out waiting for theme acceptance flow"


def preview_windows(title):
    """Read-only enumeration of real native child windows, including interpreter PID."""
    user = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user.IsWindowVisible.argtypes = [wintypes.HWND]
    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user.GetParent.argtypes = [wintypes.HWND]
    user.GetParent.restype = wintypes.HWND
    found = []

    @callback_type
    def visit(handle, _):
        text = ctypes.create_unicode_buffer(2048)
        user.GetWindowTextW(handle, text, len(text))
        if user.IsWindowVisible(handle) and text.value == title:
            pid = wintypes.DWORD()
            user.GetWindowThreadProcessId(handle, ctypes.byref(pid))
            found.append(dict(pid=pid.value, title=text.value,
                              parent_none=user.GetParent(handle) is None))
        return True

    user.EnumWindows(visit, 0)
    return found


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    results = dict(platform=platform.platform(), python=sys.version, executable=sys.executable,
                   pyside=pyside_version, qt=qVersion(), editor_pid=os.getpid(),
                   input="synthetic QtTest/QInputMethodEvent; file dialogs and questions stubbed; native windows enumerated via Win32", checks=[])

    with tempfile.TemporaryDirectory(prefix="playground themes with spaces ") as temporary:
        folder = Path(temporary)
        (folder / "docs").mkdir()
        (folder / "docs" / "api.md").write_bytes((REPOSITORY / "docs" / "api.md").read_bytes())
        editor, engine, window = create_editor(app, repository=folder)
        pulses = []
        timer = QTimer()
        timer.setInterval(20)
        timer.timeout.connect(lambda: pulses.append(True))
        timer.start()

        def click(name):
            window.requestActivate()
            QTest.qWait(30)
            item = window.findChild(QObject, name)
            assert item is not None and item.isVisible(), name
            point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
            QTest.mouseClick(window, Qt.MouseButton.LeftButton,
                             pos=QPoint(round(point.x()), round(point.y())))
            QTest.qWait(50)

        def edit(name, text):
            window.requestActivate()
            QTest.qWait(30)
            item = window.findChild(QObject, name)
            item.forceActiveFocus()
            QTest.keyClick(window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
            event = QInputMethodEvent()
            event.setCommitString(text)
            QCoreApplication.sendEvent(window, event)
            QTest.qWait(50)
            assert item.property("text") == text

        def capture(name):
            QTest.qWait(100)
            assert window.grabWindow().save(str(output / name))

        try:
            wait_until(lambda: window.isExposed())
            python = "import os, time\nprint('authored-ready', os.getpid())\ntime.sleep(30)\n"
            edit("sourceEditor", python)
            authored = folder / "авторский код.py"
            with patch.object(QFileDialog, "getSaveFileName", return_value=(str(authored), "")):
                click("saveAsButton")
            click("runButton")
            wait_until(lambda: "authored-ready" in editor.output)
            authored_pid = int(next(line.split()[1] for line in editor.output.splitlines()
                                    if line.startswith("authored-ready ")))
            python += "# unsaved Python survives Theme operations\n"
            edit("sourceEditor", python)
            click("themeTab")
            click("validateThemeButton")
            assert editor.theme.valid and editor.dirty
            lagoon_text = (REPOSITORY / "examples" / "lagoon.theme").read_text(encoding="utf-8")
            opened = folder / "лагуна с пробелами.theme"
            opened.write_bytes(b"\xef\xbb\xbf" + lagoon_text.encode("utf-8"))
            with patch.object(QFileDialog, "getOpenFileName", return_value=(str(opened), "")):
                click("openButton")
            assert editor.theme.source == lagoon_text and not editor.theme.dirty
            click("validateThemeButton")
            assert editor.theme.valid
            capture("theme-valid.png")
            assert editor.source == python and editor.dirty and process_exists(authored_pid)
            results["checks"].append("Theme tab, BOM Open and Validate Lagoon preserve dirty Python and active authored child")

            malformed = ":theme {\n radius: 49;\n}\n"
            edit("themeSourceEditor", malformed)
            click("previewThemeButton")
            assert ":2: radius=49.0" in editor.theme.validation
            assert process_exists(authored_pid) and editor.runner.active
            assert opened.read_text(encoding="utf-8-sig") == lagoon_text
            capture("theme-invalid.png")
            results["checks"].append("invalid Preview leaves running authored process and saved theme untouched")

            # Save As uses a real QFileDialog object but chooses the path without user input.
            valid = lagoon_text.replace("panel: #eaf5f2", "panel: #d6ebe4")
            edit("themeSourceEditor", valid)
            saved = folder / "новая тема.theme"
            def choose(dialog):
                assert dialog.defaultSuffix() == "theme"
                dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
                dialog.selectFile(str(saved.with_suffix("")))
                return QFileDialog.DialogCode.Accepted
            with patch.object(QFileDialog, "exec", choose):
                click("saveAsButton")
            assert editor.theme.path == saved and saved.read_bytes() == valid.encode("utf-8")
            edit("themeSourceEditor", valid + "\n")
            with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
                click("previewThemeButton")
            assert editor.theme.dirty and process_exists(authored_pid)
            with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Save):
                before = len(pulses)
                click("previewThemeButton")
            title = f"Theme preview — {saved.name}"
            wait_until(lambda: bool(preview_windows(title)))
            preview = preview_windows(title)[0]
            assert preview["pid"] != os.getpid() and preview["parent_none"]
            wait_until(lambda: not process_exists(authored_pid))
            assert editor.source == python and editor.dirty and authored.read_text(encoding="utf-8") != python
            assert saved.read_bytes() == (valid + "\n").encode("utf-8")
            assert len(pulses) > before
            assert editor.runner.process.arguments() == ["-u", str(REPOSITORY / "tools" / "api_playground" / "theme_preview.py"), str(saved)]
            results["native_preview"] = preview
            results["checks"].append("Save As default extension, Preview Save/Cancel, native separate window, asynchronous authored-to-preview replacement")

            click("sourceTab")
            assert window.findChild(QObject, "sourceEditor").property("text") == python
            click("docsTab")
            assert editor.docs.markdown
            click("themeTab")
            assert window.findChild(QObject, "themeSourceEditor").property("text") == valid + "\n"
            window.findChild(QObject, "themeSourceEditor").setProperty("cursorPosition", 0)
            window.setWidth(560)
            window.setHeight(440)
            QTest.qWait(100)
            for name in ("validateThemeButton", "previewThemeButton", "themeSourceEditor", "themeDiagnostic"):
                item = window.findChild(QObject, name)
                point = item.mapToScene(QPointF(0, 0))
                assert item.height() > 20 and 0 <= point.y() < window.height(), name
                assert 0 <= point.x() and point.x() + item.width() <= window.width(), name
            capture("theme-narrow.png")
            window.setWidth(1000)
            window.setHeight(760)
            results["checks"].append("tab switching retains both buffers and docs; Theme controls fit 560x440")

            # Reopen/edit/save/preview while the first preview is running.
            with patch.object(QFileDialog, "getOpenFileName", return_value=(str(saved), "")):
                click("openButton")
            modified = valid.replace("#eaf5f2", "#171827").replace("#173b3a", "#eeedf8").replace(
                "#d6ebe4", "#303047").replace("#126e67", "#55377e").replace("#65b8a3", "#285b78").replace(
                "radius: 20", "radius: 6").replace("opacity: 1", "opacity: 0.8")
            edit("themeSourceEditor", modified)
            QTest.keyClick(window, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
            QTest.qWait(50)
            assert saved.read_bytes() == modified.encode("utf-8")
            click("previewThemeButton")
            wait_until(lambda: bool(preview_windows(title)) and preview_windows(title)[0]["pid"] != preview["pid"])
            newer = preview_windows(title)[0]
            wait_until(lambda: not process_exists(preview["pid"]))
            results["checks"].append("reopen, modified Ctrl+S and Preview restart from the selected theme path")

            # Verify the exact sample's rendering and real control activation for both files.
            probe = Path(__file__).with_name("playground_theme_sample_probe.py")
            for name, text in (("lagoon", valid), ("modified", modified)):
                theme = folder / f"{name}.theme"
                theme.write_text(text, encoding="utf-8")
                result = subprocess.run([sys.executable, str(probe), str(theme), str(output / f"preview-{name}.png")],
                                        capture_output=True, text=True, encoding="utf-8", timeout=15)
                assert result.returncode == 0, result.stdout + result.stderr
                results[f"sample_{name}"] = json.loads(next(line[7:] for line in result.stdout.splitlines() if line.startswith("SAMPLE ")))
            assert (output / "preview-lagoon.png").read_bytes() != (output / "preview-modified.png").read_bytes()
            results["checks"].append("real sample captures reflect changed tokens and native opacity; synthetic clicks activate both gradient/solid buttons")

            click("runButton")  # F5/Run always targets authored Python, even from Theme.
            wait_until(lambda: editor.output.count("authored-ready") >= 2)
            final_authored_pid = int([line.split()[1] for line in editor.output.splitlines()
                                      if line.startswith("authored-ready ")][-1])
            wait_until(lambda: not process_exists(newer["pid"]))
            assert authored.read_bytes() == python.encode("utf-8")
            assert editor.runner.process.arguments() == ["-u", str(authored)]
            results["checks"].append("Run from Theme replaces preview and saves/relaunches authored source")

            editor.source += "# closing Python edit\n"
            editor.theme.source += "\n"
            preserved = editor.source, editor.theme.source
            for choices in ([QMessageBox.StandardButton.Cancel],
                            [QMessageBox.StandardButton.Discard, QMessageBox.StandardButton.Cancel]):
                with patch.object(QMessageBox, "question", side_effect=choices):
                    window.close()
                    QTest.qWait(50)
                assert window.isVisible() and not editor.closing and editor.runner.active
                assert (editor.source, editor.theme.source) == preserved
            before = len(pulses)
            with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Save):
                window.close()
                wait_until(lambda: editor.canClose and not window.isVisible())
            assert not editor.runner.active and len(pulses) > before
            wait_until(lambda: not process_exists(final_authored_pid))
            assert authored.read_bytes() == preserved[0].encode("utf-8")
            assert saved.read_bytes() == preserved[1].encode("utf-8")
            results["checks"].append("close Cancel at either dirty buffer retains both and child; Save both then responsive shutdown")
            results["event_loop_pulses"] = len(pulses)
        finally:
            timer.stop()
            editor.source = editor._saved_source
            editor.theme.source = editor.theme._saved_source
            editor.runner.shutdown()
            wait_until(lambda: not editor.runner.active)
            window.close()
            QTest.qWait(50)
            shiboken6.delete(engine)

    (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
