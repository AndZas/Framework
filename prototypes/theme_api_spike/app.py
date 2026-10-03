"""Standalone, provisional authoring API; UI-thread updates only."""
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl
from PySide6.QtGui import QGuiApplication, Qt
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from theme import Theme, CUSTOM, DARK, resolve, validate

HERE = Path(__file__).resolve().parent


class Widget(QObject):
    changed = Signal()

    def __init__(self, theme, *, style=None):
        super().__init__()
        self.theme = theme
        self.override = validate(style or {}, 'constructor style')

    @Property('QVariantMap', notify=changed)
    def appearance(self):
        return resolve(self.theme, self.override)

    def set_style(self, **style):
        """Replace the complete local style; empty call clears it atomically."""
        self.override = validate(style, 'set_style')
        self.changed.emit()


class Lab(QObject):
    changed = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.theme = Theme('Light')
        self.mode = 'Light'
        self.message = 'Choose an authoring source. The amber button keeps its local style.'
        self.local = Widget(self.theme, style=dict(accent='#b45309', accent_text='#ffffff', radius=6, opacity=1))
        self.method = Widget(self.theme)
        self.method.set_style(accent='#b45309', accent_text='#ffffff', radius=6, opacity=1)
        self.alternate = False
        app.styleHints().colorSchemeChanged.connect(self.system_changed)

    @Property('QVariantMap', notify=changed)
    def palette(self):
        return resolve(self.theme)

    @Property(str, notify=changed)
    def gradientStart(self):
        return self.palette['gradient'][0]

    @Property(str, notify=changed)
    def gradientEnd(self):
        return self.palette['gradient'][1]

    @Property(str, notify=changed)
    def status(self):
        return f'{self.mode} · {self.message}'

    @Property(str, notify=changed)
    def system(self):
        return f'Qt system scheme: {self.app.styleHints().colorScheme().name}. Live OS transition requires owner verification.'

    @Property(str, constant=True)
    def defaultPath(self):
        return str(HERE / 'lagoon.theme')

    @Slot(str)
    def select(self, mode):
        try:
            if mode == 'CSS':
                theme = Theme.load(HERE / 'lagoon.theme')
            elif mode == 'Python':
                theme = CUSTOM
            elif mode == 'System':
                scheme = self.app.styleHints().colorScheme()
                if scheme == Qt.ColorScheme.Unknown:
                    raise ValueError('Qt reports Unknown; retained previous theme, no guessed fallback')
                theme = Theme('System', **(DARK if scheme == Qt.ColorScheme.Dark else {}))
            elif mode in ('Light', 'Dark'):
                theme = Theme(mode, **(DARK if mode == 'Dark' else {}))
            else:
                raise ValueError(f'Unknown mode: {mode}')
            self.apply(theme, mode)
        except (ValueError, OSError) as error:
            self.message = str(error)
            self.changed.emit()

    def apply(self, theme, mode):
        self.theme, self.mode = theme, mode
        for widget in (self.local, self.method):
            widget.theme = theme
            widget.changed.emit()
        self.message = 'Applied atomically; missing tokens use built-in defaults.'
        self.changed.emit()

    @Slot(str)
    def load(self, path):
        try:
            self.apply(Theme.load(path), 'CSS file')
        except (ValueError, OSError) as error:
            self.message = str(error)
            self.changed.emit()

    @Slot()
    def update_local(self):
        self.alternate = not self.alternate
        self.local.set_style(accent='#8e3e91' if self.alternate else '#b45309',
                             accent_text='#ffffff', radius=24 if self.alternate else 6,
                             opacity=0.8 if self.alternate else 1)
        self.message = 'Python callback replaced constructor widget style; method twin stays amber.'
        self.changed.emit()

    @Slot()
    def clear_local(self):
        self.local.set_style()
        self.message = 'Local style cleared: constructor widget now follows global theme.'
        self.changed.emit()

    def system_changed(self, *_):
        if self.mode == 'System':
            self.select('System')
        self.changed.emit()


def build():
    QQuickStyle.setStyle('Basic')
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    lab = Lab(app)
    for name, obj in [('lab', lab), ('localWidget', lab.local), ('methodWidget', lab.method)]:
        engine.rootContext().setContextProperty(name, obj)
    engine.load(QUrl.fromLocalFile(str(HERE / 'Main.qml')))
    if not engine.rootObjects():
        raise RuntimeError('Theme lab QML failed to load')
    return app, engine, lab


if __name__ == '__main__':
    app, engine, lab = build()
    result = app.exec()
    # Destroy QML bindings while the Python context objects are still alive.
    delete(engine)
    raise SystemExit(result)
