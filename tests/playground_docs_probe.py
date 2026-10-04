"""Visible Windows docs acceptance flow using synthetic Qt input, not physical input."""
from pathlib import Path
import hashlib
import json
import os
import platform
import sys
import tempfile
import time
from unittest.mock import patch

import shiboken6
from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QCoreApplication, QObject, QPoint, QPointF, Qt, qVersion
from PySide6.QtGui import QInputMethodEvent, QTextTable
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

from tools.api_playground.__main__ import create_editor


def wait_until(predicate, timeout=8000):
    deadline = time.monotonic() + timeout / 1000
    while not predicate() and time.monotonic() < deadline:
        QTest.qWait(20)
    assert predicate(), "Timed out waiting for docs acceptance flow"


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    canonical = REPOSITORY / "docs" / "api.md"
    original = canonical.read_bytes()
    QQuickStyle.setStyle("Basic")
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    results = {
        "platform": platform.platform(), "python": sys.version,
        "executable": sys.executable, "pyside": pyside_version, "qt": qVersion(),
        "input": "synthetic QtTest mouse/key and QInputMethodEvent; file dialogs stubbed",
        "checks": [],
    }

    def click(name):
        item = window.findChild(QObject, name)
        assert item is not None and item.isVisible(), name
        point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
        QTest.mouseClick(window, Qt.MouseButton.LeftButton,
                         pos=QPoint(round(point.x()), round(point.y())))
        QTest.qWait(50)

    def search_for(text):
        field = window.findChild(QObject, "docsSearch")
        field.forceActiveFocus()
        QTest.keyClick(window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        event = QInputMethodEvent()
        event.setCommitString(text)
        QCoreApplication.sendEvent(window, event)
        QTest.qWait(50)
        assert editor.docs.query == text

    def capture(name):
        QTest.qWait(100)
        assert window.grabWindow().save(str(output / name))

    with tempfile.TemporaryDirectory(prefix="playground docs outside cwd ") as temporary:
        folder = Path(temporary)
        old_cwd = Path.cwd()
        os.chdir(folder)
        editor, engine, window = create_editor(app)
        try:
            wait_until(lambda: window.isExposed())
            assert editor.docs.path == canonical
            assert editor.docs.markdown == original.decode("utf-8-sig").replace("\r\n", "\n")
            results["checks"].append("default startup loads current canonical docs independent of cwd")
            click("docsTab")
            document = window.findChild(QObject, "docsDocument")
            native = document.property("textDocument").textDocument()
            tables = [frame for frame in native.rootFrame().childFrames() if isinstance(frame, QTextTable)]
            assert len(tables) >= 7 and all(table.columns() >= 2 for table in tables)
            formats = {"headings": 0, "lists": 0, "code_lines": 0, "links": 0, "inline_code": 0}
            block = native.begin()
            while block.isValid():
                formats["headings"] += bool(block.blockFormat().headingLevel())
                formats["lists"] += bool(block.textList())
                formats["code_lines"] += block.blockFormat().nonBreakableLines()
                fragments = block.begin()
                while not fragments.atEnd():
                    fmt = fragments.fragment().charFormat()
                    formats["links"] += fmt.isAnchor()
                    formats["inline_code"] += fmt.fontFixedPitch() and not block.blockFormat().nonBreakableLines()
                    fragments += 1
                block = block.next()
            assert all(formats.values()), formats
            results["native_markdown"] = dict(tables=len(tables), **formats)
            capture("docs-overview.png")
            search_for("Public member")
            assert document.property("selectedText").lower() == "public member"
            capture("docs-table.png")
            search_for("Current API boundaries")
            capture("docs-lists.png")
            # Activate the actual rendered internal link with Qt mouse input.
            search_for("see Animations")
            start = document.property("selectionStart") + 4
            point_rect = document.positionToRectangle(start)
            point = document.mapToScene(QPointF(point_rect.x() + 8, point_rect.y() + point_rect.height() / 2))
            QTest.mouseClick(window, Qt.MouseButton.LeftButton,
                             pos=QPoint(round(point.x()), round(point.y())))
            QTest.qWait(50)
            assert document.property("selectedText") == "Animations"
            assert not editor.docs.linkStatus
            heading = native.begin()
            while heading.isValid() and not (heading.blockFormat().headingLevel() and heading.text() == "Animations"):
                heading = heading.next()
            assert heading.isValid() and document.property("selectionStart") == heading.position()
            capture("docs-anchor.png")
            # Relative file links display a target without opening a file/window.
            search_for("theme file example")
            point_rect = document.positionToRectangle(document.property("selectionStart"))
            point = document.mapToScene(QPointF(point_rect.x() + 8, point_rect.y() + point_rect.height() / 2))
            QTest.mouseClick(window, Qt.MouseButton.LeftButton,
                             pos=QPoint(round(point.x()), round(point.y())))
            QTest.qWait(50)
            assert "examples/lagoon.theme" in editor.docs.linkStatus
            results["checks"].append("native headings, tables, lists, inline/fenced code and rendered internal link")
        finally:
            window.close()
            QTest.qWait(50)
            shiboken6.delete(engine)

        # Reload/failure checks use a temporary checkout; canonical bytes stay untouched.
        path = folder / "docs" / "api.md"
        path.parent.mkdir()
        fixture = original.decode("utf-8-sig") + "\n\n## Probe\n\n🌍 needle NEEDLE\n\n```python\n" + "long_code_" * 150 + "\n```\n"
        path.write_text(fixture, encoding="utf-8")
        editor, engine, window = create_editor(app, repository=folder)
        try:
            wait_until(lambda: window.isExposed())
            click("docsTab")
            document = window.findChild(QObject, "docsDocument")
            scroll = window.findChild(QObject, "docsScroll")
            flick = scroll.property("contentItem")
            source = "import os, time\nprint('docs-child-ready', os.getpid())\ntime.sleep(30)\n"
            editor.source = source
            saved = folder / "user source with spaces.py"
            with patch.object(QFileDialog, "getSaveFileName", return_value=(str(saved), "")):
                click("saveAsButton")
            click("runButton")
            wait_until(lambda: "docs-child-ready" in editor.output)
            pid = editor.runner.process.processId()
            editor.source += "# unsaved source remains\n"
            source = editor.source
            assert editor.dirty

            search_for("needle")
            assert editor.docs.searchStatus == "1 of 2" and document.property("selectedText") == "needle"
            first = document.property("selectionStart")
            click("nextDocsMatch")
            assert editor.docs.searchStatus == "2 of 2" and document.property("selectedText") == "NEEDLE", (editor.docs.searchStatus, document.property("selectedText"))
            click("nextDocsMatch")
            assert document.property("selectionStart") == first
            QTest.keyClick(window, Qt.Key.Key_F3, Qt.KeyboardModifier.ShiftModifier)
            assert editor.docs.searchStatus == "2 of 2"
            click("previousDocsMatch")
            assert editor.docs.searchStatus == "1 of 2"
            window.findChild(QObject, "docsSearch").forceActiveFocus()
            QTest.keyClick(window, Qt.Key.Key_Return)
            assert editor.docs.searchStatus == "2 of 2"
            QTest.keyClick(window, Qt.Key.Key_F3)
            assert editor.docs.searchStatus == "1 of 2"
            before_text = document.property("textDocument").textDocument().toPlainText()
            document.forceActiveFocus()
            QTest.keyClick(window, Qt.Key.Key_X)
            assert document.property("textDocument").textDocument().toPlainText() == before_text
            capture("docs-search.png")
            click("clearDocsSearch")
            assert not editor.docs.query and not document.property("selectedText")
            QTest.keyClick(window, Qt.Key.Key_F, Qt.KeyboardModifier.ControlModifier)
            assert window.findChild(QObject, "docsSearch").hasActiveFocus()
            search_for("no such docs match 0013")
            assert editor.docs.searchStatus == "No matches"
            QTest.keyClick(window, Qt.Key.Key_Escape)
            assert not editor.docs.query

            search_for("needle")
            path.write_text(fixture + "\nReloaded needle\n", encoding="utf-8")
            click("reloadDocsButton")
            assert "Reloaded needle" in editor.docs.markdown and editor.docs.searchStatus == "1 of 3"
            assert editor.source == source and editor.dirty
            assert editor.runner.active and editor.runner.process.processId() == pid
            results["checks"].append("literal Unicode-aware rendered search, next/previous/wrap, no-match, Clear/Esc/Ctrl+F; reload keeps query and child/source state")

            window.setWidth(560)
            window.setHeight(440)
            search_for("long_code_")
            QTest.qWait(100)
            assert flick.property("contentWidth") > flick.property("width") * 2
            assert flick.property("contentHeight") > flick.property("height")
            assert scroll.height() >= 60, scroll.height()
            capture("docs-long-line-start.png")
            click("clearDocsSearch")
            flick.setProperty("contentX", flick.property("contentWidth") - flick.property("width"))
            assert flick.property("contentX") > 0
            capture("docs-long-line-narrow.png")
            # Check actual painted text, not just scroll extents: Qt's default
            # viewport optimization previously left this far-right view blank.
            painted = window.grabWindow()
            origin = scroll.mapToScene(QPointF(0, 0))
            blue_ink = 0
            for y in range(round(origin.y()) + 8, round(origin.y() + scroll.height()) - 8):
                for x in range(round(origin.x()) + 8, round(origin.x() + scroll.width()) - 8):
                    color = painted.pixelColor(x, y)
                    blue_ink += color.blue() > color.red() + 15 and color.red() < 200
            assert blue_ink > 100, "Far-right code text must actually render"
            search_for("long_code_")
            click("previousDocsMatch")
            assert editor.docs.searchStatus == "150 of 150"
            assert document.property("selectedText") == "long_code_"
            assert flick.property("contentX") > 10000
            click("clearDocsSearch")
            for name in ("docsSearch", "reloadDocsButton", "clearDocsSearch", "nextDocsMatch"):
                item = window.findChild(QObject, name)
                point = item.mapToScene(QPointF(0, 0))
                assert point.x() >= 0 and point.x() + item.width() <= window.width(), name
            results["checks"].append("minimum 560x440 window retains controls; long code and long document scroll horizontally/vertically")

            window.setWidth(1000)
            window.setHeight(760)
            path.unlink()
            click("reloadDocsButton")
            assert editor.docs.error and not editor.docs.markdown
            assert window.findChild(QObject, "docsError").isVisible()
            assert not editor.docs.hasMatches
            capture("docs-missing.png")
            click("stopButton")
            wait_until(lambda: not editor.runner.active)
            opened = folder / "other source.py"
            opened.write_text("print('works during docs error')\n", encoding="utf-8")
            # Save and Open still work while the docs error is visible.
            click("saveButton")
            assert saved.read_text(encoding="utf-8") == source
            with patch.object(QFileDialog, "getOpenFileName", return_value=(str(opened), "")):
                click("openButton")
            click("runButton")
            wait_until(lambda: not editor.runner.active)
            assert "works during docs error" in editor.output
            assert editor.source == opened.read_text(encoding="utf-8")
            path.write_text("# Recovered\n\nneedle after retry\n", encoding="utf-8")
            click("reloadDocsButton")
            assert not editor.docs.error and "Recovered" in document.property("text")
            assert editor.source == opened.read_text(encoding="utf-8")
            search_for("needle")
            assert document.property("selectedText") == "needle"
            capture("docs-recovered.png")
            click("sourceTab")
            assert window.findChild(QObject, "sourceEditor").property("text") == editor.source
            results["checks"].append("missing docs shows inline error; Stop/Save/Open/Run stay usable; Reload recovers and source tab retains buffer")
        finally:
            editor.source = editor._saved_source
            editor.runner.shutdown()
            wait_until(lambda: not editor.runner.active)
            window.close()
            QTest.qWait(50)
            shiboken6.delete(engine)
            os.chdir(old_cwd)

    assert canonical.read_bytes() == original
    results["canonical_sha256"] = hashlib.sha256(original).hexdigest()
    (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
