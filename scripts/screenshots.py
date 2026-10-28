#!/usr/bin/env python3
"""Render public screenshots with synthetic data and an isolated database."""
import datetime as dt
import os
from pathlib import Path
import sys
import tempfile
import json
import shutil
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
os.environ.setdefault('QT_QUICK_BACKEND','software')
os.environ.setdefault('QT_QUICK_CONTROLS_STYLE','Basic')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl,QTimer,QEventLoop,QLocale
from PySide6.QtQml import QQmlApplicationEngine,QQmlExpression
from PySide6.QtQuick import QQuickWindow
from app import Bridge
from store import Store
QLocale.setDefault(QLocale('en_GB'))
app=QApplication([])
def settle(ms=300):
 loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
with tempfile.TemporaryDirectory(prefix='liquid-public-screenshots-') as folder:
 store=Store(Path(folder)/'demo.sqlite');day=dt.date.today().isoformat()
 def event(ident,title,time,**kw):
  e=dict(id=ident,title=title,date=day,time=time,minutes=45,allDay=False,task=False,done=False,repeat='none',until='',category=0,location='',notes='',reminder=10);e.update(kw);return e
 store.merge([event('demo-design','Design review','10:00',category=1,location='Studio'),event('demo-lunch','Lunch with the team','12:30',category=3),event('demo-plan','Plan next week','16:00',category=0,repeat='weekly'),event('demo-task','Explore new ideas','',date='',task=True,reminder=-1,minutes=30,category=2,priority=3,project='Creative studio',checklist=[dict(id='ideas',title='Collect inspiration',done=True),dict(id='sketch',title='Sketch three concepts',done=False)]),event('demo-notes','Write project notes','',date='',task=True,reminder=-1,minutes=45,category=1,priority=2,project='Creative studio')],[])
 qml=Path(folder)/'qml';shutil.copytree(ROOT/'qml',qml)
 for name,needle in [('App.qml','id:win'),('CalendarEditor.qml','id: root')]:
  file=qml/name;file.write_text(file.read_text().replace(needle,needle+'\n function review(code){return eval(code);}',1))
 bridge=Bridge(store,True);bridge.saveTemplate('Design review',json.dumps(event('template','Design review','10:00',category=1,location='Studio')));engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('planner',bridge);engine.load(QUrl.fromLocalFile(str(qml/'App.qml')))
 if not engine.rootObjects():raise SystemExit('QML failed to load')
 window=engine.rootObjects()[0];window.setWidth(1280);window.setHeight(860)
 for view in ['today','week','agenda','tasks']:
  bridge.setView(view);settle();image=QQuickWindow.grabWindow(window)
  if not image.save(str(ROOT/'docs/screenshots'/f'{view}.png')):raise SystemExit('Could not save screenshot')
 def run(code):
  expression=QQmlExpression(engine.rootContext(),window,'review('+json.dumps(code)+')');expression.evaluate()
  if expression.hasError():raise RuntimeError(expression.error().toString())
 def capture(name):
  settle()
  if not QQuickWindow.grabWindow(window).save(str(ROOT/'docs/screenshots'/name)):raise SystemExit('Could not save screenshot')
 bridge.setView('today');run('win.openQuick();quickInput.text="Tomorrow 15:00 Dentist for 45m";quickPopup.refresh()');capture('quick-add.png');run('quickPopup.close()')
 bridge.edit('demo-design',day,False);settle();run('editorSurface.review('+json.dumps('datePicker.openFor(dateField.text)')+')');capture('date-picker.png');run('editorSurface.review("datePicker.close();editor.close()")')
 run('templateLibrary.open()');capture('templates.png');run('templateLibrary.close()')
 run('toolsButton.clicked()');capture('creation-menu.png');run('creationMenu.close()')
 bridge.edit('demo-design',day,False);settle();run('editorSurface.review('+json.dumps('repeatBox.currentIndex=2;editor.selectedWeekdays=[0,2,4];editor.detailsExpanded=true')+')');capture('weekly-repeat.png');run('editorSurface.review("editor.close()")')
 bridge.reload_timer.stop();bridge.reminder_timer.stop();window.close();engine.deleteLater();settle()
print('Rendered public screenshots using synthetic data only.')
