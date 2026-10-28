"""Isolated widget editor integration; Kirigami theme lookup is stubbed only."""
import os,pathlib,tempfile,shutil,json
os.environ.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_QUICK_CONTROLS_STYLE='Basic')
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine,QQmlExpression
from PySide6.QtCore import QUrl,QEventLoop,QTimer,qInstallMessageHandler
app=QApplication([]);logs=[];qInstallMessageHandler(lambda typ,ctx,text:logs.append(text))
src=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='widget-repeat-test-') as folder:
 root=pathlib.Path(folder);shutil.copytree(src/'companion-widget/contents/ui',root/'ui')
 file=root/'ui/CalendarView.qml';code=file.read_text().replace('import org.kde.kirigami as Kirigami\n','').replace('Kirigami.Theme.backgroundColor.r > 0.6','false').replace('id: root','id: root\n function review(code){return eval(code);}',1);file.write_text(code)
 (root/'ui/Test.qml').write_text('import QtQuick\nimport QtQuick.Controls\nApplicationWindow {id:win;visible:true;width:650;height:800;CalendarView {id:calendar;anchors.fill:parent} function review(code){return eval(code);}}')
 engine=QQmlApplicationEngine();engine.setOfflineStoragePath(str(root/'offline'));engine.load(QUrl.fromLocalFile(str(root/'ui/Test.qml')));assert engine.rootObjects(),logs
 win=engine.rootObjects()[0]
 def settle():
  loop=QEventLoop();QTimer.singleShot(180,loop.quit);loop.exec()
 def expr(code):
  x=QQmlExpression(engine.rootContext(),win,'review('+json.dumps(code)+')');v=x.evaluate();assert not x.hasError(),x.error().toString();return v[0]
 entry=dict(id='synthetic',title='Weekly lesson',date='2026-10-27',time='09:00',minutes=60,allDay=False,task=True,done=False,repeat='weekly',until='',category=0,location='',notes='',reminder=10,weekdays=[0,2,4],priority=3,project='Test project',checklist=[dict(id='step',title='Prepare',done=True)])
 expr('calendar.store(['+json.dumps(entry)+']);calendar.openEvent(calendar.events[0])');settle()
 assert expr('calendar.review("priorityBox.currentIndex")')==3
 assert expr('calendar.review("projectField.text")')=='Test project'
 assert expr('calendar.review("JSON.stringify(editor.checklist)")')==json.dumps(entry['checklist'],separators=(',',':'))
 assert expr('calendar.review("JSON.stringify(editor.weeklyDays())")')=='[0,2,4]'
 expr('calendar.review("repeatDays.itemAt(1).clicked();saveButton.clicked()")');settle()
 stored=json.loads(expr('JSON.stringify(calendar.events)'))[0]
 assert stored['weekdays']==[0,1,2,4];assert stored['checklist']==entry['checklist'];assert stored['priority']==3;assert stored['project']=='Test project'
 expr('calendar.openEvent(calendar.events[0]);calendar.review("repeatBox.currentIndex=0;saveButton.clicked()")');settle()
 assert 'weekdays' not in json.loads(expr('JSON.stringify(calendar.events)'))[0]
 win.close();engine.deleteLater();settle();assert not logs,logs
 print('Isolated widget weekly editor, metadata retention and rule removal passed; live Kirigami/Plasma not tested.')
