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
print('English dates/search; German aliases; non-ASCII data preserved; 14 small-window views rendered.')
win.close();engine.deleteLater();settle();assert not logs,logs
