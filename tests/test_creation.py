"""Creation milestone: deterministic parsing and transactional event templates."""
import copy
import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QCoreApplication
from app import Bridge
from store import Store,ConflictError
from logic import quick_entry,new_event,template_from_event,event_from_template,validate_templates
application=QCoreApplication.instance() or QCoreApplication([])
TODAY=dt.date(2026,10,28)
def event(**fields):
    e=new_event(TODAY);e['title']='Team meeting';e.update(fields);return e

class QuickEntryTests(unittest.TestCase):
    def test_english_and_german(self):
        for text in ['tomorrow 15:00 Dentist for 45m','Dentist tomorrow at 15:00 for 45 minutes','Morgen 15 Uhr Dentist für 45 Minuten']:
            with self.subTest(text=text):
                e=quick_entry(text,TODAY);self.assertEqual((e['title'],e['date'],e['time'],e['minutes']),('Dentist','2026-10-29','15:00',45))
    def test_relative_dates_ignore_selected_month(self):
        e=quick_entry('tomorrow 10:30 Review',TODAY,dt.date(2032,1,5));self.assertEqual(e['date'],'2026-10-29')
    def test_defaults_use_selected_date(self):
        e=quick_entry('Review',TODAY,dt.date(2032,1,5));self.assertEqual((e['date'],e['time'],e['minutes']),('2032-01-05','09:00',60))
    def test_weekdays_and_explicit_dates(self):
        for token,day in [('Monday','2026-11-02'),('Montag','2026-11-02'),('2027-03-15','2027-03-15'),('15.03.2027','2027-03-15'),('15.03.','2026-03-15'),('day after tomorrow','2026-10-30'),('übermorgen','2026-10-30')]:
            self.assertEqual(quick_entry(token+' Review',TODAY)['date'],day)
    def test_ampm_and_duration(self):
        for clock,hour in [('3 pm','15:00'),('12 am','00:00'),('12 pm','12:00'),('3:45 pm','15:45')]:
            e=quick_entry('tomorrow '+clock+' Call for 2h',TODAY);self.assertEqual(e['time'],hour);self.assertEqual(e['minutes'],120)
    def test_all_day(self):
        self.assertTrue(quick_entry('tomorrow all day Conference',TODAY)['allDay'])
        self.assertTrue(quick_entry('morgen ganztägig Messe',TODAY)['allDay'])
    def test_invalid_or_ambiguous_input(self):
        for text in ['', 'tomorrow 15:00', 'tomorrow Friday Call','10:00 11:00 Call','2026-02-30 Call','Call at 25:00','Call at 3:99','Call at 13 pm','Call for 2m','Call for 25h','Call for 1h for 2h','tomorrow 15:00 all day Call','Call at 15','Call for 0m']:
            with self.subTest(text=text),self.assertRaises(ValueError):quick_entry(text,TODAY)
    def test_unicode_title_and_preview_no_mutation(self):
        e=quick_entry('morgen 15 Uhr Grüße 日本語 🚀',TODAY);self.assertEqual(e['title'],'Grüße 日本語 🚀')
        self.assertNotEqual(e['id'],quick_entry('morgen 15 Uhr Grüße 日本語 🚀',TODAY)['id'])

class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store(pathlib.Path(self.temp.name)/'calendar.sqlite');self.b=Bridge(self.store,True)
    def tearDown(self):
        self.b.reload_timer.stop();self.b.reminder_timer.stop();self.temp.cleanup()
    def test_template_strips_identity_date_and_series(self):
        original=event(repeat='weekly',until='2027-12-31',exceptions={'2026-11-04':{'cancelled':True}},seriesId='parent',originalDate='2026-10-28')
        t=template_from_event(' Meeting ',original);draft=event_from_template(t,dt.date(2032,1,5))
        self.assertEqual(t['name'],'Meeting');self.assertEqual(draft['date'],'2032-01-05');self.assertEqual(draft['repeat'],'none')
        self.assertNotIn('seriesId',draft);self.assertNotIn('exceptions',draft);self.assertNotEqual(draft['id'],original['id']);self.assertEqual(draft['title'],original['title'])
    def test_add_persist_use_and_delete_without_touching_events(self):
        original=event();self.store.merge([original],[]);self.b.reload()
        self.assertTrue(self.b.saveTemplate('Meeting',json.dumps(original)));saved=self.b.templates[0]
        self.assertEqual(Store(self.store.path).templates(),[saved]);self.assertEqual(self.store.read(),[original])
        drafts=[];self.b.createRequested.connect(drafts.append);self.b.selectDate('2032-01-05');self.b.useTemplate(saved['id'])
        self.assertEqual(drafts[0]['date'],'2032-01-05');self.assertEqual(self.store.read(),[original])
        self.assertTrue(self.b.deleteTemplate(saved['id'],json.dumps(saved)));self.assertEqual(self.store.read(),[original]);self.assertEqual(self.store.templates(),[])
    def test_template_rename_and_cross_instance_reload(self):
        self.b.saveTemplate('Old',json.dumps(event()));saved=self.b.templates[0]
        self.assertTrue(self.b.renameTemplate(saved['id'],'New',json.dumps(saved)));self.b.reload();self.assertEqual(self.b.templates[0]['name'],'New')
    def test_stale_rename_or_delete_is_rejected(self):
        t=template_from_event('Old',event());self.store.write_template(t);self.b.reload()
        changed=copy.deepcopy(t);changed['name']='Remote';self.store.write_template(changed,t)
        self.b.reload()  # An open dialog keeps its original snapshot even after polling.
        self.assertFalse(self.b.renameTemplate(t['id'],'Local',json.dumps(t)));self.assertEqual(self.store.templates(),[changed])
        self.assertFalse(self.b.deleteTemplate(t['id'],json.dumps(t)));self.assertEqual(self.store.templates(),[changed])
    def test_template_limits_invalid_fields_and_task_rejection(self):
        for name in ['', 'x'*81]:
            with self.assertRaises(ValueError):template_from_event(name,event())
        with self.assertRaises(ValueError):template_from_event('Task',event(task=True))
        t=template_from_event('Good',event())
        with self.assertRaises(ValueError):validate_templates([t,t])
        extra=copy.deepcopy(t);extra['event']['seriesId']='parent'
        with self.assertRaises(ValueError):validate_templates([extra])
        for i in range(50):self.store.write_template(template_from_event(str(i),event()))
        with self.assertRaises(ValueError):self.store.write_template(template_from_event('Overflow',event()))
        self.assertEqual(len(self.store.templates()),50)
    def test_template_unicode_and_detached_copy_safety(self):
        t=template_from_event('🚀'*80,event(title='🚀'*200,notes='Notes',location='Studio',reminder=30))
        self.store.write_template(t);draft=event_from_template(t,TODAY);draft['notes']='Changed';self.assertEqual(t['event']['notes'],'Notes')
        validate_templates([t])
    def test_quick_preview_never_writes(self):
        before=self.store.read();preview=self.b.quickPreview('tomorrow 15:00 Dentist');self.assertFalse(preview['error']);self.assertEqual(self.store.read(),before)
