"""Automatic daily backups publish only complete, readable SQLite snapshots."""
import datetime as dt
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager,closing
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from logic import new_event
from store import Store

class BackupRecoveryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.store=Store(self.root/'live.sqlite',self.root/'backups')
  self.events=[]
  for n in range(15):
   event=new_event(dt.date(2026,10,31));event.update(id=str(n),title='Synthetic '+str(n),notes='x'*10000);self.events.append(event)
  with self.store.connect() as connection:connection.execute('INSERT INTO state VALUES (?,?)',('events',json.dumps(self.events)))
  self.target=self.store.backup_dir/('calendar-'+dt.date.today().strftime('%Y%m%d')+'.sqlite')
 def tearDown(self):self.temp.cleanup()
 @contextmanager
 def interrupt_copy(self):
  real_connect=self.store.connect
  class InterruptedSource:
   def __init__(self,connection):self.connection=connection
   def backup(self,destination):
    def interrupt(*args):raise OSError('synthetic interrupted copy')
    self.connection.backup(destination,pages=1,progress=interrupt)
  @contextmanager
  def interrupted_connect():
   with real_connect() as connection:yield InterruptedSource(connection)
  with patch.object(self.store,'connect',interrupted_connect):yield
 def test_interrupted_copy_leaves_no_daily_or_temporary_snapshot(self):
  with self.interrupt_copy(),self.assertRaises(OSError):self.store.backup()
  self.assertFalse(self.target.exists());self.assertIsNone(self.store._backup_date)
  self.assertEqual(list(self.store.backup_dir.glob('*.sqlite')),[])
  self.assertEqual(self.store.read(),self.events)
 def test_retry_after_interruption_backs_up_before_saving(self):
  with self.interrupt_copy(),self.assertRaises(OSError):self.store.backup()
  changed=[dict(e,title='Edited' if e['id']=='0' else e['title']) for e in self.events]
  self.store.merge(changed,self.events)
  self.assertTrue(Store.valid_backup(self.target))
  with closing(sqlite3.connect(self.target)) as connection:self.assertEqual(Store.read_conn(connection),self.events)
  self.assertEqual({e['id']:e for e in self.store.read()}['0']['title'],'Edited')
 def test_empty_or_corrupt_previous_daily_file_is_repaired(self):
  for contents in [b'',b'incomplete SQLite backup']:
   with self.subTest(contents=contents):
    self.store.backup_dir.mkdir(exist_ok=True);self.target.write_bytes(contents);self.store._backup_date=None
    self.store.backup();self.assertTrue(Store.valid_backup(self.target))
    with closing(sqlite3.connect(self.target)) as connection:self.assertEqual(Store.read_conn(connection),self.events)
 def test_failed_atomic_publish_keeps_retry_available(self):
  self.store.backup_dir.mkdir();self.target.write_bytes(b'previous incomplete copy')
  with patch('store.os.replace',side_effect=OSError('synthetic rename failure')),self.assertRaises(OSError):self.store.backup()
  self.assertEqual(self.target.read_bytes(),b'previous incomplete copy');self.assertIsNone(self.store._backup_date)
  self.assertEqual(list(self.store.backup_dir.glob('.*.sqlite')),[])
  self.store.backup();self.assertTrue(Store.valid_backup(self.target))
 def test_valid_existing_daily_snapshot_is_retained_by_another_client(self):
  self.store.backup();original=self.target.read_bytes()
  with self.store.connect() as connection:connection.execute('UPDATE state SET value=? WHERE key=?',('[]','events'))
  other=Store(self.store.path,self.store.backup_dir);other.backup()
  self.assertEqual(self.target.read_bytes(),original)
 def test_concurrent_clients_publish_one_valid_snapshot(self):
  other=Store(self.store.path,self.store.backup_dir);barrier=Barrier(2)
  def backup(store):barrier.wait();store.backup()
  with ThreadPoolExecutor(max_workers=2) as executor:
   futures=[executor.submit(backup,store) for store in [self.store,other]]
   for future in futures:future.result(timeout=10)
  self.assertTrue(Store.valid_backup(self.target));self.assertEqual(len(list(self.store.backup_dir.glob('calendar-*.sqlite'))),1)
