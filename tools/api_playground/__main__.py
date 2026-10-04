"""Run with the repository environment: python -m tools.api_playground."""
from pathlib import Path
import sys

import shiboken6

from PySide6.QtGui import QFontDatabase
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from .editor import EditorController


def create_editor(app, repository=None):
    repository = repository or Path(__file__).resolve().parents[2]
    controller = EditorController(repository)
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("editor", controller)
    context.setContextProperty("runner", controller.runner)
    context.setContextProperty("apiDocs", controller.docs)
    context.setContextProperty("codeFont", QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    engine.load(str(Path(__file__).with_name("Main.qml")))
    if not engine.rootObjects():
        raise RuntimeError("Could not load the API Playground editor")
    return controller, engine, engine.rootObjects()[0]


def main():
    QQuickStyle.setStyle("Basic")
    app = QApplication(sys.argv)
    app.setApplicationName("API Playground")
    controller, engine, window = create_editor(app)
    result = app.exec()
    # Normal close is gated by runner.idle in QML; never block with waitForFinished.
    # Destroy QML while its context objects are still alive.
    shiboken6.delete(engine)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
