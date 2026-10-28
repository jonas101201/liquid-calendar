"""Regression coverage for the first public beta bug audit. All data is synthetic."""
import datetime as dt
import gc
import os
from pathlib import Path
import random
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch,Mock
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QCoreApplication
from app import Bridge
from logic import fingerprint,instances,occurs,parse
from store import Store
application=QCoreApplication.instance() or QCoreApplication([])
def event(ident='series',**kw):
 e=dict(id=ident,title='Synthetic task',date='2032-01-05',time='09:00',minutes=30,allDay=False,task=True,done=False,repeat='weekly',until='',category=0,location='',notes='',reminder=10)
 e.update(kw);return e
class Bugfixes(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=Store(Path(self.temp.name)/'calendar.sqlite');self.bridge=Bridge(self.store,True);self.bridge.selectDate('2032-01-05')
 def tearDown(self):self.bridge.reload_timer.stop();self.bridge.reminder_timer.stop();self.temp.cleanup()
 def put(self,records):self.store.merge(records,self.store.read());self.bridge.reload()
 def test_recurring_completion_is_scoped_to_original_occurrence(self):
  source=event(time='23:30',minutes=90);self.put([source]);self.bridge.toggleTask('series','2032-01-05',fingerprint(source))
  parent=next(e for e in self.store.read() if e['id']=='series');child=next(e for e in self.store.read() if e['id']!='series')
  self.assertFalse(parent['done']);self.assertTrue(child['done']);self.assertEqual(child['date'],'2032-01-05');self.assertEqual(child['originalDate'],'2032-01-05');self.assertFalse(occurs(parent,parse('2032-01-05')));self.assertTrue(occurs(parent,parse('2032-01-12')))
 def test_reopen_completed_child_preserves_future_and_single_instance(self):
  self.put([event()]);self.bridge.toggleTask('series','2032-01-05');child=next(e for e in self.store.read() if e['id']!='series');self.bridge.toggleTask(child['id'],child['date'],fingerprint(child))
  self.assertEqual(len(self.store.read()),2);self.assertFalse(next(e for e in self.store.read() if e['id']==child['id'])['done']);self.assertEqual(len(instances(self.store.read(),parse('2032-01-05'),1)),1);self.assertEqual(len(instances(self.store.read(),parse('2032-01-12'),1)),1)
 def test_legacy_all_series_completion_can_be_reopened(self):
  self.put([event(done=True)]);self.bridge.toggleTask('series','2032-01-05');self.assertEqual(len(self.store.read()),1);self.assertFalse(self.store.read()[0]['done'])
 def test_two_stale_instances_cannot_complete_same_date_twice(self):
  self.put([event()]);other=Bridge(self.store,True)
  try:
   self.bridge.toggleTask('series','2032-01-05');other.toggleTask('series','2032-01-05');self.assertTrue(other.error);self.assertEqual(len(self.store.read()),2)
  finally:other.reload_timer.stop();other.reminder_timer.stop()
 def test_stale_displayed_snapshot_rejected_even_after_refresh(self):
  original=event();self.put([original]);self.put([event(title='Updated elsewhere')]);self.bridge.toggleTask('series','2032-01-05',fingerprint(original));self.assertTrue(self.bridge.error);self.assertEqual(len(self.store.read()),1)
 def test_non_occurrence_rejected(self):
  self.put([event()]);self.bridge.toggleTask('series','2032-01-06');self.assertTrue(self.bridge.error);self.assertEqual(len(self.store.read()),1)
 def test_completion_undo_restores_parent_and_removes_detached_child(self):
  source=event();self.put([source]);self.bridge.toggleTask('series','2032-01-05');self.bridge.undo();self.assertEqual(self.store.read(),[source])
 def test_all_day_reminder_identifies_tomorrow(self):
  class Now(dt.datetime):
   @classmethod
   def now(cls,tz=None):return cls(2032,1,5,9,0,tzinfo=tz)
  self.put([event('tomorrow',date='2032-01-06',allDay=True,repeat='none',reminder=1440)])
  with patch('app.dt.datetime',Now),patch('app.subprocess.run',return_value=Mock(returncode=0)) as notify:
   self.bridge.remind();self.assertEqual(notify.call_args.args[0][-1],'All day tomorrow')
 def test_connections_close_and_transactions_roll_back(self):
  with self.store.connect() as connection:connection.execute('CREATE TABLE rollback_probe (value TEXT)')
  with self.assertRaises(sqlite3.ProgrammingError):connection.execute('SELECT 1')
  with self.assertRaisesRegex(RuntimeError,'rollback'):
   with self.store.connect() as connection:
    connection.execute("INSERT INTO rollback_probe VALUES ('not committed')");raise RuntimeError('rollback')
  with self.store.connect() as connection:self.assertEqual(connection.execute('SELECT count(*) FROM rollback_probe').fetchone()[0],0)
 def test_reads_do_not_wait_for_garbage_collection(self):
  if not Path('/proc/self/fd').exists():self.skipTest('Requires Linux process descriptors')
  gc.collect();was_enabled=gc.isenabled();gc.disable()
  try:
   count=len(list(Path('/proc/self/fd').iterdir()))
   for _ in range(40):self.store.read()
   self.assertLessEqual(len(list(Path('/proc/self/fd').iterdir())),count+1)
  finally:
   if was_enabled:gc.enable()
 def test_sweep_matches_pairwise_reference(self):
  rng=random.Random(812)
  for sample in range(20):
   data=[event(str(i),repeat='none',date=f'2032-01-{5+rng.randrange(3):02}',time=f'{rng.randrange(24):02}:{rng.choice([0,15,30,45]):02}',minutes=rng.choice([15,30,90,240]),task=i%3==0,done=i%7==0,allDay=i%11==0) for i in range(35)]
   rows=instances(data,parse('2032-01-05'),4)
   for row in rows:
    expected=False
    if not row['allDay'] and not(row['task'] and row['done']):
     expected=any(other is not row and other['date']==row['date'] and not other['allDay'] and not(other['task'] and other['done']) and row['start']<other['end'] and other['start']<row['end'] for other in rows)
    self.assertEqual(row['conflict'],expected,(sample,row))
 def test_conflict_calculation_does_not_parse_all_pairs(self):
  import logic
  data=[event(str(i),repeat='daily',time=f'{9+i:02}:00') for i in range(10)]
  with patch('logic.parse',wraps=logic.parse) as parser:
   rows=logic.instances(data,parse('2032-01-05'),14);self.assertEqual(len(rows),140);self.assertLess(parser.call_count,500)
if __name__=='__main__':unittest.main()
