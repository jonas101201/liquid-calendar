#!/usr/bin/env python3
"""Render public screenshots with synthetic data and an isolated database."""
import datetime as dt
import os
from pathlib import Path
import sys
import tempfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
os.environ.setdefault('QT_QUICK_BACKEND','software')
os.environ.setdefault('QT_QUICK_CONTROLS_STYLE','Basic')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl,QTimer,QEventLoop,QLocale
from PySide6.QtQml import QQmlApplicationEngine
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
 bridge=Bridge(store,True);engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('planner',bridge);engine.load(QUrl.fromLocalFile(str(ROOT/'qml/App.qml')))
 if not engine.rootObjects():raise SystemExit('QML failed to load')
 window=engine.rootObjects()[0];window.setWidth(1280);window.setHeight(860)
 for view in ['today','week','agenda','tasks']:
  bridge.setView(view);settle();image=QQuickWindow.grabWindow(window)
  if not image.save(str(ROOT/'docs/screenshots'/f'{view}.png')):raise SystemExit('Could not save screenshot')
 bridge.reload_timer.stop();bridge.reminder_timer.stop();window.close();engine.deleteLater();settle()
print('Rendered public screenshots using synthetic data only.')
