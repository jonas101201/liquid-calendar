import os,sys,pathlib,tempfile,json,shutil,datetime as dt
os.environ.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_QUICK_CONTROLS_STYLE='Basic',LANG='de_DE.UTF-8')
src=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(src))
from app import Bridge
from store import Store
from logic import *
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine,QQmlExpression
from PySide6.QtCore import QUrl,QTimer,QEventLoop,qInstallMessageHandler,QLocale
from PySide6.QtQuick import QQuickWindow,QQuickItem
from PySide6.QtGui import QPalette,QColor
from unittest.mock import patch
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt,QPoint,QPointF
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
def settle(ms=180):
 loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
def expr(code):
 x=QQmlExpression(engine.rootContext(),win,'review('+json.dumps(code)+')');v=x.evaluate();assert not x.hasError(),x.error().toString();return v[0]
win.setWidth(980);win.setHeight(680)
out=p/'screenshots';out.mkdir(exist_ok=True)
settle(80)
assert expr('navigationRail.selectedItem===navigationItems.itemAt(0) && navigationHighlight.visible')
assert expr('!dayList.ScrollBar.vertical.visible')
# Desktop shortcuts have one owner, including while Calendar's month is visible.
b.setView('month');win.requestActivate();settle(300)
QTest.keyClick(win,Qt.Key_N,Qt.ControlModifier);settle(260)
assert expr('editorSurface.review("editor.visible")')
expr('editorSurface.review("editor.close()")');settle(160)
QTest.keyClick(win,Qt.Key_F,Qt.ControlModifier);settle(300);assert b.view=='search'
QTest.keyClick(win,Qt.Key_L,Qt.ControlModifier);settle(260);assert expr('datePopup.visible')
QTest.keyClick(win,Qt.Key_N,Qt.ControlModifier);settle(40)
assert expr('!editorSurface.review("editor.visible")')
expr('datePopup.close()');settle(160)
# Appearance controls are reachable and update both shell and calendar.
b.setView('settings');settle(300)
assert expr('Math.abs(settingsVerticalScroll.x+settingsVerticalScroll.width-settingsScroll.width)<1')
# A failed theme write must restore the actual checked choice, not imply it saved.
b.setTheme('dark');win.requestActivate();settle(160)
light_point=QPoint(round(expr('lightThemeChoice.mapToItem(win.contentItem,lightThemeChoice.width/2,lightThemeChoice.height/2).x')),round(expr('lightThemeChoice.mapToItem(win.contentItem,0,lightThemeChoice.height/2).y')))
with patch.object(st,'set_settings',side_effect=OSError('synthetic failed theme save')):
 QTest.mouseClick(win,Qt.LeftButton,Qt.NoModifier,light_point);settle(120)
assert b.theme=='dark' and expr('darkThemeChoice.checked && !lightThemeChoice.checked')
b.clearError();settle(40)
# Opacity is a lightweight preview while held; persist once on release, without rebuilding calendar models.
expr('settingsScroll.contentItem.contentY=Math.max(0,Math.min(settingsScroll.contentItem.contentHeight-settingsScroll.height,settingsScroll.contentItem.contentY+appearanceOpacity.mapToItem(settingsScroll,0,0).y-settingsScroll.height/2))');settle(80)
def opacity_point(x):
 return QPoint(round(expr(f'appearanceOpacity.mapToItem(win.contentItem,appearanceOpacity.width*{x},appearanceOpacity.height/2).x')),round(expr('appearanceOpacity.mapToItem(win.contentItem,0,appearanceOpacity.height/2).y')))
calendar_refreshes=[]
def count_refresh():calendar_refreshes.append(True)
b.changed.connect(count_refresh)
with patch.object(st,'set_settings',wraps=st.set_settings) as writes:
 QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,opacity_point(.1))
 for step in range(1,61):
  QTest.mouseMove(win,opacity_point(.1+.8*step/60));settle(2)
 assert expr('appearanceOpacity.pressed && win.surfaceOpacity>.85')
 assert writes.call_count==0 and calendar_refreshes==[]
 QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,opacity_point(.9));settle(250)
 assert writes.call_count==1 and calendar_refreshes==[]
 assert abs(b.glassOpacity-expr('win.surfaceOpacity'))<.001
 writes.reset_mock()
 for _ in range(4):QTest.keyClick(win,Qt.Key_Left);settle(15)
 assert writes.call_count==0
 settle(250);assert writes.call_count==1 and calendar_refreshes==[]
b.changed.disconnect(count_refresh)
expr('settingsScroll.contentItem.contentY=0');settle(30)
print('Opacity drag has zero writes/model refreshes while held, one release write and debounced keyboard persistence.')
expr('appearanceChoices.itemAt(2).clicked()');settle(200)
assert st.settings()['accent']=='#72ebce'
assert expr('String(editorSurface.accent)')=='#72ebce'
expr('appearanceOpacity.value=.84;appearanceOpacity.moved()');settle(250)
assert abs(st.settings()['glassOpacity']-.84)<.001
assert expr('win.surfaceOpacity')==.84
# Each design is selectable, persistent, and represented by the matching preview.
expr('darkThemeChoice.clicked()');settle(200)
assert b.theme=='dark' and expr('darkThemeChoice.checked && !lightThemeChoice.checked && !win.light')
expr('lightThemeChoice.clicked()');settle(200)
assert st.settings()['theme']=='light' and expr('win.light && lightThemeChoice.previewLight')
assert expr('appearanceOpacity.from===.72')
expr('systemThemeChoice.clicked()');settle(200)
assert b.theme=='auto' and expr('systemThemeChoice.checked && win.light===win.systemLight')
original_palette=app.palette();test_palette=QPalette(original_palette)
test_palette.setColor(QPalette.Window,QColor('#081d31'));app.setPalette(test_palette);settle(200)
assert expr('!win.light && !systemThemeChoice.previewLight')
test_palette.setColor(QPalette.Window,QColor('#70e0ee'));app.setPalette(test_palette);settle(200)
assert expr('win.light && systemThemeChoice.previewLight')
b.setTheme('dark');settle(200);assert expr('!win.light')
app.setPalette(original_palette);b.setTheme('dark')
# Filter menus and their checked states follow the active theme and accent.
b.setView('tasks');settle(300);expr('sortMenu.open()');settle(180)
assert expr('sortMenu.light===win.light && String(sortMenu.accent)===String(win.accent)')
expr('sortMenu.itemAt(2).triggered();sortMenu.close()');settle(160)
assert b.taskOrder=='project' and expr('sortMenu.itemAt(2).checked')
b.setTaskOrder('default')
b.setAppearance('#7ceafa',.60);b.setView('today');settle(300)
print('Dark/light/system choices, live desktop palette changes and themed sort menus passed.')
# Each accent recolors the entire palette and calendar glass in both themes.
def luminance(color):
 values=[color.redF(),color.greenF(),color.blueF()]
 return sum(weight*(value/12.92 if value<=.04045 else ((value+.055)/1.055)**2.4) for weight,value in zip([.2126,.7152,.0722],values))
for theme in ['dark','light']:
 b.setTheme(theme);settle(100)
 previous=None
 for accent in ['#7ceafa','#8cbcff','#72ebce','#c2adff','#ffa8cf']:
  b.setAppearance(accent,.60);settle(170)
  panel=expr('win.panel');ink=expr('win.ink');muted=expr('win.muted')
  assert panel!=previous;previous=panel
  assert expr('Math.abs(win.panel.hslHue-win.tint.hslHue)<.01')
  assert expr('editorSurface.review("String(calendarGlass.tint)")')==accent
  assert expr('String(quickPopup.background.tint)')==accent
  for text in [ink,muted]:
   values=sorted([luminance(text),luminance(panel)])
   assert (values[1]+.05)/(values[0]+.05)>=4.5
b.setAppearance('#7ceafa',.60);b.setTheme('dark');settle(180)
print('All five accents recolor surfaces and popup glass in both themes with readable text contrast.')
# Closing during the enter transition must continue from the visible frame.
expr('win.openQuick()');settle(25)
before_opacity=expr('quickPopup.opacity');before_scale=expr('quickPopup.scale')
expr('quickPopup.close()');settle(1)
assert expr('quickPopup.opacity')<=before_opacity+.03
assert expr('quickPopup.scale')<=before_scale+.003
settle(160)
print('Native shortcut ownership, appearance controls and interrupted popup close passed.')
for theme in ['dark','light']:
 b.setTheme(theme)
 for view in ['today','week','agenda','month','tasks','search','settings']:
  b.setView(view);settle();QQuickWindow.grabWindow(win).save(str(out/f'{theme}-{view}.png'))
# Calendar owns both presentations and remembers the last one across navigation.
assert expr('navigationItems.count')==5
assert expr('navigationItems.model.some(function(item){return item.id==="week";})') is False
b.selectDate('2026-10-28');b.setView('month');settle()
expr('calendarWeekButton.clicked()');settle();assert b.view=='week'
assert expr('navigationItems.itemAt(1).primary') is True
b.setView('tasks');expr('navigationItems.itemAt(1).clicked()');settle();assert b.view=='week'
expr('calendarMonthButton.clicked()');settle();assert b.view=='month'
assert expr('editorSurface.mode')==0
expr('editorSurface.navigate(1)');settle();assert b.selected=='2026-11-01'
expr('editorSurface.navigate(-1)');settle();assert b.selected=='2026-10-01'
expr('calendarWeekButton.clicked()');b.navigate(1);settle();assert b.selected=='2026-10-08'
b.selectDate(today.isoformat());b.setView('month');settle()
print('Consolidated Calendar navigation and month/week switching passed.')
# Saving an undated task must not leak the standalone task filter into Calendar.
b.setView('tasks');expr('editorSurface.openNewTask(win.dateValue(planner.selected))');settle(220)
expr('editorSurface.review('+json.dumps('titleField.text="Undated filter regression";saveButton.clicked()')+')');settle(220)
b.setView('month');settle(300)
assert expr('!editorSurface.globalMode && editorSurface.kindFilter===0')
expr('editorSurface.review('+json.dumps('searchInput.text="no matching title"')+')');settle(40)
assert expr('editorSurface.globalMode && !previousPeriod.enabled && !nextPeriod.enabled')
expr('todayAction.clicked()');settle(220)
assert b.selected==dt.date.today().isoformat() and expr('!editorSurface.globalMode && editorSurface.query===""')
expr('editorSurface.review('+json.dumps('searchInput.text="still no matching title"')+')')
expr('jumpDate.text="2026-11-15";datePopup.go()');settle(220)
assert b.selected=='2026-11-15' and expr('!editorSurface.globalMode && previousPeriod.enabled && nextPeriod.enabled')
previous_selected=b.selected
expr('datePopup.open()');settle(260)
expr('jumpDate.text="1.1.0001";datePopup.go()');settle(40)
assert b.selected==previous_selected and expr('datePopup.visible && datePopup.validation.length>0')
expr('datePopup.close()');settle(160)
b.undo();assert st.read()==before
b.selectDate(today.isoformat());b.setView('month');settle(280)
print('Undated task routing, month filter isolation and Today/date navigation recovery passed.')
# Drag the selected calendar pill, rather than a scrollbar, while the left button is held.
def calendar_point(name):
 return QPoint(round(expr(f'{name}.mapToItem(win.contentItem,{name}.width/2,{name}.height/2).x')),round(expr(f'{name}.mapToItem(win.contentItem,0,{name}.height/2).y')))
for motion in [True,False]:
 b.setAnimations(motion);b.setView('month');settle(280)
 start=calendar_point('calendarMonthButton');end=calendar_point('calendarWeekButton')
 QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,start);QTest.mouseMove(win,QPoint(end.x()+35,end.y()));settle(30)
 assert expr('calendarModePointer.pressed && calendarModePointer.dragging && calendarModeHighlight.x===calendarModeSwitch.lastX')
 assert b.view=='month'
 QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,QPoint(end.x()+35,end.y()));settle(280);assert b.view=='week'
 QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,end);QTest.mouseMove(win,QPoint(start.x()-35,start.y()));settle(30)
 assert expr('calendarModeHighlight.x===calendarModeSwitch.firstX')
 QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,QPoint(start.x()-35,start.y()));settle(280);assert b.view=='month'
 QTest.mouseClick(win,Qt.LeftButton,Qt.NoModifier,end);settle(280);assert b.view=='week'
 expr('calendarMonthButton.forceActiveFocus()');QTest.keyClick(win,Qt.Key_Space);settle(280);assert b.view=='month'
 QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,start);QTest.mouseMove(win,end);settle(30)
 b.setView('tasks');settle(30)
 assert expr('!calendarModePointer.dragging') and b.view=='tasks'
 QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,end)
b.setAnimations(True);b.setView('month');settle(280)
print('Held Month/Week pill drag, bounds, click, keyboard and cancellation passed with and without motion.')
# Sample real animation frames, then interrupt them with reduced motion.
b.setAnimations(True);b.setView('today');settle(320)
b.setView('tasks');settle(60)
assert expr('viewArrival.running && workspace.opacity>.35 && workspace.opacity<1')
assert expr('navigationHighlight.y>0 && navigationHighlight.y<navigationRail.selectedItem.y')
settle(320)
assert expr('workspace.opacity===1 && workspaceShift.y===0 && navigationHighlight.y===navigationRail.selectedItem.y')
for view in ['month','week','tasks','today']:
 b.setView(view);settle(35)
b.setAnimations(False);settle(10)
assert expr('!viewArrival.running && workspace.opacity===1 && workspaceShift.y===0')
b.setView('search');settle(10)
assert expr('navigationHighlight.y===navigationRail.selectedItem.y')
expr('win.openQuick()');settle(10)
assert expr('quickPopup.opacity===1 && quickPopup.scale===1')
expr('quickPopup.close()');settle(10);assert expr('!quickPopup.visible')
b.setAnimations(True);expr('win.openQuick()');settle(55)
assert expr('quickPopup.opacity>0 && quickPopup.opacity<1 && quickPopup.scale<1')
expr('quickPopup.close()');settle(160)
expr('win.openQuick()');settle(260)
assert expr('quickPopup.opacity===1 && quickPopup.scale===1')
expr('quickPopup.close()');settle(160)
b.selectDate(today.isoformat());b.setView('month');settle(300)
print('Sliding selections, interrupted view transitions and popup/reduced-motion frames passed.')
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
assert expr('editorSurface.review("mergeDialog.preview.events[0].minutes")')==60
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-merge-preview.png')
expr('editorSurface.review("confirmMerge.clicked()")');settle()
assert len(st.read())==2 and next(e for e in st.read() if e['id']==a['id'])['notes']=='First note'
assert st.read()[0]['groupId']==st.read()[1]['groupId']
# Both cards remain visible and carry an identifiable link; unlink includes a draft.
b.setView('week');b.selectDate(a['date']);settle(240)
assert expr('!!linkedGroups[planner.events[0].groupId]')
assert expr('linkConnections.visible && linkConnections.records.length===2')
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-linked-week.png')
linked_snapshot=next(e for e in st.read() if e['id']==a['id'])
b.edit(a['id'],a['date'],True);settle(180)
expr('editorSurface.review('+json.dumps('titleField.text="Updated linked review";editorToolsButton.clicked()')+')');settle(180)
assert expr('editorSurface.review("unlinkButton.visible && !mergeButton.visible")')
expr('editorSurface.review("unlinkButton.triggered();editorActions.close()")');settle(200)
assert all('groupId' not in e for e in st.read())
assert next(e for e in st.read() if e['id']==a['id'])['title']=='Updated linked review'
b.undo();assert next(e for e in st.read() if e['id']==a['id'])==linked_snapshot
b.commit([a,c]);assert sorted(st.read(),key=lambda e:e['id'])==[a,c]
# Unsaved form changes enter the preview and commit together; Cancel writes nothing.
b.edit(a['id'],a['date'],False);settle(220)
expr('editorSurface.review('+json.dumps('titleField.text="Unsaved design";timeField.text="08:30";durationField.value=120;categoryBox.currentIndex=3;locationField.text="New studio";notesField.text="Unsaved note";root.openMerge()')+')');settle(220)
assert expr('editorSurface.review("mergeDialog.preview.events[0].title")')=='Unsaved design'
assert expr('editorSurface.review("mergeDialog.preview.events[0].minutes")')==120
assert expr('editorSurface.review("mergeDialog.preview.events[0].notes")')=='Unsaved note'
assert sorted(st.read(),key=lambda e:e['id'])==[a,c]
expr('editorSurface.review("mergeDialog.close()")');settle(160)
assert expr('editorSurface.review("titleField.text")')=='Unsaved design'
expr('editorSurface.review("root.openMerge()")');settle(220)
expr('editorSurface.review("confirmMerge.clicked()")');settle(220)
saved_by_id={e['id']:e for e in st.read()}
assert saved_by_id[a['id']]['title']=='Unsaved design' and saved_by_id[a['id']]['category']==3
assert saved_by_id[a['id']]['location']=='New studio'
assert saved_by_id[c['id']]['title']==c['title'] and saved_by_id[c['id']]['location']==c['location']
b.undo();assert sorted(st.read(),key=lambda e:e['id'])==[a,c]
# The edited date controls candidate selection and the destination after saving.
next_day=e('next-day',date='2026-10-29',title='Next day event')
b.commit([a,c,next_day]);b.edit(a['id'],a['date'],False);settle(220)
expr('editorSurface.review('+json.dumps('dateField.text="2026-10-29";root.openMerge()')+')');settle(220)
assert expr('editorSurface.review("mergeDialog.choices.length")')==1
expr('editorSurface.review("confirmMerge.clicked()")');settle(220)
assert b.selected=='2026-10-29'
b.undo();assert sorted(st.read(),key=lambda e:e['id'])==[a,c,next_day]
b.edit(a['id'],a['date'],False);settle(220)
expr('editorSurface.review('+json.dumps('titleField.text="";root.openMerge()')+')');settle(160)
assert expr('editorSurface.review("!mergeDialog.visible && editor.visible && editor.validation.length>0")')
assert sorted(st.read(),key=lambda e:e['id'])==[a,c,next_day]
expr('editorSurface.review("editor.close()")');settle(160)
print('Unsaved merge preview/commit/Cancel, edited-date candidates and invalid draft protection passed.')
# Dense lanes, short neighboring entries and horizontally aligned week headings.
dense=[e('parallel-'+str(n),title='Parallel event '+str(n)) for n in range(5)]
dense.extend([e('short-a',time='11:00',minutes=5),e('short-b',time='11:05',minutes=5)])
b.commit(dense);b.selectDate(a['date']);b.setView('week');win.setWidth(980);win.setHeight(680);settle()
assert expr('timeline.contentWidth>timeline.width')
assert expr('timeline.contentX>0 && timeline.contentX<=timeline.gutter+2.5*timeline.columnWidth && timeline.contentX+timeline.width>=timeline.gutter+2.5*timeline.columnWidth')
expr('timeline.contentX=300');settle()
assert expr('weekHeader.x===timeline.gutter-timeline.contentX')
assert expr('timeAxis.parent===timeline && timeAxis.x===0 && timeAxis.width===timeline.gutter')
assert expr('timeAxis.mapToItem(win.contentItem,0,0).x===timeline.mapToItem(win.contentItem,0,0).x')
expr('timeline.contentX=timeline.gutter+2*timeline.columnWidth;timeline.contentY=8*timeline.hourHeight');settle()
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-overlap-preview.png')
# Pressing the track and dragging must update the view before mouse release.
def scrollbar_point(name,x,y):
 return QPoint(round(expr(f'{name}.mapToItem(win.contentItem,{name}.width*{x},{name}.height*{y}).x')),round(expr(f'{name}.mapToItem(win.contentItem,{name}.width*{x},{name}.height*{y}).y')))
expr('timeline.contentX=0;timeline.contentY=0');settle()
point=scrollbar_point('weekHorizontalScroll',.8,.5)
QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,point);settle(30)
assert expr('weekHorizontalScroll.dragging && timeline.contentX>0')
pressed_x=expr('timeline.contentX')
QTest.mouseMove(win,scrollbar_point('weekHorizontalScroll',.25,.5));settle(30)
assert expr('weekHorizontalScroll.dragging') and expr('timeline.contentX')<pressed_x
QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,scrollbar_point('weekHorizontalScroll',.25,.5));settle(20)
assert expr('!weekHorizontalScroll.dragging')
point=scrollbar_point('weekVerticalScroll',.5,.8)
QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,point);settle(30)
assert expr('weekVerticalScroll.dragging && timeline.contentY>0')
pressed_y=expr('timeline.contentY')
QTest.mouseMove(win,scrollbar_point('weekVerticalScroll',.5,.25));settle(30)
assert expr('weekVerticalScroll.dragging') and expr('timeline.contentY')<pressed_y
QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,scrollbar_point('weekVerticalScroll',.5,.25));settle(20)
assert expr('!weekVerticalScroll.dragging')
# Keep thumb offset when it is grabbed, rather than jumping its centre to the pointer.
expr('timeline.contentX=0');settle(20)
point=QPoint(round(expr('weekHorizontalScroll.mapToItem(win.contentItem,weekHorizontalScroll.leftPadding+8,weekHorizontalScroll.height/2).x')),round(expr('weekHorizontalScroll.mapToItem(win.contentItem,0,weekHorizontalScroll.height/2).y')))
QTest.mousePress(win,Qt.LeftButton,Qt.NoModifier,point);settle(20)
assert expr('weekHorizontalScroll.dragging && timeline.contentX===0')
QTest.mouseMove(win,QPoint(point.x()+45,point.y()));settle(20)
assert expr('timeline.contentX>0')
QTest.mouseRelease(win,Qt.LeftButton,Qt.NoModifier,QPoint(point.x()+45,point.y()));settle(20)
QTest.keyClick(win,Qt.Key_End);settle(20)
assert expr('Math.abs(timeline.contentX-(timeline.contentWidth-timeline.width))<2')
QTest.keyClick(win,Qt.Key_Home);settle(20);assert expr('timeline.contentX===0')
print('Calendar scrollbars move on track press and held drag; thumb offset and keyboard endpoints passed.')
print('Merge dialog preview/save/Undo and dense week layout with aligned scrolling passed.')
# Reproduce screenshot: a selected recurring occurrence must expose Merge.
series_a=e('weekly-merge',repeat='weekly',weekdays=[2,4]);series_b=e('daily-merge',repeat='daily',title='Daily planning',time='09:30')
b.commit([series_a,series_b]);b.edit(series_a['id'],series_a['date'],True);settle()
expr('editorSurface.review("editorToolsButton.clicked()")');settle()
assert expr('editorSurface.review("mergeButton.visible")') is True
QQuickWindow.grabWindow(win).save('/tmp/liquid-calendar-occurrence-menu-fixed.png')
expr('editorSurface.review("mergeButton.triggered();editorActions.close()")');settle()
assert expr('editorSurface.review("mergeDialog.choices.length")')==1
assert expr('editorSurface.review("mergeDialog.preview.events[0].minutes")')==60
expr('editorSurface.review("confirmMerge.clicked()")');settle()
assert len(st.read())==4
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
# Actual month-card buttons must distinguish one occurrence from its whole series.
night=e('overnight',date='2026-10-28',time='23:30',minutes=120,repeat='weekly',task=True)
b.commit([night]);b.selectDate('2026-11-05');b.setView('month');expr('editorSurface.review('+json.dumps('searchInput.clear();kindBox.currentIndex=0;categoryFilter=-1')+')');settle(300)
assert expr('editorSurface.review("agenda.count")')==1
assert expr('editorSurface.review('+json.dumps('dayCount(Cal.parse("2026-10-29"))')+')')==1
def find_calendar_control(item,name):
 if item.objectName()==name:return item
 for child in item.childItems():
  found=find_calendar_control(child,name)
  if found is not None:return found
 return None
def click_calendar_control(name):
 control=find_calendar_control(win.contentItem(),name);assert control is not None and control.isVisible()
 point=control.mapToScene(QPointF(control.width()/2,control.height()/2))
 QTest.mouseClick(win,Qt.LeftButton,Qt.NoModifier,QPoint(round(point.x()),round(point.y())));settle(260)
assert 'Continued · 00:00 · 90 min' in find_calendar_control(win.contentItem(),'calendarEntryDetails').property('text')
click_calendar_control('calendarEntryOpen')
assert expr('editorSurface.review("editor.draftOriginal.occurrenceDate")')=='2026-11-04'
assert expr('editorSurface.review("editor.draftOriginal.repeat")')=='none'
expr('editorSurface.review("editor.close()")');settle(160)
click_calendar_control('calendarEntrySeries')
assert expr('editorSurface.review("editor.draftOriginal.id")')=='overnight'
assert expr('editorSurface.review("editor.draftOriginal.repeat")')=='weekly'
expr('editorSurface.review("editor.close()")');settle(160)
click_calendar_control('calendarEntryTaskToggle')
saved=st.read();parent=next(e for e in saved if e['id']=='overnight');child=next(e for e in saved if e.get('seriesId')=='overnight')
assert child['done'] and child['date']=='2026-11-04'
assert occurs(parent,parse('2026-10-28')) and not occurs(parent,parse('2026-11-04')) and occurs(parent,parse('2026-11-11'))
b.undo();assert st.read()==[night]
print('Month overnight display, source-occurrence edit/completion and separate Series button passed.')
# Supported date endpoints must not break week headers, navigation or QML loading.
b.commit([]);b.setView('week');b.selectDate('9999-12-31');settle()
assert len(b.weekDays)==7 and b.weekDays[-1]['date']==''
assert b.weekItems==[]
b.navigate(1);settle();assert b.selected=='9999-12-31'
b.selectDate('1000-01-01');b.navigate(-1);settle();assert b.selected=='1000-01-01'
assert expr('editorSurface.review("Cal.key(root.selected)")')=='1000-01-01'
print('Date endpoints render without QML errors; week navigation stays in range.')
win.close();engine.deleteLater();settle();assert not logs,logs
