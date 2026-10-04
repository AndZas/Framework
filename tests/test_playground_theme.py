"""Theme buffer safety and validation against the existing public parser."""
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from tools.api_playground.editor import EditorController
from tools.api_playground.theme_editor import STARTER_THEME


@pytest.fixture
def editor(tmp_path):
    qt_app = QApplication.instance() or QApplication([])
    qt_app.setQuitOnLastWindowClosed(False)
    controller = EditorController(tmp_path)
    yield controller
    assert not controller.runner.active
    controller.deleteLater()
    qt_app.processEvents()


def test_theme_bom_and_plain_utf8_save_are_independent(editor, tmp_path):
    editor.source += "# unsaved Python\n"
    python = (editor.source, editor.path, editor.dirty)
    text = STARTER_THEME.replace("radius: 20", "radius: 12")
    opened = tmp_path / "тема с пробелами.theme"
    opened.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    assert editor.theme.open_file(opened)
    assert editor.theme.source == text and not editor.theme.dirty
    editor.theme.source += "\n"
    saved = tmp_path / "сохранено с пробелами.theme"
    assert editor.theme.save_to(saved)
    assert saved.read_bytes() == (text + "\n").encode("utf-8")
    assert not editor.theme.dirty and editor.theme.path == saved
    assert (editor.source, editor.path, editor.dirty) == python


@pytest.mark.parametrize("text, diagnostic", [
    (":theme {\n radius 2;\n}", ":2: malformed declaration"),
    (":theme {\n radius: 2;\n radius: 3;\n}", ":3: radius: duplicate"),
    (":theme {\n mystery: 3;\n}", ":2: mystery: unknown"),
    (":theme {\n radius: 49;\n}", ":2: radius=49.0: expected finite number in 0..48"),
    (":theme {\n opacity: 1.1;\n}", ":2: opacity=1.1: expected finite number in 0..1"),
    (":theme { radius: 2 }", "final declaration requires a semicolon"),
])
def test_invalid_preview_does_not_save_or_touch_child(editor, monkeypatch, text, diagnostic):
    editor.source += "# Python edits\n"
    editor.theme.source = text
    source = (editor.source, editor.path, editor.dirty)
    theme = (editor.theme.source, editor.theme.path, editor.theme.dirty)
    pending = editor.runner._pending
    status = editor.runner.status
    with patch.object(editor.runner, "run") as run, patch.object(editor.runner, "stop") as stop:
        monkeypatch.setattr(QMessageBox, "question", lambda *_: pytest.fail("Invalid preview must not ask to save"))
        assert not editor.theme.validate()
        assert diagnostic in editor.theme.validation
        editor.previewTheme()
        run.assert_not_called()
        stop.assert_not_called()
    assert (editor.source, editor.path, editor.dirty) == source
    assert (editor.theme.source, editor.theme.path, editor.theme.dirty) == theme
    assert editor.runner._pending == pending and editor.runner.status == status
    assert not editor.theme.scratch.exists()


def test_validate_lagoon_is_read_only(editor):
    lagoon = Path(__file__).resolve().parents[1] / "examples" / "lagoon.theme"
    assert editor.theme.open_file(lagoon)
    editor.source += "# independent edit\n"
    state = (editor.source, editor.path, editor.dirty,
             editor.theme.source, editor.theme.path, editor.theme.dirty,
             editor.runner.status, editor.runner._pending)
    assert editor.theme.validate()
    assert "Valid theme:" in editor.theme.validation and str(lagoon) in editor.theme.validation
    assert state == (editor.source, editor.path, editor.dirty,
                     editor.theme.source, editor.theme.path, editor.theme.dirty,
                     editor.runner.status, editor.runner._pending)


def test_existing_scratch_cancel_and_confirm(editor, monkeypatch):
    scratch = editor.theme.scratch
    scratch.parent.mkdir()
    scratch.write_text(":theme { radius: 1; }", encoding="utf-8")
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Cancel)
    assert not editor.theme.save()
    assert scratch.read_text(encoding="utf-8") == ":theme { radius: 1; }"
    assert editor.theme.path is None
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Yes)
    assert editor.theme.save()
    assert scratch.read_bytes() == STARTER_THEME.encode("utf-8")


def test_save_as_suffix_filter_and_cancel(editor, tmp_path, monkeypatch):
    def choose(dialog):
        assert dialog.defaultSuffix() == "theme"
        assert dialog.nameFilters() == ["Theme files (*.theme)"]
        assert dialog.acceptMode() == QFileDialog.AcceptMode.AcceptSave
        assert not dialog.testOption(QFileDialog.Option.DontConfirmOverwrite)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
        dialog.selectFile(str(tmp_path / "новая тема"))
        return QFileDialog.DialogCode.Accepted
    monkeypatch.setattr(QFileDialog, "exec", choose)
    assert editor.theme.saveAs()
    assert editor.theme.path == tmp_path / "новая тема.theme"
    editor.theme.source += "\n"
    state = (editor.theme.source, editor.theme.path, editor.theme.dirty)
    monkeypatch.setattr(QFileDialog, "exec", lambda *_: QFileDialog.DialogCode.Rejected)
    assert not editor.theme.saveAs()
    assert (editor.theme.source, editor.theme.path, editor.theme.dirty) == state


def test_failed_theme_open_and_save_keep_edits(editor, tmp_path, monkeypatch):
    editor.theme.source += "\n"
    state = (editor.theme.source, editor.theme.path, editor.theme.dirty)
    monkeypatch.setattr(QMessageBox, "warning", lambda *_: None)
    bad = tmp_path / "bad.theme"
    bad.write_bytes(b"\xff")
    assert not editor.theme.open_file(bad)
    assert not editor.theme.save_to(tmp_path)
    assert (editor.theme.source, editor.theme.path, editor.theme.dirty) == state


def test_open_cancel_protects_only_theme_and_source_open_leaves_it_dirty(editor, tmp_path, monkeypatch):
    editor.theme.source += "\n"
    state = (editor.theme.source, editor.theme.path, editor.theme.dirty)
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Cancel)
    with patch.object(QFileDialog, "getOpenFileName") as select:
        editor.theme.openFile()
        select.assert_not_called()
    assert (editor.theme.source, editor.theme.path, editor.theme.dirty) == state
    python = tmp_path / "source.py"
    python.write_text("print('new Python')\n", encoding="utf-8")
    with patch.object(QFileDialog, "getOpenFileName", return_value=(str(python), "")):
        editor.openFile()
    assert editor.source == "print('new Python')\n" and not editor.dirty
    assert (editor.theme.source, editor.theme.path, editor.theme.dirty) == state


def test_theme_only_close_cancel_then_discard(editor, monkeypatch):
    editor.theme.source += "\n"
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Cancel)
    editor.requestClose()
    assert not editor.closing and editor.theme.dirty and not editor.dirty
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Discard)
    editor.requestClose()
    assert editor.canClose and not editor.theme.scratch.exists()


def test_preview_save_cancel_failure_and_external_edits(editor, tmp_path, monkeypatch):
    editor.theme.source += "\n"
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Cancel)
    with patch.object(editor.runner, "run") as run:
        editor.previewTheme()
        run.assert_not_called()
    assert editor.theme.path is None and editor.theme.dirty
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Save)
    with patch.object(editor.runner, "run") as run:
        editor.previewTheme()
        source, = run.call_args.args
        assert source.name == "theme_preview.py"
        assert run.call_args.kwargs["arguments"] == [str(editor.theme.scratch)]
    assert editor.theme.path == editor.theme.scratch and not editor.theme.dirty
    editor.theme.path.write_text(":theme { radius: 49; }", encoding="utf-8")
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Cancel)
    assert not editor.theme.prepare_preview()
    assert editor.theme.path.read_text(encoding="utf-8") == ":theme { radius: 49; }"
    editor.theme.path = tmp_path  # Save failure must also leave child alone.
    editor.theme.source += "\n"
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Save)
    monkeypatch.setattr(QMessageBox, "warning", lambda *_: None)
    with patch.object(editor.runner, "run") as run:
        editor.previewTheme()
        run.assert_not_called()
    assert editor.theme.dirty


@pytest.mark.parametrize("answers", [
    [QMessageBox.StandardButton.Cancel],
    [QMessageBox.StandardButton.Discard, QMessageBox.StandardButton.Cancel],
    [QMessageBox.StandardButton.Save, QMessageBox.StandardButton.Cancel],
])
def test_close_cancel_keeps_both_buffers(editor, monkeypatch, answers):
    editor.source += "# Python edit\n"
    editor.theme.source += "\n"
    source, theme = editor.source, editor.theme.source
    choices = iter(answers)
    monkeypatch.setattr(QMessageBox, "question", lambda *_: next(choices))
    editor.requestClose()
    assert not editor.closing and not editor.canClose
    assert editor.source == source and editor.theme.source == theme and editor.theme.dirty
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Save)
    editor.requestClose()
    assert editor.canClose and not editor.dirty and not editor.theme.dirty
    assert editor.path.read_bytes() == source.encode("utf-8")
    assert editor.theme.path.read_bytes() == theme.encode("utf-8")


def test_visible_theme_acceptance_flow(tmp_path):
    probe = Path(__file__).with_name("playground_theme_probe.py")
    result = subprocess.run([sys.executable, str(probe), str(tmp_path)],
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "results.json").exists()
