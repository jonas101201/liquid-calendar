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
from PySide6.QtCore import Qt
QLocale.setDefault(QLocale('en_GB'));app=QApplication([]);logs=[];qInstallMessageHandler(lambda typ,ctx,text:logs.append(text))
temp=tempfile.TemporaryDirectory(prefix='reviewer-language-');p=pathlib.Path(temp.name);shutil.copytree(src/'qml',p/'qml')
s=(p/'qml/App.qml').read_text().replace('id:win','id:win\n function review(code){return eval(code);}',1);(p/'qml/App.qml').write_text(s)
s=(p/'qml/CalendarEditor.qml').read_text().replace('id: root','id: root\n function review(code){return eval(code);}',1);(p/'qml/CalendarEditor.qml').write_text(s)
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
expr('resultList.itemAtIndex(0).checklistExpanded=true');settle()
expr('resultList.itemAtIndex(0).toggleStep("verify")');settle();assert st.read()[0]['checklist'][0]['done']
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
print('0.2 task editor Save/reopen/validation, project filters and checklist Undo passed.')
print('Recurring task Qt slot, hidden calendar fallback and visible app-wide group Undo passed.')
print('English dates/search; German aliases; non-ASCII data preserved; 14 small-window views rendered.')
win.close();engine.deleteLater();settle();assert not logs,logs
