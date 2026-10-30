"""Linked records remain independently editable and safely reversible."""
import copy
import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import QCoreApplication
from app import Bridge
from logic import new_event,export_ics,validate,fingerprint
from store import Store
application=QCoreApplication.instance() or QCoreApplication([])

class EventLinksTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=Store(Path(self.temp.name)/'calendar.sqlite')
  self.a=new_event(dt.date(2026,10,30));self.a.update(id='a',title='Design review',time='09:00',notes='First',reminder=10)
  self.b=dict(self.a,id='b',title='Planning',time='09:30',notes='Second',reminder=60)
  self.store.merge([self.a,self.b],[]);self.bridge=Bridge(self.store,True)
 def tearDown(self):
  self.bridge.reload_timer.stop();self.bridge.reminder_timer.stop();self.temp.cleanup()
 def records(self):return sorted(self.store.read(),key=lambda e:e['id'])
 def link(self):
  self.assertTrue(self.bridge.mergeEvents(json.dumps(self.a),json.dumps(self.b)),self.bridge.error)
  return self.records()
 def test_edit_move_unlink_draft_and_undo(self):
  linked=self.link();group=linked[0]['groupId']
  self.bridge.move('a',linked[0]['date'],'2026-10-31',840,fingerprint(linked[0]))
  moved=self.records();self.assertEqual(moved[0]['time'],'14:00');self.assertEqual(moved[0]['date'],'2026-10-31');self.assertEqual(moved[1],linked[1]);self.assertEqual(moved[0]['groupId'],group)
  edited=dict(linked[0],date='2026-10-31',time='14:00',notes='Edited independently')
  self.assertIsNotNone(self.bridge.commit([edited,linked[1]]))
  self.assertEqual(self.records(),[edited,linked[1]]);self.assertEqual(edited['groupId'],group)
  draft=dict(edited,title='Unsaved title')
  self.assertTrue(self.bridge.unlinkEvents(json.dumps(edited),json.dumps(draft)),self.bridge.error)
  saved=self.records();self.assertEqual(saved[0]['title'],'Unsaved title');self.assertTrue(all('groupId' not in e for e in saved))
  self.assertEqual(saved[1],self.b)
  self.bridge.undo();self.assertEqual(self.records(),[edited,linked[1]])
 def test_delete_one_clears_surviving_link_and_undo_restores_both(self):
  linked=self.link();self.assertIsNotNone(self.bridge.commit([linked[1]]))
  self.assertEqual(self.records(),[self.b]);self.bridge.undo();self.assertEqual(self.records(),linked)
 def test_conversion_to_task_unlinks_both(self):
  linked=self.link();converted=dict(linked[0],task=True)
  self.assertIsNotNone(self.bridge.commit([converted,linked[1]]));saved=self.records()
  self.assertTrue(saved[0]['task']);self.assertTrue(all('groupId' not in e for e in saved))
 def test_export_keeps_two_entries_and_json_keeps_link(self):
  linked=self.link();ics=export_ics(linked)
  self.assertEqual(ics.count('BEGIN:VEVENT'),2);self.assertIn('SUMMARY:Design review',ics);self.assertIn('SUMMARY:Planning',ics)
  self.assertEqual(validate(json.loads(json.dumps(linked))),linked)
 def test_unlink_rejects_concurrent_peer_edit_atomically(self):
  linked=self.link();remote=dict(linked[1],notes='Remote edit');self.store.merge([linked[0],remote],linked)
  before=self.records();self.assertFalse(self.bridge.unlinkEvents(json.dumps(linked[0])));self.assertEqual(self.records(),before)
 def test_unlink_rejects_forged_identity(self):
  linked=self.link();self.assertFalse(self.bridge.unlinkEvents(json.dumps(linked[0]),json.dumps(dict(linked[0],id='forged'))));self.assertEqual(self.records(),linked)
 def test_existing_groups_cannot_be_silently_regrouped(self):
  linked=self.link();other=dict(self.b,id='c');self.bridge.commit(linked+[other])
  self.assertFalse(self.bridge.mergeEvents(json.dumps(linked[0]),json.dumps(other)))
  self.assertEqual(self.records(),linked+[other])
 def test_group_id_validation(self):
  for invalid in [None,False,1,'','x'*151,{}]:
   with self.subTest(invalid=invalid),self.assertRaises(ValueError):validate([dict(self.a,groupId=invalid)])
