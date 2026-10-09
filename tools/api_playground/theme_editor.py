"""Independent theme text buffer; validation belongs to the public framework API."""
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox

from pyui_framework import Theme, ThemeError


STARTER_THEME = """:theme {
    background: #eaf5f2;
    foreground: #173b3a;
    panel: #d6ebe4;
    accent: #126e67;
    accent-text: #ffffff;
    radius: 20;
    opacity: 1;
    gradient: linear-gradient(#126e67, #65b8a3);
}
"""


class ThemeEditor(QObject):
    sourceChanged = Signal()
    fileChanged = Signal()
    validationChanged = Signal()
    output = Signal(str)

    def __init__(self, repository, parent=None):
        super().__init__(parent)
        self.scratch = Path(repository) / ".playground" / "scratch.theme"
        self.path = None
        self._source = self._saved_source = STARTER_THEME
        self._validation = "Not validated. Use Validate to check the current text."
        self._valid = False

    @Property(str, notify=sourceChanged)
    def source(self):
        return self._source

    @source.setter
    def source(self, text):
        if self._source != text:
            self._source = text
            self._invalidate()
            self.sourceChanged.emit()
            self.fileChanged.emit()

    @property
    def dirty(self):
        return self._source != self._saved_source

    @Property(str, notify=fileChanged)
    def fileLabel(self):
        name = str(self.path) if self.path else "Unsaved — .playground/scratch.theme on Save"
        return name + (" *" if self.dirty else "")

    @Property(str, notify=validationChanged)
    def validation(self):
        return self._validation

    @Property(bool, notify=validationChanged)
    def valid(self):
        return self._valid

    def _invalidate(self):
        self._valid = False
        self._validation = "Not validated. Use Validate to check the current text."
        self.validationChanged.emit()

    @Slot(result=bool)
    def validate(self):
        source = str(self.path) if self.path else "<unsaved theme>"
        try:
            Theme.parse(self._source, source=source)
        except ThemeError as error:
            self._valid = False
            self._validation = str(error)
        else:
            self._valid = True
            self._validation = f"Valid theme: {source}"
        self.validationChanged.emit()
        self.output.emit(self._validation + "\n")
        return self._valid

    def _file_error(self, action, error):
        self.output.emit(f"{action} failed: {error}\n")
        QMessageBox.warning(None, "API Playground", f"{action} failed:\n{error}")

    def save_to(self, path):
        path = Path(path).resolve()
        try:
            if path == self.scratch.resolve():
                path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="") as stream:
                stream.write(self._source)
        except (OSError, UnicodeError) as error:
            self._file_error("Save theme", error)
            return False
        if self.path != path:
            self._invalidate()
        self.path = path
        self._saved_source = self._source
        self.fileChanged.emit()
        return True

    @Slot(result=bool)
    def save(self):
        target = self.path or self.scratch
        if self.path is None and target.exists():
            answer = QMessageBox.question(
                None, "Replace scratch theme?",
                f"Replace {target} with the current theme text?\nUse Save As to choose another file.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False
        return self.save_to(target)

    @Slot(result=bool)
    def saveAs(self):
        # A QFileDialog instance provides a default suffix and native overwrite confirmation.
        dialog = QFileDialog(None, "Save theme", str(self.path or self.scratch),
                             "Theme files (*.theme)")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix("theme")
        if dialog.exec() != QFileDialog.DialogCode.Accepted:
            return False
        return self.save_to(dialog.selectedFiles()[0])

    def may_discard(self):
        if not self.dirty:
            return True
        answer = QMessageBox.question(
            None, "Unsaved theme", "Save the current theme before continuing?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Save:
            return self.save()
        return answer == QMessageBox.StandardButton.Discard

    def open_file(self, path):
        try:
            text = Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            self._file_error("Open theme", error)
            return False
        self.path = Path(path).resolve()
        self._saved_source = text
        self.source = text
        self._invalidate()
        self.fileChanged.emit()
        return True

    @Slot()
    def openFile(self):
        if not self.may_discard():
            return
        folder = self.path.parent if self.path else self.scratch.parent
        if not folder.exists():
            folder = folder.parent
        path, _ = QFileDialog.getOpenFileName(
            None, "Open theme", str(folder), "Theme files (*.theme)",
        )
        if path:
            self.open_file(path)

    def prepare_preview(self):
        """Validate before any save or lifecycle change; Cancel leaves the child alone."""
        if not self.validate():
            return False
        # Also notice external edits/deletion so Preview uses the validated editor text.
        try:
            disk_matches = self.path is not None and self.path.read_text(
                encoding="utf-8-sig") == self._source
        except (OSError, UnicodeError):
            disk_matches = False
        if self.dirty or not disk_matches:
            answer = QMessageBox.question(
                None, "Save theme for preview",
                "Preview needs the current theme saved to disk. Save it and continue?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if answer != QMessageBox.StandardButton.Save or not self.save():
                return False
            # Refresh diagnostic context after a new path is assigned.
            return self.validate()
        return True
