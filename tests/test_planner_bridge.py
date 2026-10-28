import os,sys,pathlib,tempfile,datetime as dt,unittest,copy
os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QCoreApplication
from app import Bridge
from logic import *
from store import Store,ConflictError
from unittest.mock import patch,Mock
application=QCoreApplication.instance() or QCoreApplication([])
def event(**kw):
 e=dict(id='a',title='Termin',date='2026-10-28',time='09:00',minutes=60,allDay=False,task=False,done=False,repeat='none',until='',category=0,location='',notes='',reminder=10);e.update(kw);return e
class FakeNow(dt.datetime):
 @classmethod
 def now(cls,tz=None):return cls(2026,10,28,8,50,tzinfo=tz)
class TestBridge(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=Store(pathlib.Path(self.temp.name)/'db.sqlite');self.bridge=Bridge(self.store,True)
 def tearDown(self):self.bridge.reload_timer.stop();self.bridge.reminder_timer.stop();self.temp.cleanup()
 def test_widget_gate_on_dbus_failure(self):
  home=pathlib.Path(self.temp.name);(home/'.local/share/plasma/plasmoids/org.jonas.liquidglass.calendar').mkdir(parents=True)
  with patch('app.Path.home',return_value=home),patch('app.subprocess.run',return_value=Mock(returncode=1,stdout='')):
   bridge=Bridge(self.store,False)
  try:
   self.assertFalse(bridge.widgetCompatible);self.assertIsNone(bridge.commit([event()]));self.assertEqual(self.store.read(),[])
   with self.store.connect() as c:c.execute('INSERT OR REPLACE INTO state VALUES (?,?)',('planner-protocol',json.dumps({'version':2})))
   bridge.reload();self.assertTrue(bridge.widgetCompatible)
  finally:bridge.reload_timer.stop();bridge.reminder_timer.stop()
 def test_notification_once(self):
  self.store.merge([event()],[])
  with patch('app.dt.datetime',FakeNow),patch('app.subprocess.run',return_value=Mock(returncode=0)) as notify:
   self.bridge.remind();self.bridge.remind();self.assertEqual(notify.call_count,1)
 def test_disabled_or_done_no_notification(self):
  self.store.merge([event(task=True,done=True)],[])
  with patch('app.dt.datetime',FakeNow),patch('app.subprocess.run',return_value=Mock(returncode=0)) as notify:
   self.bridge.remind();self.assertEqual(notify.call_count,0)
   self.bridge.setReminders(False);self.bridge.remind();self.assertEqual(notify.call_count,0)
 def test_failed_notification_retried(self):
  self.store.merge([event()],[])
  with patch('app.dt.datetime',FakeNow),patch('app.subprocess.run',side_effect=[Mock(returncode=1),Mock(returncode=0)]) as notify:
   self.bridge.remind();self.bridge.remind();self.assertEqual(notify.call_count,2)
 def test_single_occurrence_delete_and_undo(self):
  source=event(repeat='weekly');self.store.merge([source],[]);self.bridge.reload()
  self.assertTrue(self.bridge.deleteOccurrence('a','2026-11-04',fingerprint(source)))
  self.assertFalse(occurs(self.store.read()[0],parse('2026-11-04')))
  self.assertTrue(occurs(self.store.read()[0],parse('2026-11-11')))
  self.bridge.undo();self.assertTrue(occurs(self.store.read()[0],parse('2026-11-04')))
 def test_delete_series_cascades_and_undo(self):
  source=event(repeat='weekly');self.store.merge([source],[])
  child=event(id='child',repeat='none',occurrenceOf='a',occurrenceDate='2026-11-04',originHash=fingerprint(source))
  self.store.merge([source,child],[source],allow_occurrences=True);self.bridge.reload()
  self.bridge.commit([]);self.assertEqual(self.store.read(),[]);self.bridge.undo();self.assertEqual(len(self.store.read()),2)
 def test_import_pending_commands_rejected(self):
  path=pathlib.Path(self.temp.name)/'invalid.json';path.write_text(json.dumps({'format':'liquid-glass-calendar','version':1,'events':[event(occurrenceOf='x')]}))
  self.bridge.importFile(path.as_uri());self.assertEqual(self.store.read(),[]);self.assertTrue(self.bridge.error)
 def test_lanes_only_overlapping_group(self):
  rows=instances([event(),event(id='b',time='09:30'),event(id='c',time='12:00')],parse('2026-10-28'),1)
  self.assertEqual(next(v for v in rows if v['id']=='c')['lanes'],1);self.assertEqual(rows[0]['lanes'],2)
 def test_autostart_opt_in_test_path(self):
  self.assertFalse(self.bridge.autoStart);self.bridge.setAutoStart(True);self.assertTrue(self.bridge.autoStart);self.bridge.setAutoStart(False);self.assertFalse(self.bridge.autoStart)
if __name__=='__main__':unittest.main(verbosity=2)
