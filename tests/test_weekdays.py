"""Selectable weekly recurrence: bounds, exceptions, clients and export."""
import copy
import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch,Mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from app import Bridge
from store import Store
from logic import *
from PySide6.QtCore import QCoreApplication
application=QCoreApplication.instance() or QCoreApplication([])
def weekly(**kw):
 e=new_event(parse('2026-10-27'));e.update(title='Weekly lesson',repeat='weekly',weekdays=[0,2,4]);e.update(kw);return e
class WeeklyDays(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.st=Store(pathlib.Path(self.temp.name)/'calendar.sqlite');self.b=Bridge(self.st,True)
 def tearDown(self):self.b.reload_timer.stop();self.b.reminder_timer.stop();self.temp.cleanup()
 def put(self,e):self.st.merge([e],[]);self.b.reload()
 def test_dates_and_start_boundary(self):
  e=weekly();validate([e]);days=[v['date'] for v in instances([e],parse('2026-10-26'),10)]
  self.assertEqual(days,['2026-10-28','2026-10-30','2026-11-02','2026-11-04'])
 def test_all_weekday_subsets(self):
  start=parse('2026-10-26')
  for mask in range(1,128):
   days=[n for n in range(7) if mask&(1<<n)];e=weekly(date=start.isoformat(),weekdays=days)
   self.assertEqual([n for n in range(14) if occurs(e,start+dt.timedelta(days=n))],[n for n in range(14) if n%7 in days])
 def test_legacy_weekly_is_unchanged(self):
  e=weekly();del e['weekdays'];self.put(e)
  self.assertTrue(occurs(e,parse('2026-10-27')));self.assertFalse(occurs(e,parse('2026-10-28')))
  self.assertEqual(self.st.read(),[e]);self.assertEqual(next_occurrence(e,parse('2026-10-28')),parse('2026-11-03'))
 def test_invalid_masks(self):
  for value in [[],None,{},[True],[7],[-1],[1,1],['1'],[0.5]]:
   with self.subTest(value=value),self.assertRaises(ValueError):validate([weekly(weekdays=value)])
  with self.assertRaises(ValueError):validate([weekly(repeat='none')])
 def test_exceptions_until_next_and_last(self):
  e=weekly(until='2026-11-03',exceptions={'2026-10-28':{'cancelled':True}})
  self.assertEqual(next_occurrence(e,parse('2026-10-27')),parse('2026-10-30'))
  self.assertIsNone(next_occurrence(e,parse('2026-11-03')))
  self.assertEqual(representative(e,parse('2026-12-01')),parse('2026-11-02'))
 def test_search_and_free_slots_use_selected_days(self):
  e=weekly();self.assertEqual(search([e],'Monday',parse('2026-10-28'))[0]['date'],'2026-11-02')
  self.assertFalse(search([e],'Tuesday',parse('2026-10-28')))
  self.assertFalse(slot_available([e],parse('2032-01-05'),60,540))  # Monday
  self.assertTrue(slot_available([e],parse('2032-01-06'),60,540))
 def test_ics_byday_and_matching_start(self):
  e=weekly();text=export_ics([e]);self.assertIn('RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR',text);self.assertIn('DTSTART:20261028T090000',text)
  self.assertIn('DTSTART;VALUE=DATE:20261028',export_ics([weekly(allDay=True)]))
  self.assertNotIn('BEGIN:VEVENT',export_ics([weekly(until='2026-10-27')]))
 def test_detached_edit_move_completion_and_checklist(self):
  source=weekly(task=True,checklist=[dict(id='step',title='Prepare',done=False)]);self.put(source)
  drafts=[];self.b.editRequested.connect(drafts.append);self.b.edit(source['id'],'2026-10-28',True)
  self.assertNotIn('weekdays',drafts[0]);self.assertEqual(drafts[0]['repeat'],'none')
  for action in [lambda:self.b.move(source['id'],'2026-10-28','2026-10-29',600,fingerprint(source)),lambda:self.b.toggleTask(source['id'],'2026-10-28',fingerprint(source)),lambda:self.b.toggleChecklist(source['id'],'2026-10-28','step',fingerprint(source))]:
   action();self.assertFalse(self.b.error)
   parent=next(e for e in self.st.read() if e['id']==source['id']);child=next(e for e in self.st.read() if e['id']!=source['id'])
   self.assertEqual(parent['weekdays'],[0,2,4]);self.assertNotIn('weekdays',child);self.assertTrue(occurs(parent,parse('2026-10-30')))
   self.b.undo();self.assertEqual(self.st.read(),[source])
 def test_backup_roundtrip(self):
  source=weekly();self.put(source);path=pathlib.Path(self.temp.name)/'events.json';self.b.exportFile(path.as_uri(),'json');self.b.commit([]);self.b.importFile(path.as_uri());self.assertEqual(self.st.read(),[source])
 def test_reminder_only_selected_day(self):
  source=weekly();self.put(source)
  class Clock(dt.datetime):
   day=28
   @classmethod
   def now(cls,tz=None):return cls(2026,10,cls.day,8,50,tzinfo=tz)
  with patch('app.dt.datetime',Clock),patch('app.subprocess.run',return_value=Mock(returncode=0)) as notify:
   self.b.remind();self.assertEqual(notify.call_count,1);Clock.day=29;self.b.remind();self.assertEqual(notify.call_count,1)
