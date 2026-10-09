"""Qt Quick editor controller; widgets are used only for native file dialogs."""
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox

from .runner import ChildRunner
from .docs import DocsController
from .theme_editor import ThemeEditor


STARTER = '''from pyui_framework import App, Button, Label, Window

status = Label("Ready — edit this code and press Run.")

def greet():
    status.set_text("Hello from your Python UI!")
    print("Button clicked")

window = Window("Playground app", status, Button("Say hello", on_click=greet))
raise SystemExit(App(window).run())
'''


class EditorController(QObject):
    sourceChanged = Signal()
    fileChanged = Signal()
    outputChanged = Signal()
    closingChanged = Signal()
    closeReady = Signal()

    def __init__(self, repository, parent=None):
        super().__init__(parent)
        self.scratch = Path(repository) / ".playground" / "scratch.py"
        self.path = None
        self._source = STARTER
        # The untouched starter is recoverable on next launch; edits need a prompt.
        self._saved_source = STARTER
        self._output = "Run saves the Python source, then opens the app in a separate window.\n"
        self._closing = False
        self._can_close = False
        self.runner = ChildRunner(self)
        self.docs = DocsController(repository, self)
        self.theme = ThemeEditor(repository, self)
        self.theme.output.connect(self._append_output)
        self.runner.output.connect(self._append_output)
        self.runner.statusChanged.connect(self._status_output)
        self.runner.idle.connect(self._idle)

    @Property(str, notify=sourceChanged)
    def source(self):
        return self._source

    @source.setter
    def source(self, text):
        if self._source != text:
            self._source = text
            self.sourceChanged.emit()
            self.fileChanged.emit()

    @Property(str, notify=fileChanged)
    def fileLabel(self):
        name = str(self.path) if self.path else "Unsaved — .playground/scratch.py on Run or Save"
        return name + (" *" if self.dirty else "")

    @property
    def dirty(self):
        return self._saved_source != self._source

    @Property(str, notify=outputChanged)
    def output(self):
        return self._output

    @Property(bool, notify=closeReady)
    def canClose(self):
        return self._can_close

    @Property(bool, notify=closingChanged)
    def closing(self):
        return self._closing

    def _append_output(self, text):
        # Keep the recent output bounded during long sessions.
        self._output = (self._output + text)[-120_000:]
        self.outputChanged.emit()

    def _status_output(self):
        self._append_output(f"[{self.runner.status}]\n")

    def _file_error(self, action, error):
        self._append_output(f"{action} failed: {error}\n")
        QMessageBox.warning(None, "API Playground", f"{action} failed:\n{error}")

    def save_to(self, path):
        """Save exactly the editor text; update the active path only on success."""
        path = Path(path).resolve()
        try:
            if path == self.scratch.resolve():
                path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="") as stream:
                stream.write(self._source)
        except (OSError, UnicodeError) as error:
            self._file_error("Save", error)
            return False
        self.path = path
        self._saved_source = self._source
        self.fileChanged.emit()
        return True

    @Slot(result=bool)
    def save(self):
        if self._closing:
            return False
        target = self.path or self.scratch
        # A fresh starter must not silently overwrite an earlier scratch session.
        if self.path is None and target.exists():
            answer = QMessageBox.question(
                None, "Replace scratch file?",
                f"Replace {target} with the current editor text?\nUse Save As to choose another file.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False
        return self.save_to(target)

    @Slot(result=bool)
    def saveAs(self):
        if self._closing:
            return False
        path, _ = QFileDialog.getSaveFileName(
            None, "Save Python source", str(self.path or self.scratch),
            "Python source (*.py);;All files (*)",
        )
        return self.save_to(path) if path else False

    def _may_discard(self):
        if not self.dirty:
            return True
        answer = QMessageBox.question(
            None, "Unsaved source", "Save the current source before continuing?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Save:
            return self.save()
        return answer == QMessageBox.StandardButton.Discard

    def open_file(self, path):
        try:
            # Accept UTF-8 BOM from other Windows editors, save as plain UTF-8.
            text = Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            self._file_error("Open", error)
            return False
        self.path = Path(path).resolve()
        self._saved_source = text
        self.source = text
        self.fileChanged.emit()
        return True

    @Slot()
    def openFile(self):
        if self._closing or not self._may_discard():
            return
        folder = self.path.parent if self.path else self.scratch.parent
        if not folder.exists():
            folder = folder.parent
        path, _ = QFileDialog.getOpenFileName(
            None, "Open Python source", str(folder), "Python source (*.py);;All files (*)",
        )
        if path:
            self.open_file(path)

    @Slot()
    def run(self):
        if not self._closing and self.save():
            self.runner.run(self.path)

    @Slot()
    def previewTheme(self):
        if self._closing or not self.theme.prepare_preview():
            return
        self._append_output("Preview Theme replaces the current child. Run (F5) relaunches Python source.\n")
        self.runner.run(Path(__file__).with_name("theme_preview.py"),
                        arguments=[str(self.theme.path)],
                        working_directory=self.theme.path.parent,
                        label=f"Preview Theme: {self.theme.path}")

    @Slot()
    def requestClose(self):
        if self._closing or not self._may_discard() or not self.theme.may_discard():
            return
        self._closing = True
        self.closingChanged.emit()
        self.runner.shutdown()

    def _idle(self):
        if self._closing:
            self._can_close = True
            self.closeReady.emit()
