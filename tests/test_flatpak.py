"""Sandbox integration state with isolated records and a synthetic portal."""
import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import QCoreApplication
from app import Bridge
from logic import new_event
from store import Store
application=QCoreApplication.instance() or QCoreApplication([])
class FakePortals:
 def __init__(self):self.calls=[]
 def notify(self,*args):self.calls.append(args)
 def set_autostart(self,enabled):self.calls.append(enabled)
class FlatpakTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=Store(Path(self.temp.name)/'calendar.sqlite');self.bridge=Bridge(self.store,True)
 def tearDown(self):
  self.bridge.reload_timer.stop();self.bridge.reminder_timer.stop();self.temp.cleanup()
 def test_async_reminder_waits_for_ack_and_does_not_queue_duplicates(self):
  now=dt.datetime.now();event=new_event(now.date());event.update(id='portal',title='--help',time=now.strftime('%H:%M'),reminder=0)
  self.bridge.commit([event]);fake=FakePortals();self.bridge._portals=fake
  self.bridge.remind();self.bridge.remind();self.assertEqual(len(fake.calls),1)
  key,title,body=fake.calls[0];self.assertEqual(title,'--help');self.assertFalse(self.store.notified(key))
  self.bridge.notification_finished(key,True,'');self.assertTrue(self.store.notified(key));self.bridge.remind();self.assertEqual(len(fake.calls),1)
 def test_failed_portal_delivery_is_not_marked_sent(self):
  self.bridge._pending_notifications.add('failed');self.bridge.notification_finished('failed',False,'Synthetic failure')
  self.assertNotIn('failed',self.bridge._pending_notifications);self.assertFalse(self.store.notified('failed'));self.assertIn('Synthetic failure',self.bridge.error)
 def test_autostart_only_changes_after_successful_portal_response(self):
  fake=FakePortals();self.bridge._portals=fake;before=self.store.settings()
  self.bridge.setAutoStart(True);self.assertEqual(fake.calls,[True]);self.assertEqual(self.store.settings(),before)
  self.bridge.background_finished(False,False,'Denied');self.assertEqual(self.store.settings(),before)
  self.bridge.background_finished(True,True,'');self.assertTrue(self.store.settings()['flatpakAutostart'])
 def test_default_manifest_has_no_home_network_or_plasma_shell_grant(self):
  root=Path(__file__).resolve().parents[1];manifest=json.loads((root/'flatpak/io.github.jonas101201.LiquidCalendar.json').read_text())
  args=manifest['finish-args'];self.assertFalse(any(arg.startswith('--filesystem=') for arg in args));self.assertNotIn('--share=network',args);self.assertNotIn('--talk-name=org.kde.plasmashell',args)
