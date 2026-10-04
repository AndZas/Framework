"""One asynchronous child process, using the editor's Python environment."""
import codecs
from pathlib import Path
import sys

from PySide6.QtCore import QObject, Property, QProcess, QProcessEnvironment, QTimer, Signal, Slot


class ChildRunner(QObject):
    output = Signal(str)
    statusChanged = Signal()
    activeChanged = Signal()
    idle = Signal()

    def __init__(self, parent=None, *, executable=None, stop_timeout_ms=1500):
        super().__init__(parent)
        self._executable = executable or sys.executable
        self._status = "Ready"
        self._active = False
        self._stopping = False
        self._closing = False
        self._pending = None
        self.process = QProcess(self)
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("PYTHONIOENCODING", "utf-8")
        environment.insert("PYTHONUNBUFFERED", "1")
        self.process.setProcessEnvironment(environment)
        self.process.started.connect(self._started)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._error)
        self.process.readyReadStandardOutput.connect(self._stdout)
        self.process.readyReadStandardError.connect(self._stderr)
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.setInterval(stop_timeout_ms)
        self._kill_timer.timeout.connect(self._kill)
        self._reset_decoders()

    @Property(str, notify=statusChanged)
    def status(self):
        return self._status

    @Property(bool, notify=activeChanged)
    def active(self):
        # Includes startup and shutdown, not just QProcess.Running.
        return self._active

    def _set_status(self, status):
        self._status = status
        self.statusChanged.emit()

    def _reset_decoders(self):
        self._out_decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self._err_decoder = codecs.getincrementaldecoder("utf-8")("replace")

    def run(self, source):
        if self._closing:
            return
        self._pending = Path(source).resolve()
        if self._active:
            self._begin_stop()
        else:
            self._launch_pending()

    def _launch_pending(self):
        if self._active or self._pending is None or self._closing:
            return
        source, self._pending = self._pending, None
        self._reset_decoders()
        self._stopping = False
        self._active = True
        self.activeChanged.emit()
        self.process.setWorkingDirectory(str(source.parent))
        # QProcess receives program and arguments separately; no shell or quoting.
        self.process.setProgram(self._executable)
        self.process.setArguments(["-u", str(source)])
        self.output.emit(f"\n>>> Run: {source}\n")
        self._set_status("Starting…")
        self.process.start()

    def _started(self):
        if self._stopping:
            # Stop can arrive while QProcess is still Starting.
            self.process.terminate()
        else:
            self._set_status(f"Running (PID {self.process.processId()})")

    @Slot()
    def stop(self):
        self._pending = None
        if self._active:
            self._begin_stop()

    def shutdown(self):
        self._closing = True
        self._pending = None
        if self._active:
            self._begin_stop()
        else:
            self.idle.emit()

    def _begin_stop(self):
        if self._stopping:
            return
        self._stopping = True
        self._set_status("Stopping…")
        self.process.terminate()
        self._kill_timer.start()

    def _kill(self):
        if self._active:
            self.output.emit("Child did not stop in time; killing it.\n")
            self.process.kill()

    def _stdout(self):
        text = self._out_decoder.decode(bytes(self.process.readAllStandardOutput()))
        if text:
            self.output.emit(text)

    def _stderr(self):
        text = self._err_decoder.decode(bytes(self.process.readAllStandardError()))
        if text:
            self.output.emit(text)

    def _error(self, error):
        self.output.emit(f"Process error: {self.process.errorString()}\n")
        if error == QProcess.ProcessError.FailedToStart:
            # FailedToStart has no finished signal.
            self._complete("Failed to start")

    def _finished(self, code, exit_status):
        self._stdout()
        self._stderr()
        for decoder in (self._out_decoder, self._err_decoder):
            tail = decoder.decode(b"", final=True)
            if tail:
                self.output.emit(tail)
        if self._stopping:
            status = f"Stopped (exit code {code})"
        elif exit_status == QProcess.ExitStatus.CrashExit:
            status = f"Crashed (exit code {code})"
        else:
            status = f"Exited (code {code})"
        self._complete(status)

    def _complete(self, status):
        self._kill_timer.stop()
        self._active = False
        self._stopping = False
        self._set_status(status)
        self.activeChanged.emit()
        if self._pending is not None and not self._closing:
            QTimer.singleShot(0, self._launch_pending)
        else:
            self.idle.emit()
