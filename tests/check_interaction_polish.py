"""Real keyboard/mouse regressions using an isolated calendar and QML copy."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import patch

os.environ.update(QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software', QT_QUICK_CONTROLS_STYLE='Basic')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import QEventLoop, QTimer, Qt, QUrl, qInstallMessageHandler
from PySide6.QtQml import QQmlApplicationEngine, QQmlExpression
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from app import Bridge
from store import Store

app = QApplication([])
logs = []
qInstallMessageHandler(lambda kind, context, message: logs.append(message))

def settle(ms=80):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()

with tempfile.TemporaryDirectory(prefix='calendar-interactions-') as directory:
    temp = Path(directory)
    shutil.copytree(ROOT / 'qml', temp / 'qml')
    source = temp / 'qml/App.qml'
    source.write_text(source.read_text().replace('id:win', 'id:win\n function review(code){return eval(code);}', 1))
    editor_source=temp / 'qml/CalendarEditor.qml'
    editor_source.write_text(editor_source.read_text().replace('id: root', 'id: root\n function review(code){return eval(code);}', 1))
    store = Store(temp / 'test.sqlite')
    bridge = Bridge(store, True)
    bridge.selectDate('2026-10-28')
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty('planner', bridge)
    engine.load(QUrl.fromLocalFile(str(source)))
    assert engine.rootObjects(), logs
    win = engine.rootObjects()[0]
    win.setWidth(980)
    win.setHeight(780)
    win.requestActivate()
    def expr(code):
        expression = QQmlExpression(engine.rootContext(), win, 'review(' + json.dumps(code) + ')')
        value = expression.evaluate()
        assert not expression.hasError(), expression.error().toString()
        return value[0]
    def type_text(text):
        for char in text:QTest.keyClick(win, Qt.Key(ord(char.upper())))
    settle(300)
    assert bridge.selected == '2026-10-28', 'Editor initialization must retain a preselected date in another week.'
    for theme in ['dark', 'light']:
        bridge.setTheme(theme)
        QTest.keyClick(win, Qt.Key_K, Qt.ControlModifier)
        settle(240)
        assert expr('commandPalette.visible && commandPalette.height<win.height-40'), (theme,expr('commandPalette.visible'),expr('commandPalette.height'),logs)
        assert win.findChild(type(win.contentItem()), 'commandResults').property('contentY') == 0
        if os.environ.get('LIQUID_UX_SCREENSHOTS'):
            output=Path(os.environ['LIQUID_UX_SCREENSHOTS']);output.mkdir(parents=True,exist_ok=True)
            assert win.grabWindow().save(str(output / ('commands-'+theme+'.png')))
        assert expr('commandPalette.matches.every(function(c){return c.id!=="undo";})')
        type_text('calendar week')
        settle()
        assert expr('commandPalette.matches.length===1 && commandPalette.matches[0].id==="week"')
        QTest.keyClick(win, Qt.Key_Return)
        settle(260)
        assert bridge.view == 'week' and not expr('commandPalette.visible')
        # Esc is non-destructive, restores input focus and never executes the result.
        bridge.setView('search')
        expr('globalSearch.forceActiveFocus()')
        QTest.keyClick(win, Qt.Key_K, Qt.ControlModifier)
        settle(240)
        type_text('no such command')
        QTest.keyClick(win, Qt.Key_Down)
        QTest.keyClick(win, Qt.Key_Return)
        settle()
        assert expr('commandPalette.visible && commandPalette.matches.length===0')
        QTest.keyClick(win, Qt.Key_Escape)
        settle(240)
        assert expr('!commandPalette.visible && globalSearch.activeFocus')
        QTest.keyClick(win, Qt.Key_K, Qt.ControlModifier)
        settle(240)
        QTest.keyClick(win, Qt.Key_Up)
        QTest.keyClick(win, Qt.Key_Return)
        settle(260)
        assert expr('shortcutsPopup.visible && !commandPalette.visible')
        QTest.keyClick(win, Qt.Key_Escape)
        settle(240)
    # Commit feedback is emitted for actual successful writes only.
    notices = []
    bridge.changeCommitted.connect(notices.append)
    event = dict(id='ux', title='Synthetic task', date='', time='', minutes=60, task=True,
                 done=False, allDay=False, repeat='none', until='', category=0,
                 location='', notes='', reminder=-1)
    bridge.commit([event], label='Task saved')
    settle(240)
    assert notices == ['Task saved'] and expr('undoToast.visible && undoToast.message==="Task saved"')
    bridge.commit(bridge.events)
    assert notices == ['Task saved']
    with patch.object(store, 'merge', side_effect=OSError('synthetic save failure')):
        assert bridge.commit([]) is None
    assert notices == ['Task saved'] and len(store.read()) == 1
    bridge.clearError()
    # Text editing Undo must not undo a saved calendar mutation.
    bridge.setView('search')
    expr('globalSearch.text="";globalSearch.forceActiveFocus()')
    type_text('sample')
    QTest.keyClick(win, Qt.Key_Z, Qt.ControlModifier)
    settle()
    assert len(store.read()) == 1 and bridge.canUndo
    assert expr('globalSearch.text===""')
    # Palette opens Undo only when available, and uses the ordinary guarded operation.
    QTest.keyClick(win, Qt.Key_K, Qt.ControlModifier)
    settle(240)
    type_text('undo')
    settle()
    assert expr('commandPalette.matches.length===1')
    QTest.keyClick(win, Qt.Key_Return)
    settle(260)
    assert store.read() == [] and not bridge.canUndo and not expr('undoToast.visible')
    bridge.commit([event], label='Task saved')
    settle(240)
    assert expr('undoToast.visible')
    # Expiring the visual hint must not discard the actual Undo history.
    expr('undoExpiry.interval=60;undoExpiry.restart()')
    settle(260)
    assert not expr('undoToast.visible') and bridge.canUndo
    # Retarget an in-flight section animation without jumping back to its start.
    bridge.setView('today');settle(300)
    bridge.setView('tasks');settle(70)
    before=expr('workspace.opacity')
    bridge.setView('agenda')
    assert expr('workspace.opacity') >= before-.02
    bridge.setAnimations(False);settle(20)
    assert expr('workspace.opacity===1 && workspaceShift.y===0 && !viewArrival.running')
    # Palette cannot replace a draft currently open in an editor.
    expr('win.newEvent()')
    settle(240)
    QTest.keyClick(win, Qt.Key_K, Qt.ControlModifier)
    settle()
    assert not expr('commandPalette.visible')
    expr('editorSurface.review("titleField.text=\\"Synthetic appointment\\"")')
    before=store.read()
    with patch.object(store, 'merge', side_effect=OSError('synthetic failed save')):
        expr('editorSurface.review("saveButton.clicked()")')
    assert store.read()==before and expr('editorSurface.review("editor.visible && !editor.submitted && saveButton.enabled")')
    expr('editorSurface.review("saveButton.clicked();saveButton.clicked()")')
    settle(240)
    assert len(store.read())==len(before)+1, 'Rapid repeated Save must create exactly one event.'
    assert not expr('editorSurface.modalOpen')
    engine.deleteLater()
    settle()
    bridge.reload_timer.stop()
    bridge.reminder_timer.stop()
    assert not logs, logs
print('Command search, keyboard wrapping, empty results, focus restoration, modal guards, themes, commit feedback and text/calendar Undo passed.')
