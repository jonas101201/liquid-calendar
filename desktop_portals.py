"""Non-blocking desktop portals used by the Flatpak build."""
import uuid
from PySide6.QtCore import QObject,Signal,Slot,QTimer,SLOT
from PySide6.QtDBus import QDBusConnection,QDBusMessage,QDBusPendingCallWatcher

SERVICE='org.freedesktop.portal.Desktop'
PATH='/org/freedesktop/portal/desktop'

class BackgroundRequest(QObject):
    finished=Signal(bool,bool,str)
    def __init__(self,bus,enabled,parent=None):
        super().__init__(parent);self.bus=bus;self.enabled=enabled;self.done=False
        self.token='calendar_'+uuid.uuid4().hex
        sender=bus.baseService().lstrip(':').replace('.','_')
        self.path=PATH+'/request/'+sender+'/'+self.token
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.timeout)
    def start(self):
        if not self.bus.connect(SERVICE,self.path,'org.freedesktop.portal.Request','Response',self,SLOT('response(uint,QVariantMap)')):
            self.finish(False,False,'Could not listen for background permission.');return
        self.timer.start(120000)
        message=QDBusMessage.createMethodCall(SERVICE,PATH,'org.freedesktop.portal.Background','RequestBackground')
        message.setArguments(['',{'handle_token':self.token,'reason':'Start Liquid Calendar at login and deliver calendar reminders.','autostart':self.enabled}])
        watcher=QDBusPendingCallWatcher(self.bus.asyncCall(message,8000),self)
        def complete():
            reply=watcher.reply()
            if reply.type()==QDBusMessage.ErrorMessage:self.finish(False,False,reply.errorMessage())
            elif not self.done and reply.arguments():
                handle=reply.arguments()[0]
                actual=handle.path() if hasattr(handle,'path') else str(handle)
                if actual!=self.path:
                    self.bus.disconnect(SERVICE,self.path,'org.freedesktop.portal.Request','Response',self,SLOT('response(uint,QVariantMap)'))
                    self.path=actual
                    if not self.bus.connect(SERVICE,self.path,'org.freedesktop.portal.Request','Response',self,SLOT('response(uint,QVariantMap)')):
                        self.cancel_remote();self.finish(False,False,'Could not listen for background permission.')
            watcher.deleteLater()
        watcher.finished.connect(complete)
    @Slot('uint','QVariantMap')
    def response(self,code,results):
        if code!=0:self.finish(False,False,'Background permission was not granted.');return
        allowed=bool(results.get('background',False))
        autostart=bool(results.get('autostart',False))
        if self.enabled and (not allowed or not autostart):self.finish(False,False,'Autostart permission was not granted.');return
        self.finish(True,autostart,'')
    def cancel_remote(self):
        message=QDBusMessage.createMethodCall(SERVICE,self.path,'org.freedesktop.portal.Request','Close')
        self.bus.asyncCall(message,8000)
    def timeout(self):
        if self.done:return
        self.cancel_remote()
        self.finish(False,False,'Background permission request timed out; the request was cancelled.')
    def finish(self,ok,autostart,error):
        if self.done:return
        self.done=True;self.timer.stop()
        self.bus.disconnect(SERVICE,self.path,'org.freedesktop.portal.Request','Response',self,SLOT('response(uint,QVariantMap)'))
        self.finished.emit(ok,autostart,error);self.deleteLater()

class DesktopPortals(QObject):
    notificationFinished=Signal(str,bool,str)
    backgroundFinished=Signal(bool,bool,str)
    def __init__(self,parent=None):
        super().__init__(parent);self.bus=QDBusConnection.sessionBus();self.background=None
    def notify(self,key,title,body):
        message=QDBusMessage.createMethodCall(SERVICE,PATH,'org.freedesktop.portal.Notification','AddNotification')
        message.setArguments([key,{'title':title,'body':body}])
        watcher=QDBusPendingCallWatcher(self.bus.asyncCall(message,8000),self)
        def complete():
            reply=watcher.reply();ok=reply.type()!=QDBusMessage.ErrorMessage
            self.notificationFinished.emit(key,ok,'' if ok else reply.errorMessage());watcher.deleteLater()
        watcher.finished.connect(complete)
    def set_autostart(self,enabled):
        if self.background is not None:
            self.backgroundFinished.emit(False,False,'A background permission request is already open.');return
        request=BackgroundRequest(self.bus,enabled,self);self.background=request
        def complete(ok,autostart,error):
            self.background=None;self.backgroundFinished.emit(ok,autostart,error)
        request.finished.connect(complete);request.start()
