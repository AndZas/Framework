"""Canonical file loading failures and a visible Qt Quick acceptance probe."""
from pathlib import Path
import subprocess
import sys

import pytest

from tools.api_playground.docs import DocsController


def test_docs_path_is_independent_of_cwd(tmp_path, monkeypatch):
    repository = tmp_path / "checkout"
    path = repository / "docs" / "api.md"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"\xef\xbb\xbf# Reference\n")
    monkeypatch.chdir(tmp_path)
    docs = DocsController(repository)
    assert docs.sourcePath == str(path)
    assert docs.markdown == "# Reference\n" and not docs.error
    path.write_text("# Changed\n", encoding="utf-8")
    docs.reload()
    assert docs.markdown == "# Changed\n"


@pytest.mark.parametrize("failure", ["missing", "directory", "encoding", "permission"])
def test_read_error_can_be_retried(tmp_path, monkeypatch, failure):
    path = tmp_path / "docs" / "api.md"
    path.parent.mkdir()
    if failure == "directory":
        path.mkdir()
    elif failure == "encoding":
        path.write_bytes(b"\xff")
    if failure == "permission":
        def denied(*_args, **_kwargs):
            raise PermissionError("denied")
        with monkeypatch.context() as patch:
            patch.setattr(Path, "read_text", denied)
            docs = DocsController(tmp_path)
    else:
        docs = DocsController(tmp_path)
    assert not docs.markdown
    assert str(path) in docs.error and "Reload" in docs.error
    if failure == "directory":
        path.rmdir()
    path.write_text("# Recovered\n", encoding="utf-8")
    docs.reload()
    assert docs.markdown == "# Recovered\n" and not docs.error


def test_visible_docs_acceptance_flow(tmp_path):
    probe = Path(__file__).with_name("playground_docs_probe.py")
    result = subprocess.run([sys.executable, str(probe), str(tmp_path)],
                            capture_output=True, text=True, encoding="utf-8", timeout=45)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "results.json").exists()
