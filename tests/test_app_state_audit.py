"""Fresh export snapshots and failed settings writes, using isolated databases."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QCoreApplication,QUrl,QSaveFile
from app import Bridge
from logic import new_event
from store import Store
application=QCoreApplication.instance() or QCoreApplication([])

class AppStateAuditTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.store=Store(self.root/'calendar.sqlite')
  self.original=new_event(dt.date(2026,10,28));self.original.update(id='source',title='Cached title')
  self.store.merge([self.original],[]);self.bridge=Bridge(self.store,True)
 def tearDown(self):
  self.bridge.reload_timer.stop();self.bridge.reminder_timer.stop();self.temp.cleanup()
 def test_json_and_ics_export_include_changes_before_poll(self):
  updated=dict(self.original,title='Newest committed title')
  Store(self.store.path).merge([updated],[self.original])
  self.assertEqual(self.bridge.events[0]['title'],'Cached title')
  for kind in ['json','ics']:
   with self.subTest(kind=kind):
    target=self.root/('export.'+kind)
    self.bridge.exportFile(QUrl.fromLocalFile(str(target)).toString(),kind)
    text=target.read_text()
    if kind=='json':self.assertEqual(json.loads(text)['events'],[updated])
    else:self.assertIn('SUMMARY:Newest committed title',text)
 def test_unreadable_fresh_source_preserves_existing_export(self):
  target=self.root/'backup.json';target.write_text('existing export')
  with self.store.connect() as c:c.execute('UPDATE state SET value=? WHERE key=?',('invalid JSON','events'))
  self.bridge.exportFile(QUrl.fromLocalFile(str(target)).toString(),'json')
  self.assertEqual(target.read_text(),'existing export');self.assertTrue(self.bridge.error)
 def test_partial_export_write_preserves_existing_backup(self):
  target=self.root/'existing.json';target.write_text('previous complete backup')
  class InterruptedSave(QSaveFile):
   def write(self,data):
    super().write(data[:10]);raise OSError('synthetic partial write')
  with patch('app.QSaveFile',InterruptedSave):
   self.bridge.exportFile(QUrl.fromLocalFile(str(target)).toString(),'json')
  self.assertEqual(target.read_text(),'previous complete backup');self.assertTrue(self.bridge.error)
 def test_failed_settings_write_preserves_active_and_persisted_values(self):
  before=self.store.settings()
  for setter,value,prop in [('setTheme','light','theme'),('setReminders',False,'remindersEnabled'),('setAnimations',False,'animationsEnabled')]:
   with self.subTest(setter=setter):
    active=getattr(self.bridge,prop)
    with patch.object(self.store,'set_settings',side_effect=OSError('synthetic full disk')):
     getattr(self.bridge,setter)(value)
    self.assertEqual(getattr(self.bridge,prop),active)
    self.assertEqual(self.store.settings(),before)
