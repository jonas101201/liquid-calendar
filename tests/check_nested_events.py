"""Actual nested-card geometry and edit targets, with synthetic calendar data."""
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
os.environ.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_QUICK_CONTROLS_STYLE='Basic')
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl,QEventLoop,QTimer,QPoint,Qt,qInstallMessageHandler
from PySide6.QtQml import QQmlApplicationEngine,QQmlExpression
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest
from app import Bridge
from logic import new_event
from store import Store
app=QApplication([]);logs=[];qInstallMessageHandler(lambda typ,ctx,msg:logs.append(msg))
def settle(ms=120):
 loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
with tempfile.TemporaryDirectory(prefix='calendar-nested-ui-') as temporary:
 target=Path(temporary);shutil.copytree(root/'qml',target/'qml')
 for name,marker in [('App.qml','id:win'),('CalendarEditor.qml','id: root')]:
  path=target/'qml'/name;path.write_text(path.read_text().replace(marker,marker+'\n function review(code){return eval(code);}',1))
 store=Store(target/'calendar.sqlite');day=dt.date(2026,10,28)
 school=new_event(day);school.update(id='school',title='School',time='07:00',minutes=420,category=1,groupId='school-day')
 exam=dict(school,id='exam',title='Math exam',time='09:00',minutes=60,category=2)
 store.merge([school,exam],[]);bridge=Bridge(store,True);bridge.selectDate(day.isoformat());bridge.setView('week')
 engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('planner',bridge);engine.load(QUrl.fromLocalFile(str(target/'qml/App.qml')))
 assert engine.rootObjects(),logs
 win=engine.rootObjects()[0];win.setWidth(1120);win.setHeight(860);win.requestActivate()
 def evaluate(code):
  expression=QQmlExpression(engine.rootContext(),win,'review('+json.dumps(code)+')');result=expression.evaluate();assert not expression.hasError(),expression.error().toString();return result[0]
 def block(ident):return 'weekEventRepeater.itemAt('+str(evaluate('planner.weekItems.filter(function(v){return !v.allDay;}).findIndex(function(v){return v.id==='+json.dumps(ident)+';})'))+')'
 def point(ident,x,y):
  item=block(ident);return QPoint(round(evaluate(item+f'.mapToItem(win.contentItem,{item}.width*{x},{item}.height*{y}).x')),round(evaluate(item+f'.mapToItem(win.contentItem,{item}.width*{x},{item}.height*{y}).y')))
 for theme in ['dark','light']:
  bridge.setTheme(theme);settle(250);evaluate('timeline.contentY=6.5*timeline.hourHeight');settle(60);parent=block('school');child=block('exam')
  assert evaluate(child+'.x>'+parent+'.x && '+child+'.x+'+child+'.width<'+parent+'.x+'+parent+'.width')
  assert evaluate(child+'.y>'+parent+'.y && '+child+'.y+'+child+'.height<'+parent+'.y+'+parent+'.height')
  assert evaluate(child+'.z>'+parent+'.z')
  assert all(not row['conflict'] and row['lanes']==1 for row in bridge.weekItems)
  QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-nested-'+theme+'.png')
  QTest.mouseDClick(win,Qt.LeftButton,Qt.NoModifier,point('exam',.6,.5));settle(240)
  assert evaluate('editorSurface.review("editor.visible && editor.eventId===\\"exam\\"")')
  evaluate('editorSurface.review("editor.close()")');settle(220)
  QTest.mouseDClick(win,Qt.LeftButton,Qt.NoModifier,point('school',.5,.04));settle(240)
  assert evaluate('editorSurface.review("editor.visible && editor.eventId===\\"school\\"")')
  evaluate('editorSurface.review("editor.close()")');settle(220)
 # Regression: a child starting 30 minutes later must not cover the parent header.
 screenshot_parent=dict(school,time='09:00',minutes=220,title='Long parent title that should stay readable')
 screenshot_child=dict(exam,time='09:30')
 bridge.commit([screenshot_parent,screenshot_child]);settle(200)
 for theme in ['dark','light']:
  bridge.setTheme(theme);settle(180);evaluate('timeline.contentY=8.5*timeline.hourHeight');settle(60)
  parent=block('school');child=block('exam')
  assert evaluate(child+'.y>='+parent+'.y+40')
  assert evaluate(child+'.y+'+child+'.height<'+parent+'.y+'+parent+'.height')
  QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-nested-header-'+theme+'.png')
 # Actual held-pointer reschedules must ignore the nested card's header offset.
 for time,vertical_steps,day_shift,expected in [('09:30',0,1,'09:30'),('09:30',1,1,'09:45'),('09:30',-1,1,'09:15'),('09:37',0,1,'09:37'),('09:30',1,0,'09:45')]:
  bridge.commit([dict(school,time='09:00',minutes=220),dict(exam,time=time)]);settle(180)
  evaluate('timeline.contentY=8.5*timeline.hourHeight');settle(60)
  start=point('exam',.5,.5);dx=evaluate('timeline.columnWidth')*day_shift;dy=evaluate('timeline.hourHeight')/4*vertical_steps
  QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,start);settle(25)
  for step in range(1,13):
   QTest.mouseMove(win,QPoint(round(start.x()+dx*step/12),round(start.y()+dy*step/12)));settle(15)
  QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,QPoint(round(start.x()+dx),round(start.y()+dy)));settle(220)
  saved=next(e for e in store.read() if e['id']=='exam')
  assert saved['time']==expected,(time,vertical_steps,day_shift,saved)
  assert saved['date']==(day+dt.timedelta(days=day_shift)).isoformat(),saved
 external=dict(exam,id='external',title='Independent appointment');external.pop('groupId')
 bridge.commit([school,exam,external]);settle(250)
 assert all(row['conflict'] for row in bridge.weekItems)
 assert next(row for row in bridge.weekItems if row['id']=='school')['lanes']==2
 bridge.reload_timer.stop();bridge.reminder_timer.stop();win.close();engine.deleteLater();settle()
 assert not logs,logs
print('Nested School/Exam geometry, independent edit targets, both themes, external conflict and offset-safe pointer rescheduling passed.')
