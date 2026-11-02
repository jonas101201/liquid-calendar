"""Background import atomicity, cancellation and shared-store concurrency."""
import base64
import fcntl
import os
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QCoreApplication
from app import Bridge
from import_job import ImportJob
from logic import new_event
from store import Store
application=QCoreApplication.instance() or QCoreApplication([])

def event(ident):
    value=new_event(dt.date(2026,11,2));value.update(id=ident,title='Import '+ident);return value

class AsyncImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.store=Store(self.root/'data.sqlite');self.bridge=Bridge(self.store,True)
        self.path=self.root/'backup.json';self.path.write_text(json.dumps({'format':'liquid-glass-calendar','version':1,'events':[event('new')]}))
    def tearDown(self):
        self.bridge.shutdown_imports();application.processEvents()
        self.bridge.reload_timer.stop();self.bridge.reminder_timer.stop();self.temp.cleanup()
    def wait(self,condition,timeout=5):
        until=time.monotonic()+timeout
        while not condition() and time.monotonic()<until:application.processEvents();time.sleep(.003)
        self.assertTrue(condition())
    def test_async_success_preserves_selection_and_supports_undo(self):
        self.bridge.selectDate('2026-12-24');self.bridge.setView('tasks')
        self.assertTrue(self.bridge.startImport(self.path.as_uri()));self.wait(lambda:not self.bridge.importBusy)
        self.assertEqual(self.bridge.error,'');self.assertEqual(self.bridge.selected,'2026-12-24');self.assertEqual(self.bridge.view,'tasks')
        self.assertEqual([row['id'] for row in self.store.read()],['new']);self.bridge.undo();self.assertEqual(self.store.read(),[])
    def test_cancel_during_read_retains_records_and_undo(self):
        self.bridge.commit([event('existing')]);before=self.store.read();undo=self.bridge._undo
        entered=threading.Event();release=threading.Event();original=ImportJob.read_document
        def hold(job):entered.set();release.wait(3);return original(job)
        with patch.object(ImportJob,'read_document',hold):
            self.bridge.startImport(self.path.as_uri());self.wait(entered.is_set)
            self.bridge.cancelImport();release.set();self.wait(lambda:not self.bridge.importBusy)
        self.assertEqual(self.store.read(),before);self.assertEqual(self.bridge._undo,undo);self.assertIn('cancelled',self.bridge.notice)
    def test_cancel_before_commit_rolls_back_entries_and_files(self):
        data=b'attached bytes';ident=hashlib.sha256(data).hexdigest();record=event('new');record['task']=True
        record['attachments']=[dict(id=ident,name='file.txt',size=len(data))]
        self.path.write_text(json.dumps({'format':'liquid-glass-calendar','version':2,'events':[record],'files':{ident:base64.b64encode(data).decode()}}))
        entered=threading.Event();release=threading.Event();original=ImportJob.seal
        def hold(job):entered.set();release.wait(3);original(job)
        with patch.object(ImportJob,'seal',hold):
            self.bridge.startImport(self.path.as_uri());self.wait(entered.is_set)
            self.bridge.cancelImport();release.set();self.wait(lambda:not self.bridge.importBusy)
        self.assertEqual(self.store.read(),[])
        with self.store.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM planner_attachments').fetchone()[0],0)
    def test_sealed_commit_cannot_be_reported_as_cancelled(self):
        entered=threading.Event();release=threading.Event();original=ImportJob.seal
        def hold(job):original(job);entered.set();release.wait(3)
        with patch.object(ImportJob,'seal',hold):
            self.bridge.startImport(self.path.as_uri());self.wait(entered.is_set)
            self.bridge.cancelImport();release.set();self.wait(lambda:not self.bridge.importBusy)
        self.assertEqual([row['id'] for row in self.store.read()],['new']);self.assertNotIn('cancelled',self.bridge.notice)
    def test_external_change_while_reading_is_preserved(self):
        entered=threading.Event();release=threading.Event();original=ImportJob.read_document
        def hold(job):entered.set();release.wait(3);return original(job)
        with patch.object(ImportJob,'read_document',hold):
            self.bridge.startImport(self.path.as_uri());self.wait(entered.is_set)
            self.store.merge([event('widget')],[]);release.set();self.wait(lambda:not self.bridge.importBusy)
        self.assertEqual({row['id'] for row in self.store.read()},{'widget','new'})
        self.bridge.undo();self.assertEqual([row['id'] for row in self.store.read()],['widget'])
    def test_invalid_input_does_not_change_records(self):
        self.path.write_text('{broken JSON');self.bridge.startImport(self.path.as_uri());self.wait(lambda:not self.bridge.importBusy)
        self.assertTrue(self.bridge.error);self.assertEqual(self.store.read(),[])
    def test_cancel_while_waiting_for_backup_lock(self):
        self.store.backup_dir.mkdir(parents=True,exist_ok=True)
        with (self.store.backup_dir/'.backup.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            self.bridge.startImport(self.path.as_uri())
            self.wait(lambda:self.bridge.importProgress>=88)
            self.bridge.cancelImport();self.wait(lambda:not self.bridge.importBusy,1)
        self.assertEqual(self.store.read(),[])
    def test_fifo_is_rejected_without_blocking_cancellation(self):
        fifo=self.root/'not-a-file.json';os.mkfifo(fifo)
        self.bridge.startImport(fifo.as_uri());self.wait(lambda:not self.bridge.importBusy,1)
        self.assertIn('regular',self.bridge.error);self.assertEqual(self.store.read(),[])
    def test_one_job_at_a_time_and_edits_are_guarded(self):
        entered=threading.Event();release=threading.Event();original=ImportJob.read_document
        def hold(job):entered.set();release.wait(3);return original(job)
        with patch.object(ImportJob,'read_document',hold):
            self.bridge.startImport(self.path.as_uri());self.wait(entered.is_set)
            self.assertFalse(self.bridge.startImport(self.path.as_uri()));self.assertIsNone(self.bridge.commit([event('editor')]))
            self.bridge.cancelImport();release.set();self.wait(lambda:not self.bridge.importBusy)
        self.assertEqual(self.store.read(),[])
