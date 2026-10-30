"""Exercise real Qt D-Bus marshalling against a private synthetic portal service.
Run with dbus-run-session; never contacts the desktop's real portal service.
"""
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QObject,Signal,Slot,QCoreApplication,QEventLoop,QTimer,ClassInfo
from PySide6.QtDBus import QDBusConnection,QDBusObjectPath
from desktop_portals import DesktopPortals,PATH,SERVICE
if not os.environ.get('LIQUID_PORTAL_TEST_BUS'):raise SystemExit('Use LIQUID_PORTAL_TEST_BUS=1 dbus-run-session -- python tests/check_desktop_portals.py')
application=QCoreApplication([]);bus=QDBusConnection.sessionBus()
assert bus.registerService(SERVICE),bus.lastError().message()
requests=[];notifications=[];deny_next=False;response_delay=20;alternate_handle=False;closed=[];grants=[]
@ClassInfo(**{'D-Bus Interface':'org.freedesktop.portal.Request'})
class Request(QObject):
    Response=Signal('uint','QVariantMap')
    @Slot()
    def Close(self):self.closed=True;closed.append(self.path)
class Background(QObject):
    @Slot(str,'QVariantMap',result=QDBusObjectPath)
    def RequestBackground(self,parent,options):
        path=PATH+'/request/'+bus.baseService().lstrip(':').replace('.','_')+'/'+options['handle_token']
        if alternate_handle:path+='_alternative'
        request=Request();request.path=path;request.closed=False;requests.append(request)
        assert bus.registerObject(path,'org.freedesktop.portal.Request',request,QDBusConnection.ExportAllSignals|QDBusConnection.ExportAllSlots)
        def respond():
            if request.closed:return
            if not deny_next:grants.append(path)
            request.Response.emit(1 if deny_next else 0,{'background':True,'autostart':bool(options['autostart'])})
        QTimer.singleShot(response_delay,respond)
        return QDBusObjectPath(path)
    @Slot(str,'QVariantMap')
    def AddNotification(self,key,options):notifications.append((key,options))
# Export methods on their actual interfaces with adaptors.
from PySide6.QtDBus import QDBusAbstractAdaptor
from PySide6.QtCore import ClassInfo
@ClassInfo(**{'D-Bus Interface':'org.freedesktop.portal.Background'})
class BackgroundAdaptor(QDBusAbstractAdaptor):
    @Slot(str,'QVariantMap',result=QDBusObjectPath)
    def RequestBackground(self,parent,options):return service.RequestBackground(parent,options)
@ClassInfo(**{'D-Bus Interface':'org.freedesktop.portal.Notification'})
class NotificationAdaptor(QDBusAbstractAdaptor):
    @Slot(str,'QVariantMap')
    def AddNotification(self,key,options):service.AddNotification(key,options)
service=Background();background=BackgroundAdaptor(service);notification=NotificationAdaptor(service)
assert bus.registerObject(PATH,service,QDBusConnection.ExportAdaptors)
portal=DesktopPortals();background_results=[];notification_results=[]
portal.backgroundFinished.connect(lambda *args:background_results.append(args));portal.notificationFinished.connect(lambda *args:notification_results.append(args))
def wait(predicate):
    loop=QEventLoop();timer=QTimer();timer.setInterval(10);timer.timeout.connect(lambda:loop.quit() if predicate() else None);timer.start();QTimer.singleShot(2500,loop.quit);loop.exec();assert predicate(),(background_results,notification_results,bus.lastError().message(),len(requests))
portal.set_autostart(True);wait(lambda:len(background_results)==1);assert background_results[-1]==(True,True,''),background_results
portal.set_autostart(False);wait(lambda:len(background_results)==2);assert background_results[-1]==(True,False,''),background_results
deny_next=True
portal.set_autostart(True);wait(lambda:len(background_results)==3);assert not background_results[-1][0] and background_results[-1][2]
deny_next=False
# A timeout must close the remote dialog and prevent a late permission grant.
response_delay=120;previous_grants=len(grants)
portal.set_autostart(True);portal.background.timer.start(25)
wait(lambda:len(background_results)==4)
assert not background_results[-1][0] and 'timed out' in background_results[-1][2]
wait(lambda:bool(closed));assert portal.background is None
loop=QEventLoop();QTimer.singleShot(200,loop.quit);loop.exec()
assert len(grants)==previous_grants and len(background_results)==4
# A later request works, even if an older backend returns another handle.
response_delay=20;alternate_handle=True
portal.set_autostart(True);wait(lambda:len(background_results)==5)
assert background_results[-1]==(True,True,''),background_results
alternate_handle=False
portal.notify('test-key','--help','Synthetic title is literal text');wait(lambda:bool(notification_results));assert notification_results==[('test-key',True,'')]
assert notifications==[('test-key',{'title':'--help','body':'Synthetic title is literal text'})],notifications
print('Private D-Bus portal: autostart enable/disable/timeout cancellation and alternative handles, asynchronous notification and literal title passed.')
