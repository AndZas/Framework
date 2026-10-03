"""Visible QtTest input, render equality and state assertions; no physical input."""
import json
import platform
import sys
from pathlib import Path
import PySide6
from PySide6.QtCore import QPoint, QPointF, Qt, qVersion, qInstallMessageHandler
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest
from app import build, HERE, delete
from theme import DEFAULTS, CUSTOM, resolve

out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / 'evidence'
out.mkdir(parents=True, exist_ok=True)
messages = []
qInstallMessageHandler(lambda kind, context, message: messages.append(message))
app, engine, lab = build()
window = engine.rootObjects()[0]
QTest.qWait(500)
assert window.isVisible()
steps = []


def find(name, item=None):
    item = item or window.contentItem()
    if item.objectName() == name:
        return item
    for child in item.childItems():
        found = find(name, child)
        if found is not None:
            return found
    return None


def click(name):
    item = find(name)
    assert item is not None, name
    point = item.mapToScene(item.boundingRect().center()).toPoint()
    assert 0 <= point.y() < window.height(), (name, point)
    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
    QTest.qWait(100)
    steps.append(dict(action=name, mode=lab.mode, palette=lab.palette,
                      local=lab.local.appearance, status=lab.status))


initial = lab.local.appearance.copy()
assert initial == lab.method.appearance
click('selectDark')
assert lab.palette['background'] == '#131a2a'
assert lab.local.appearance['accent'] == '#b45309'
click('selectLight')
assert lab.palette == DEFAULTS
click('selectCSS')
assert lab.palette == resolve(CUSTOM)
css_image = window.grabWindow()
css_image.save(str(out / 'css.png'))
click('selectPython')
assert lab.palette == resolve(CUSTOM)
python_image = window.grabWindow()
python_image.save(str(out / 'python.png'))
# Compare rendered theme samples above the source-dependent status text.
assert css_image.copy(0, 260, css_image.width(), 390) == python_image.copy(0, 260, python_image.width(), 390)
click('updateLocal')
assert lab.local.appearance['accent'] == '#8e3e91'
assert lab.local.appearance['radius'] == 24
assert lab.local.appearance['opacity'] == 0.8
assert lab.method.appearance['accent'] == '#b45309'
click('selectDark')
assert lab.local.appearance['accent'] == '#8e3e91'
window.grabWindow().save(str(out / 'dark-local.png'))
click('clearLocal')
assert lab.local.appearance == lab.palette
before = lab.palette.copy()
lab.load(str(out / 'missing.theme'))
assert lab.palette == before and 'missing.theme' in lab.status
bad = out / 'invalid.theme'
bad.write_text(':theme { opacity: 2; }', encoding='utf-8')
lab.load(str(bad))
assert lab.palette == before and 'opacity' in lab.status and 'invalid.theme' in lab.status
bad.unlink()
path = find('themePath')
path.setProperty('text', str(HERE / 'lagoon.theme'))
click('loadFile')
assert lab.palette == resolve(CUSTOM)
click('selectSystem')
scheme = app.styleHints().colorScheme().name
assert (lab.mode == 'System') if scheme != 'Unknown' else ('Unknown' in lab.status)
click('selectCSS')
window.setWidth(620)
window.setHeight(520)
QTest.qWait(250)
window.grabWindow().save(str(out / 'narrow.png'))
for name in ('selectCSS', 'globalSample', 'localSample', 'methodSample', 'themePath'):
    item = find(name)
    pos = item.mapToScene(QPoint(0, 0))
    assert pos.x() >= 0 and pos.x() + item.width() <= window.width(), name
# Scroll the short window using actual synthetic wheel events, then inspect status.
for _ in range(12):
    QTest.wheelEvent(window, QPoint(580, 450), QPoint(0, -120))
    QTest.qWait(30)
QTest.qWait(300)
status = find('status')
status_pos = status.mapToScene(QPointF(0, 0))
assert 0 <= status_pos.y() < window.height(), status_pos
window.grabWindow().save(str(out / 'narrow-scrolled.png'))
try:
    lab.local.set_style(opacity=3)
    raise AssertionError('invalid override accepted')
except ValueError:
    assert lab.local.appearance == lab.palette
result = dict(python=sys.version, windows=platform.platform(), pyside=PySide6.__version__,
              qt=qVersion(), system_scheme=scheme, messages=messages, steps=steps,
              visible=True, render_equality=True, physical_input=False)
window.close()
delete(engine)
(out / 'probe.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
assert not messages, messages
print(json.dumps({k: v for k, v in result.items() if k != 'steps'}, indent=2))
