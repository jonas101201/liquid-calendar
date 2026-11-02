"""Task attachment editor interactions with synthetic local files and no personal DB."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
os.environ.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_QUICK_CONTROLS_STYLE='Basic')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl,QEventLoop,QTimer,qInstallMessageHandler
from PySide6.QtQml import QQmlApplicationEngine,QQmlExpression
from app import Bridge
from store import Store

app=QApplication([]);logs=[];qInstallMessageHandler(lambda kind,ctx,msg:logs.append(msg))
def settle(ms=200):
    loop=QEventLoop();QTimer.singleShot(ms,loop.quit);loop.exec()
with tempfile.TemporaryDirectory(prefix='calendar-file-ui-') as directory:
    root=Path(directory);shutil.copytree(ROOT/'qml',root/'qml')
    for file,marker in [('App.qml','id:win'),('CalendarEditor.qml','id: root')]:
        p=root/'qml'/file;p.write_text(p.read_text().replace(marker,marker+'\n function review(code){return eval(code);}',1))
    store=Store(root/'test.sqlite');bridge=Bridge(store,True)
    engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('planner',bridge)
    engine.load(QUrl.fromLocalFile(str(root/'qml/App.qml')));assert engine.rootObjects(),logs
    win=engine.rootObjects()[0];win.setWidth(980);win.setHeight(780);win.requestActivate();settle()
    def expr(code):
        x=QQmlExpression(engine.rootContext(),win,'review('+json.dumps(code)+')');v=x.evaluate();assert not x.hasError(),x.error().toString();return v[0]
    def edit(code):return expr('editorSurface.review('+json.dumps(code)+')')
    file=root/'Lernzettel 日本語.txt';file.write_text('Synthetic file content. No personal data.')
    for theme in ['dark','light']:
        bridge.setTheme(theme);expr('editorSurface.openNewTask(win.dateValue(planner.selected))');settle()
        edit('titleField.text="Task with files";attachmentPicker.options=FileDialog.DontUseNativeDialog;attachmentPicker.currentFolder='+json.dumps(root.as_uri())+';attachmentPicker.selectedFile='+json.dumps(file.as_uri())+';attachmentPicker.open()');settle()
        edit('attachmentPicker.accept()');settle()
        assert edit('editor.attachmentFiles.length===1 && attachmentRows.count===1')
        assert store.read()==[] and bridge._pending_attachments
        edit('task.checked=false;task.clicked()');assert edit('task.checked && editor.validation.length>0')
        # Closing a new unsaved task must release staged bytes, without touching files.
        edit('editor.close()');settle();assert not bridge._pending_attachments and store.read()==[]
    expr('editorSurface.openNewTask(win.dateValue(planner.selected))');settle()
    edit('titleField.text="Task with files";editor.addFiles('+json.dumps([file.as_uri()])+');saveButton.clicked()');settle()
    saved=store.read();assert len(saved)==1 and len(saved[0]['attachments'])==1
    ident=saved[0]['id'];blob=saved[0]['attachments'][0]['id'];file.unlink()
    bridge.edit(ident,'',True);settle()
    assert edit('editor.attachmentFiles[0].name==="Lernzettel 日本語.txt"')
    # Remove the visible row, Cancel, reopen: saved attachment is intact.
    edit('attachmentRows.itemAt(0).children[3].clicked()');settle(30)
    assert edit('editor.attachmentFiles.length===0');assert store.read()==saved
    edit('editor.close()');settle();bridge.edit(ident,'',True);settle()
    assert edit('attachmentRows.count===1')
    edit('attachmentRows.itemAt(0).children[3].clicked();saveButton.clicked()');settle()
    assert store.read()[0]['attachments']==[]
    bridge.undo();assert store.read()==saved and store.attachment_data(blob)
    bridge.edit(ident,'',True);settle()
    if os.environ.get('LIQUID_ATTACHMENT_SCREENSHOTS'):
        out=Path(os.environ['LIQUID_ATTACHMENT_SCREENSHOTS']);out.mkdir(parents=True,exist_ok=True)
        assert win.grabWindow().save(str(out/'task-attachments.png'))
    edit('editor.close()');settle()
    bridge.reload_timer.stop();bridge.reminder_timer.stop();engine.deleteLater();settle()
    assert not logs,logs
print('Task files: both themes, draft cancellation, task conversion guard, Save/reopen without original, remove/Cancel and saved removal/Undo passed.')
