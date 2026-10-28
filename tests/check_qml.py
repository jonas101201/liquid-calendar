import os,sys,pathlib,tempfile,json,shutil,datetime as dt
os.environ.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_QUICK_CONTROLS_STYLE='Basic',LANG='de_DE.UTF-8')
src=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(src))
from app import Bridge
from store import Store
from logic import *
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine,QQmlExpression
from PySide6.QtCore import QUrl,QTimer,QEventLoop,qInstallMessageHandler,QLocale
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt,QPoint
QLocale.setDefault(QLocale('en_GB'));app=QApplication([]);logs=[];qInstallMessageHandler(lambda typ,ctx,text:logs.append(text))
temp=tempfile.TemporaryDirectory(prefix='reviewer-language-');p=pathlib.Path(temp.name);shutil.copytree(src/'qml',p/'qml')
s=(p/'qml/App.qml').read_text().replace('id:win','id:win\n function review(code){return eval(code);}',1);(p/'qml/App.qml').write_text(s)
s=(p/'qml/CalendarEditor.qml').read_text().replace('id: root','id: root\n function review(code){return eval(code);}',1);(p/'qml/CalendarEditor.qml').write_text(s)
for name in ['DatePicker.qml','TimePicker.qml']:
 file=p/'qml'/name;file.write_text(file.read_text().replace('id:picker','id:picker\n function review(code){return eval(code);}',1))
st=Store(p/'data.sqlite');b=Bridge(st,True);today=dt.date(2026,10,28)
def e(ident,n=0,**kw):
 v=dict(id=ident,title='Besprechung mit Müller',date=(today+dt.timedelta(days=n)).isoformat(),time='09:00',minutes=60,task=False,done=False,allDay=False,repeat='none',until='',category=2,location='Büro Köln',notes='Grüße – Vorbereitung 日本語',reminder=10);v.update(kw);return v
fixtures=[e('today'),e('tomorrow',1),e('after',2),e('november',10),e('undated',task=True,date='',time='',reminder=-1)]
st.merge(fixtures,[]);b.reload();b.selectDate(today.isoformat());before=st.read()
assert date_hints('tomorrow',today)[0]['label']=='Tomorrow'
assert {v['id'] for v in search(fixtures,'tomorrow',today)}=={'tomorrow'}
assert {v['id'] for v in search(fixtures,'day after tomorrow',today)}=={'after'}
assert {v['id'] for v in search(fixtures,'morgen',today)}=={'tomorrow'}
assert date_hints('monday',today)[0]['label']=='Monday'
assert date_hints('nov',today)[0]['label']=='November'
assert date_hints('mär',today)[0]['label']=='March'
assert {v['id'] for v in search(fixtures,'nov',today)}=={'november'}
assert {v['id'] for v in search(fixtures,'Thursday',today)}=={'tomorrow'}
assert {v['id'] for v in search(fixtures,'Müller',today)}=={e['id'] for e in fixtures}
engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('planner',b);engine.load(QUrl.fromLocalFile(str(p/'qml/App.qml')));assert engine.rootObjects(),logs
win=engine.rootObjects()[0]
def settle():
 loop=QEventLoop();QTimer.singleShot(180,loop.quit);loop.exec()
def expr(code):
 x=QQmlExpression(engine.rootContext(),win,'review('+json.dumps(code)+')');v=x.evaluate();assert not x.hasError(),x.error().toString();return v[0]
win.setWidth(980);win.setHeight(680)
out=p/'screenshots';out.mkdir(exist_ok=True)
for theme in ['dark','light']:
 b.setTheme(theme)
 for view in ['today','week','agenda','month','tasks','search','settings']:
  b.setView(view);settle();QQuickWindow.grabWindow(win).save(str(out/f'{theme}-{view}.png'))
assert expr('editorSurface.review('+json.dumps('root.dateText(Cal.parse("2026-10-28"),"dddd, dd. MMMM")')+')')=='Wednesday, 28. October'
b.edit('today',today.isoformat(),False);settle()
assert expr('editorSurface.review("titleField.text")')=='Besprechung mit Müller'
assert expr('editorSurface.review("locationField.text")')=='Büro Köln'
expr('editorSurface.review("saveButton.clicked()")');assert st.read()==before
# Actual Qt-slot and calendar restore paths use only isolated synthetic data.
source=e('series',repeat='weekly',task=True)
b.commit([source]);b.selectDate(source['date']);b.setView('month');settle()
expr('editorSurface.review('+json.dumps('toggleTask(events.filter(function(e){return e.id==="series";})[0],"2026-10-28")')+')');settle()
parent=next(e for e in st.read() if e['id']=='series');assert not parent['done'];assert occurs(parent,parse('2026-11-04'));assert len(st.read())==2
b.undo();assert st.read()==[source]
b.move('series','2026-11-04','2026-11-05',600,fingerprint(source));before_group=st.read();assert len(before_group)==2
b.edit('series',source['date'],False);settle()
expr('editorSurface.review("deleteConfirm.accept()")');settle();assert st.read()==[]
# This fallback is hidden in the native app; verify it without claiming a visible click.
assert expr('editorSurface.review("deletedEntry!==null&&!root.persistence")') is False
expr('editorSurface.review("undoDelete()")');settle();assert sorted(st.read(),key=lambda e:e['id'])==sorted(before_group,key=lambda e:e['id'])
# The user-visible application-wide Undo must also restore the whole group.
b.edit('series',source['date'],False);settle();expr('editorSurface.review("deleteConfirm.accept()")');settle();b.undo();assert sorted(st.read(),key=lambda e:e['id'])==sorted(before_group,key=lambda e:e['id'])
# Exercise actual 0.2 editor fields and Save; no personal data is touched.
b.commit([]);b.setView('tasks');settle()
expr('editorSurface.openNewTask(win.dateValue(planner.selected))');settle()
expr('editorSurface.review('+json.dumps('titleField.text="Prepare release";priorityBox.currentIndex=3;projectField.text="Launch";editor.checklist=[{id:"verify",title:"Verify package",done:false}];saveButton.clicked()')+')');settle()
saved=st.read()[0];assert saved['date']=='' and saved['priority']==3 and saved['project']=='Launch';assert len(saved['checklist'])==1
b.setTaskFilters('Launch',3);assert len(b.results)==1
expr('resultList.itemAtIndex(0).setChecklistExpanded(true)');settle()
expr('resultList.itemAtIndex(0).toggleStep("verify")');settle();assert st.read()[0]['checklist'][0]['done']
assert expr('resultList.itemAtIndex(0).checklistExpanded') is True
b.undo();assert st.read()==[saved]
for theme in ['dark','light']:
 b.setTheme(theme)
 for width,height in [(980,680),(1280,860)]:
  win.setWidth(width);win.setHeight(height);settle()
  QQuickWindow.grabWindow(win).save(str(out/f'{theme}-tasks-{width}.png'))
b.edit(saved['id'],'',False);settle()
assert expr('editorSurface.review("priorityBox.currentIndex")')==3
assert expr('editorSurface.review("projectField.text")')=='Launch'
# Invalid blank steps must block Save, then a valid edit is persisted.
expr('editorSurface.review('+json.dumps('editor.checklist=[{id:"verify",title:"",done:false}];saveButton.clicked()')+')');assert st.read()==[saved]
expr('editorSurface.review('+json.dumps('editor.checklist=[{id:"verify",title:"Verify package",done:true}];saveButton.clicked()')+')');settle()
assert st.read()[0]['checklist'][0]['done']
b.undo();assert st.read()==[saved]
# Reproduce actual typing into delegate fields, rather than assigning the draft.
b.edit(saved['id'],'',False);settle()
expr('editorSurface.review("addChecklistStep.clicked()")');settle()
expr('editorSurface.review("checklistRows.itemAt(1).children[1].forceActiveFocus()")');settle()
for char in 'second step':QTest.keyClick(win,Qt.Key(ord(char.upper())))
settle()
assert expr('editorSurface.review("checklistRows.itemAt(1).children[1].text")')=='second step'
assert expr('editorSurface.review("editor.checklist[1].title")')=='second step', 'Typed checklist text did not reach saved draft'
# Adding another row must retain earlier input; toggling checks must use the draft too.
expr('editorSurface.review("addChecklistStep.clicked()")');settle()
assert expr('editorSurface.review("checklistRows.itemAt(1).children[1].text")')=='second step'
expr('editorSurface.review("checklistRows.itemAt(1).children[0].toggle();checklistRows.itemAt(1).children[0].clicked()")');settle()
assert expr('editorSurface.review("editor.checklist[1].done")') is True
expr('editorSurface.review("checklistRows.itemAt(2).children[2].clicked()")');settle()
expr('editorSurface.review("saveButton.clicked()")');settle()
assert len(st.read()[0]['checklist'])==2
assert st.read()[0]['checklist'][1]['title']=='second step'
assert st.read()[0]['checklist'][1]['done'] is True
b.edit(st.read()[0]['id'],'',False);settle()
assert expr('editorSurface.review("checklistRows.itemAt(1).children[1].text")')=='second step'
expr('editorSurface.review("editor.close()")')
# Valid imported astral Unicode must survive opening and saving without truncation.
unicode_entry=e('unicode',task=True,date='',time='',reminder=-1,title='🚀'*200,location='🚀'*500,project='🚀'*80,checklist=[dict(id='emoji',title='🚀'*200,done=False)])
b.commit([unicode_entry]);b.edit('unicode','',False);settle()
assert expr('editorSurface.review("titleField.text")')==unicode_entry['title']
assert expr('editorSurface.review("locationField.text")')==unicode_entry['location']
assert expr('editorSurface.review("projectField.text")')==unicode_entry['project']
assert expr('editorSurface.review("checklistRows.itemAt(0).children[1].text")')==unicode_entry['checklist'][0]['title']
expr('editorSurface.review("saveButton.clicked()")');settle();assert st.read()==[unicode_entry]
# Expansion survives a model refresh and detachment of a recurring occurrence.
check_series=e('check-series',task=True,date='2032-01-05',repeat='weekly',checklist=[dict(id='step',title='Check',done=False)])
b.commit([check_series]);b.setView('tasks');b.setTaskFilters('*',-1);b.setFilter('tasks',-1);settle()
expr('resultList.itemAtIndex(0).setChecklistExpanded(true)');expr('resultList.itemAtIndex(0).toggleStep("step")');settle()
assert st.read()!=[check_series]
assert expr('resultList.itemAtIndex(0).checklistExpanded') is True
# Creation milestone: preview -> editor -> pickers -> template -> actual Save.
b.commit([]);settle();expr('toolsButton.clicked()');settle()
point=QPoint(round(expr('quickAddAction.mapToItem(win.contentItem,quickAddAction.width/2,quickAddAction.height/2).x')),round(expr('quickAddAction.mapToItem(win.contentItem,quickAddAction.width/2,quickAddAction.height/2).y')))
QTest.mouseClick(win,Qt.LeftButton,Qt.NoModifier,point);settle()
assert expr('quickPopup.visible') is True
assert expr('quickInput.activeFocus') is True
expr('quickInput.text="tomorrow 15:00 Dentist for 45m";quickPopup.refresh()');settle()
assert st.read()==[]
assert expr('quickPopup.preview.event.time')=='15:00'
expr('quickPopup.review()');settle()
assert expr('editorSurface.review("titleField.text")')=='Dentist'
assert expr('editorSurface.review("editor.eventId")')==''
expr('editorSurface.review('+json.dumps('datePicker.openFor("2032-02-29");datePicker.shift(1);datePicker.choose("2032-03-15")')+')');settle()
assert expr('editorSurface.review("dateField.text")')=='2032-03-15'
expr('editorSurface.review('+json.dumps('datePicker.openFor(dateField.text);datePicker.review("yearChoice.contentItem.forceActiveFocus();yearChoice.contentItem.selectAll()")')+')');settle()
for char in '2034':QTest.keyClick(win,Qt.Key(ord(char)))
QTest.keyClick(win,Qt.Key_Tab);settle()
assert expr('editorSurface.review('+json.dumps('datePicker.monthDate.getFullYear()')+')')==2034
expr('editorSurface.review("datePicker.close()")')

expr('editorSurface.review('+json.dumps('timePicker.openFor("23:55");timePicker.choose()')+')');settle()
assert expr('editorSurface.review("timeField.text")')=='23:55'
expr('editorSurface.review("editorToolsButton.clicked();templateButton.triggered();editorActions.close()")');settle()
expr('editorSurface.review('+json.dumps('templateNameField.text="Dentist visit";saveTemplateButton.clicked()')+')');settle()
assert len(b.templates)==1 and st.read()==[]
expr('editorSurface.review("saveButton.clicked()")');settle()
assert len(st.read())==1 and st.read()[0]['time']=='23:55'
original=st.read()[0];b.selectDate('2033-01-05');expr('templateLibrary.open()');settle()
expr('templateList.itemAtIndex(0).children[1].clicked()');settle()
assert expr('editorSurface.review("dateField.text")')=='2033-01-05'
assert expr('editorSurface.review("editor.eventId")')==''
expr('editorSurface.review("saveButton.clicked()")');settle()
assert len(st.read())==2 and original in st.read()
# Opening and cancelling creation/library controls never inserts events.
expr('templateLibrary.open()');settle();expr('templateLibrary.close()');expr('win.openQuick()');settle();expr('quickPopup.close()')
assert len(st.read())==2
expr('templateLibrary.open()');settle();expr('templateList.itemAtIndex(0).children[2].clicked()');settle()
expr('templateRename.text="Renamed visit";renameTemplateButton.clicked()');settle();assert b.templates[0]['name']=='Renamed visit'
expr('templateList.itemAtIndex(0).children[2].clicked()');settle();expr('deleteTemplateButton.clicked()');settle()
assert b.templates==[] and len(st.read())==2
expr('templateLibrary.close()')
# Actual weekly weekday controls, save/reopen, last-day guard and rule removal.
b.commit([]);expr('editorSurface.openEvent(null,win.dateValue("2026-10-27"))');settle()
expr('editorSurface.review('+json.dumps('titleField.text="Weekly lesson";dateField.text="2026-10-27";repeatBox.currentIndex=2;editor.detailsExpanded=true')+')');settle()
assert expr('editorSurface.review("repeatDays.itemAt(1).highlighted")') is True
expr('editorSurface.review("repeatDays.itemAt(0).clicked();repeatDays.itemAt(1).clicked();repeatDays.itemAt(2).clicked();repeatDays.itemAt(4).clicked();saveButton.clicked()")');settle()
weekly_entry=st.read()[0];assert weekly_entry['weekdays']==[0,2,4]
b.edit(weekly_entry['id'],'2026-10-28',False);settle()
assert expr('editorSurface.review("JSON.stringify(editor.weeklyDays())")')=='[0,2,4]'
expr('editorSurface.review("repeatDays.itemAt(0).clicked();repeatDays.itemAt(2).clicked();repeatDays.itemAt(4).clicked()")')
assert expr('editorSurface.review("JSON.stringify(editor.weeklyDays())")')=='[4]'
assert expr('editorSurface.review("editor.validation")')=='Choose at least one weekday.'
expr('editorSurface.review("repeatBox.currentIndex=0;saveButton.clicked()")');settle()
assert 'weekdays' not in st.read()[0]
print('Weekly day buttons, legacy default, save/reopen and last-day guard passed.')
print('0.3 quick preview, event/time pickers, template save/use and new IDs passed.')
print('0.2 task editor Save/reopen/validation, project filters and checklist Undo passed.')
print('Recurring task Qt slot, hidden calendar fallback and visible app-wide group Undo passed.')
print('English dates/search; German aliases; non-ASCII data preserved; 14 small-window views rendered.')
# Real merge dialog preview, save, conflict rejection and Undo on synthetic records.
a=e('merge-a',title='Design review',notes='First note');c=e('merge-b',title='Planning',time='09:30',notes='Second note')
b.commit([a,c]);b.edit(a['id'],a['date'],False);settle()
expr('editorSurface.review("mergeButton.triggered()")');settle()
assert expr('editorSurface.review("mergeDialog.visible")') is True
assert expr('editorSurface.review("mergeDialog.preview.event.minutes")')==90
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-merge-preview.png')
expr('editorSurface.review("confirmMerge.clicked()")');settle()
assert len(st.read())==1 and st.read()[0]['notes']=='First note\n\nSecond note'
b.undo();assert sorted(st.read(),key=lambda e:e['id'])==[a,c]
# Dense lanes, short neighboring entries and horizontally aligned week headings.
dense=[e('parallel-'+str(n),title='Parallel event '+str(n)) for n in range(5)]
dense.extend([e('short-a',time='11:00',minutes=5),e('short-b',time='11:05',minutes=5)])
b.commit(dense);b.selectDate(a['date']);b.setView('week');win.setWidth(980);win.setHeight(680);settle()
assert expr('timeline.contentWidth>timeline.width')
assert expr('timeline.contentX>0 && timeline.contentX<=timeline.gutter+2.5*timeline.columnWidth && timeline.contentX+timeline.width>=timeline.gutter+2.5*timeline.columnWidth')
expr('timeline.contentX=300');settle()
assert expr('weekHeader.x===timeline.gutter-timeline.contentX')
expr('timeline.contentX=timeline.gutter+2*timeline.columnWidth;timeline.contentY=8*timeline.hourHeight');settle()
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-overlap-preview.png')
print('Merge dialog preview/save/Undo and dense week layout with aligned scrolling passed.')
# Reproduce screenshot: a selected recurring occurrence must expose Merge.
series_a=e('weekly-merge',repeat='weekly',weekdays=[2,4]);series_b=e('daily-merge',repeat='daily',title='Daily planning',time='09:30')
b.commit([series_a,series_b]);b.edit(series_a['id'],series_a['date'],True);settle()
expr('editorSurface.review("editorToolsButton.clicked()")');settle()
assert expr('editorSurface.review("mergeButton.visible")') is True
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-occurrence-menu-fixed.png')
expr('editorSurface.review("mergeButton.triggered();editorActions.close()")');settle()
assert expr('editorSurface.review("mergeDialog.choices.length")')==1
assert expr('editorSurface.review("mergeDialog.preview.event.minutes")')==90
expr('editorSurface.review("confirmMerge.clicked()")');settle()
assert len(st.read())==3
for source in (series_a,series_b):
 parent=next(e for e in st.read() if e['id']==source['id'])
 assert not occurs(parent,parse(source['date'])) and occurs(parent,parse('2026-11-04'))
b.undo();assert sorted(st.read(),key=lambda e:e['id'])==sorted([series_a,series_b],key=lambda e:e['id'])
expr('editorSurface.openEvent(null,win.dateValue("2026-10-28"))');settle()
expr('editorSurface.review("editorToolsButton.clicked()")');settle()
assert expr('editorSurface.review("duplicateButton.height")')==0
assert expr('editorSurface.review("mergeButton.height")')==0
assert expr('editorSurface.review("templateButton.y")')==0
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-hidden-menu-fixed.png')
expr('editorSurface.review("editorActions.close();editor.close()")');settle()
print('Selected occurrences merge without changing future repeats; hidden menu rows take zero space.')
win.close();engine.deleteLater();settle();assert not logs,logs
