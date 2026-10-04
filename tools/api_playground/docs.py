"""Read-only canonical API reference and search in Qt's rendered document."""
from pathlib import Path
import re

from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtQuick import QQuickItem


class DocsController(QObject):
    loadedChanged = Signal()
    searchChanged = Signal()
    linkChanged = Signal()
    selectionRequested = Signal(int, int)

    def __init__(self, repository, parent=None):
        super().__init__(parent)
        self.path = Path(repository).resolve() / "docs" / "api.md"
        self._url = QUrl.fromLocalFile(str(self.path))
        self._markdown = ""
        self._error = ""
        self._query = ""
        self._matches = []
        self._index = -1
        self._document = None
        self._quick_document = None
        self._view = None
        self._rendered_text = ""
        self._link = ""
        self.reload()

    @Property(str, notify=loadedChanged)
    def markdown(self):
        return self._markdown

    @Property(str, notify=loadedChanged)
    def error(self):
        return self._error

    @Property(str, constant=True)
    def sourcePath(self):
        return str(self.path)

    @Property(QUrl, constant=True)
    def baseUrl(self):
        return self._url

    @Property(str, notify=searchChanged)
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        if self._query != value:
            self._query = value
            self._rebuild_matches()

    @Property(str, notify=searchChanged)
    def searchStatus(self):
        if not self._query:
            return ""
        if not self._matches:
            return "No matches"
        return f"{self._index + 1} of {len(self._matches)}"

    @Property(bool, notify=searchChanged)
    def hasMatches(self):
        return bool(self._matches)

    @Property(str, notify=linkChanged)
    def linkStatus(self):
        return self._link

    @Slot()
    def reload(self):
        try:
            markdown = self.path.read_text(encoding="utf-8-sig")
            error = ""
        except (OSError, UnicodeError) as exc:
            markdown = ""
            error = f"Could not read {self.path}\n{exc}\nRestore access to the file, then press Reload."
        self._markdown, self._error = markdown, error
        self._link = ""
        self.linkChanged.emit()
        self.loadedChanged.emit()
        # Also reset the selection when the bytes did not change on Reload.
        self._rebuild_matches()

    @Slot(QObject)
    def attachView(self, text_view):
        self._view = text_view
        quick_document = text_view.property("textDocument")
        self._quick_document = quick_document
        quick_document.textDocumentChanged.connect(self._document_changed)
        self._document_changed()

    def _document_changed(self):
        # TextEdit can replace its QTextDocument while initializing Markdown.
        self._document = self._quick_document.textDocument()
        self._document.contentsChanged.connect(self._contents_changed)
        self._rendered_text = self._document.toPlainText()
        self._rebuild_matches()

    @Slot()
    def keepOverflowVisible(self):
        # Qt 6.11 enables viewport optimization again after large text layouts.
        # It omits overflowing code when scrolling far right in a long wrapped
        # document. Render all text and let Flickable clip it, after layout.
        if self._view is not None:
            self._view.setFlag(QQuickItem.Flag.ItemObservesViewport, False)

    def _contents_changed(self):
        text = self._document.toPlainText()
        # Qt also emits contentsChanged for formatting/layout updates. They
        # must not reset navigation or recursively reselect the first match.
        if text != self._rendered_text:
            self._rendered_text = text
            self._rebuild_matches()

    def _rebuild_matches(self):
        self._matches = []
        self._index = -1
        if self._document is not None and self._query and not self._error:
            cursor = QTextCursor(self._document)
            while True:
                # Qt supplies rendered-text positions, including UTF-16 offsets
                # and table cells. Never search/replace the Markdown/source.
                cursor = self._document.find(self._query, cursor)
                if cursor.isNull():
                    break
                self._matches.append((cursor.selectionStart(), cursor.selectionEnd()))
            if self._matches:
                self._index = 0
        self._show_match()

    def _show_match(self):
        self.searchChanged.emit()
        start, end = self._matches[self._index] if self._matches else (-1, -1)
        self.selectionRequested.emit(start, end)

    @Slot()
    def nextMatch(self):
        if self._matches:
            self._index = (self._index + 1) % len(self._matches)
            self._show_match()

    @Slot()
    def previousMatch(self):
        if self._matches:
            self._index = (self._index - 1) % len(self._matches)
            self._show_match()

    @Slot(str)
    def followLink(self, link):
        target = self._url.resolved(QUrl(link))
        document_url = QUrl(target)
        document_url.setFragment(None)
        if self._document is not None and target.fragment() and document_url == self._url:
            block = self._document.begin()
            while block.isValid():
                if block.blockFormat().headingLevel():
                    slug = re.sub(r"[^\w\s-]", "", block.text().lower()).replace(" ", "-")
                    if slug == target.fragment():
                        self.selectionRequested.emit(block.position(), block.position() + block.length() - 1)
                        self._link = ""
                        self.linkChanged.emit()
                        return
                block = block.next()
        self._link = f"Reference: {target.toDisplayString()} (read-only viewer)"
        self.linkChanged.emit()
