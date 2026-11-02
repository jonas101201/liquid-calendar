"""Actual QML: balanced titles, continuous contours, refresh anchors, imports and interrupted popups."""
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
from unittest.mock import patch
os.environ.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_QUICK_CONTROLS_STYLE='Basic')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl,QEventLoop,QTimer,qInstallMessageHandler
from PySide6.QtQml import QQmlApplicationEngine,QQmlExpression
from app import Bridge
from import_job import ImportJob
from logic import new_event
from store import Store
app=QApplication([]);logs=[];qInstallMessageHandler(lambda kind,ctx,msg:logs.append(msg))
def settle(ms=100):
    loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
with tempfile.TemporaryDirectory(prefix='calendar-polish-details-') as directory:
    root=Path(directory);shutil.copytree(ROOT/'qml',root/'qml')
    for name,marker in [('App.qml','id:win'),('CalendarEditor.qml','id: root')]:
        p=root/'qml'/name;p.write_text(p.read_text().replace(marker,marker+'\n function review(code){return eval(code);}',1))
    store=Store(root/'data.sqlite');bridge=Bridge(store,True)
    rows=[]
    for i in range(65):
        value=new_event(dt.date(2026,11,2));value.update(id=f'task-{i:03}',title='Prepare the presentation and review the supporting documents with the project team '+str(i),task=True,date='',time='',reminder=-1,priority=2,project='Planning',checklist=[dict(id='step',title='Check the draft',done=False)])
        rows.append(value)
    store.merge(rows,[]);bridge.reload();bridge.setView('tasks')
    engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('planner',bridge);engine.load(QUrl.fromLocalFile(str(root/'qml/App.qml')));assert engine.rootObjects(),logs
    win=engine.rootObjects()[0];win.setWidth(980);win.setHeight(780);win.requestActivate()
    def expr(code):
        x=QQmlExpression(engine.rootContext(),win,'review('+json.dumps(code)+')');value=x.evaluate();assert not x.hasError(),x.error().toString();return value[0]
    settle(300)
    for theme in ['dark','light']:
        bridge.setTheme(theme);settle(220)
        expr('resultList.positionViewAtIndex(22,ListView.Beginning);resultList.forceLayout();resultList.currentIndex=23')
        expr('resultList.itemAtIndex(22).setChecklistExpanded(true)');settle(100)
        assert expr('resultList.itemAtIndex(22).checklistExpanded')
        assert expr('resultList.itemAtIndex(22).rowHeight>58')
        anchor_key=expr('resultList.recordKey(22)');anchor_id=anchor_key.split('|')[0]
        before=expr('resultList.itemAtIndex(22).y-resultList.contentY')
        selected=expr('resultList.recordKey(resultList.currentIndex)')
        # Add a newly sorted item before the viewport through a separate client.
        remote=store.read();extra=dict(rows[0],id='new-'+theme,title='AAA Newly added '+theme)
        store.merge(remote+[extra],remote);bridge.reload();settle(220)
        assert expr('resultList.recordKey(resultList.currentIndex)')==selected
        anchor=expr('resultList.indexFor('+json.dumps(anchor_key)+')')
        assert abs(expr(f'resultList.itemAtIndex({anchor}).y-resultList.contentY')-before)<2
        assert expr(f'resultList.itemAtIndex({anchor}).checklistExpanded')
        # An update to the same record retains selection and expanded checklist.
        remote=store.read();changed=[dict(row,notes='External update') if row['id']==anchor_id else row for row in remote]
        store.merge(changed,remote);bridge.reload();settle(220)
        anchor=expr('resultList.indexFor('+json.dumps(anchor_key)+')')
        assert expr(f'resultList.itemAtIndex({anchor}).checklistExpanded')
        assert expr('resultList.recordKey(resultList.currentIndex)')==selected
        if os.environ.get('LIQUID_POLISH_SCREENSHOTS'):
            output=Path(os.environ['LIQUID_POLISH_SCREENSHOTS']);output.mkdir(parents=True,exist_ok=True)
            assert win.grabWindow().save(str(output/('polish-'+theme+'.png')))
        # A popup reopened during its exit must continue from the current opacity.
        expr('win.openQuick()');settle(240);expr('quickPopup.close()');settle(45)
        opacity=expr('quickPopup.opacity');scale=expr('quickPopup.scale')
        expr('quickPopup.open()');settle(5)
        assert expr('quickPopup.opacity')>=opacity-.05
        assert expr('quickPopup.scale')>=scale-.01
        settle(230);assert expr('quickPopup.opacity===1 && quickPopup.scale===1')
        expr('quickPopup.close()');settle(160)
        expr('win.openQuick()');settle(35);bridge.setAnimations(False);settle(10)
        assert expr('quickPopup.opacity===1 && quickPopup.scale===1'), (expr('quickPopup.opacity'),expr('quickPopup.scale'),logs)
        expr('quickPopup.close()');settle(20);assert not expr('quickPopup.visible')
        bridge.setAnimations(True)
        expr('editorSurface.review("mergeDialog.open()")');settle(240)
        expr('editorSurface.review("mergeDialog.close()")');settle(45)
        previous=expr('editorSurface.review("mergeDialog.opacity")')
        expr('editorSurface.review("mergeDialog.open()")');settle(5)
        assert expr('editorSurface.review("mergeDialog.opacity")')>=previous-.05
        bridge.setAnimations(False);settle(10)
        assert expr('editorSurface.review("mergeDialog.opacity===1 && mergeDialog.scale===1")')
        expr('editorSurface.review("mergeDialog.close()")');settle(20)
        bridge.setAnimations(True)
    # Keep the actual calendar visible while a genuinely slow backup read is in flight.
    entered=threading.Event();release=threading.Event();original=ImportJob.read_document
    def held(job):entered.set();release.wait(3);return original(job)
    backup=root/'import.json';backup.write_text(json.dumps({'format':'liquid-glass-calendar','version':1,'events':[]}))
    with patch.object(ImportJob,'read_document',held):
        bridge.startImport(backup.as_uri());settle(450)
        assert entered.is_set() and expr('importProgressPopup.visible') and expr('resultList.count>60')
        bridge.cancelImport();release.set();settle(300)
        assert not bridge.importBusy and not expr('importProgressPopup.visible')
    bridge.startImport(backup.as_uri());settle(180)
    assert not bridge.importBusy and not expr('importProgressPopup.visible'), 'Fast imports must not flash a loader.'
    bridge.reload_timer.stop();bridge.reminder_timer.stop();engine.deleteLater();settle()
    assert not logs,logs
print('Balanced multi-line task rows, refresh anchor/selection/checklist preservation, popup retarget/reduced motion, delayed loader and cancellation passed in both themes.')
