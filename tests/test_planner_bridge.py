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
 def test_appearance_round_trip_and_invalid_values(self):
  self.bridge.setAppearance('#72ebce',.84)
  restored=Bridge(self.store,True)
  try:
   self.assertEqual(restored.accentColor,'#72ebce');self.assertEqual(restored.glassOpacity,.84)
  finally:restored.reload_timer.stop();restored.reminder_timer.stop()
  before=self.store.settings()
  for accent,opacity in [('invalid',.8),('#7ceafa',.1),('#7ceafa',float('nan'))]:
   self.bridge.setAppearance(accent,opacity);self.assertEqual(self.store.settings(),before)
 def test_appearance_notifies_visuals_without_calendar_reload_or_duplicate_writes(self):
  calendar=[];visual=[]
  self.bridge.changed.connect(lambda:calendar.append(True))
  self.bridge.appearanceChanged.connect(lambda:visual.append(True))
  with patch.object(self.store,'set_settings',wraps=self.store.set_settings) as writes:
   self.bridge.setAppearance('#72ebce',.84);self.bridge.setAppearance('#72ebce',.84)
   self.assertEqual(writes.call_count,1)
  self.assertEqual(calendar,[]);self.assertEqual(visual,[True])
 def test_appearance_write_failure_preserves_active_settings(self):
  before=self.store.settings()
  with patch.object(self.store,'set_settings',side_effect=OSError('synthetic write failure')):
   self.bridge.setAppearance('#72ebce',.84)
  self.assertEqual(self.store.settings(),before);self.assertEqual(self.bridge.accentColor,'#7ceafa')
 def test_widget_gate_on_dbus_failure(self):
  home=pathlib.Path(self.temp.name);(home/'.local/share/plasma/plasmoids/org.jonas.liquidglass.calendar').mkdir(parents=True)
  with patch('app.Path.home',return_value=home),patch('app.subprocess.run',return_value=Mock(returncode=1,stdout='')):
   bridge=Bridge(self.store,False)
  try:
   self.assertFalse(bridge.widgetCompatible);self.assertIsNone(bridge.commit([event()]));self.assertEqual(self.store.read(),[])
   with self.store.connect() as c:c.execute('INSERT OR REPLACE INTO state VALUES (?,?)',('planner-protocol',json.dumps({'version':2})))
   bridge.reload();self.assertFalse(bridge.widgetCompatible)
   with self.store.connect() as c:c.execute('INSERT OR REPLACE INTO state VALUES (?,?)',('planner-protocol',json.dumps({'version':3})))
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

class TestMergeBridge(unittest.TestCase):
 setUp=TestBridge.setUp
 tearDown=TestBridge.tearDown
 def test_merge_undo_and_concurrent_edit(self):
  a=event();b=event(id='b',title='Second',time='09:30');self.store.merge([a,b],[]);self.bridge.reload()
  snapshots=[json.dumps(a),json.dumps(b)]
  self.assertTrue(self.bridge.mergeEvents(*snapshots));self.assertEqual(len(self.store.read()),1)
  self.bridge.undo();self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[a,b])
  newer=copy.deepcopy(b);newer['notes']='Another client edit';self.store.merge([a,newer],[a,b])
  self.assertFalse(self.bridge.mergeEvents(*snapshots));self.assertEqual(len(self.store.read()),2)
  self.assertEqual(next(e for e in self.store.read() if e['id']=='b')['notes'],newer['notes'])
 def test_stale_snapshot_after_reload(self):
  a=event();b=event(id='b');self.store.merge([a,b],[]);self.bridge.reload()
  newer=copy.deepcopy(a);newer['title']='Changed';self.store.merge([newer,b],[a,b]);self.bridge.reload()
  self.assertFalse(self.bridge.mergeEvents(json.dumps(a),json.dumps(b)))

 def test_former_series_with_children_rejected(self):
  a=event();b=event(id='b');child=event(id='child',seriesId='b',date='2026-11-04')
  self.store.merge([a,b,child],[]);self.bridge.reload()
  self.assertFalse(self.bridge.mergeEvents(json.dumps(a),json.dumps(b)))
  self.assertEqual(len(self.store.read()),3)

class TestOccurrenceMergeBridge(unittest.TestCase):
 setUp=TestBridge.setUp
 tearDown=TestBridge.tearDown
 def seed(self):
  self.a=event(repeat='weekly',weekdays=[2,4]);self.b=event(id='b',title='Second',repeat='daily',time='09:30')
  self.store.merge([self.a,self.b],[]);self.bridge.reload()
  return occurrence_draft(self.a,'2026-10-28'),occurrence_draft(self.b,'2026-10-28')
 def test_two_series_keep_future_and_undo(self):
  a,b=self.seed();self.assertTrue(self.bridge.mergeEvents(json.dumps(a),json.dumps(b)))
  saved=self.store.read();self.assertEqual(len(saved),3)
  for source in (self.a,self.b):
   parent=next(e for e in saved if e['id']==source['id'])
   self.assertFalse(occurs(parent,parse('2026-10-28')));self.assertTrue(occurs(parent,parse('2026-11-04')))
  merged=next(e for e in saved if e['id']==a['id']);self.assertEqual(merged['minutes'],90)
  self.assertNotIn('occurrenceOf',merged)
  self.bridge.undo();self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[self.a,self.b])
 def test_choices_exclude_self_and_cancelled_occurrences(self):
  a,b=self.seed();choices=self.bridge.mergeChoices(json.dumps(a))
  self.assertEqual(len(choices),1);self.assertEqual(choices[0]['occurrenceOf'],'b')
  cancelled=copy.deepcopy(self.b);cancelled['exceptions']={'2026-10-28':{'cancelled':True}}
  self.store.merge([self.a,cancelled],[self.a,self.b]);self.bridge.reload()
  self.assertEqual(self.bridge.mergeChoices(json.dumps(a)),[])
 def test_normal_and_occurrence_both_orders(self):
  for reverse in (False,True):
   self.store.merge([],self.store.read());self.bridge.reload()
   normal=event(id='normal');series=event(id='series',repeat='weekly')
   self.store.merge([normal,series],[]);self.bridge.reload()
   pair=[normal,occurrence_draft(series,'2026-10-28')]
   if reverse:pair.reverse()
   self.assertTrue(self.bridge.mergeEvents(*(json.dumps(e) for e in pair)))
   saved=self.store.read();self.assertEqual(len(saved),2)
   self.assertTrue(occurs(next(e for e in saved if e['id']=='series'),parse('2026-11-04')))
   self.bridge.undo();self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[normal,series])
 def test_concurrent_series_edit_rejected_atomically(self):
  a,b=self.seed();updated=copy.deepcopy(self.b);updated['notes']='Remote change'
  self.store.merge([self.a,updated],[self.a,self.b])
  self.assertFalse(self.bridge.mergeEvents(json.dumps(a),json.dumps(b)))
  self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[self.a,updated])
 def test_forged_or_stale_drafts_rejected(self):
  a,b=self.seed();a['title']='Unsaved change'
  self.assertFalse(self.bridge.mergeEvents(json.dumps(a),json.dumps(b)))
  a=occurrence_draft(self.a,'2026-10-28')
  a['originHash']='stale'
  self.assertFalse(self.bridge.mergeEvents(json.dumps(a),json.dumps(b)))
  self.assertEqual(len(self.store.read()),2)

class AtomicSchedulingTests(unittest.TestCase):
 setUp=TestBridge.setUp
 tearDown=TestBridge.tearDown
 def test_booking_between_suggestion_check_and_commit_is_rejected(self):
  task=event(id='task',task=True,date='',time='',reminder=-1)
  self.store.merge([task],[]);self.bridge.reload()
  original_merge=self.store.merge
  competitor=Store(self.store.path)
  busy=event(id='busy',date='2032-01-05',time='09:00')
  def racing_merge(desired,base,**kwargs):
   competitor.merge([task,busy],[task])
   return original_merge(desired,base,**kwargs)
  with patch.object(self.store,'merge',side_effect=racing_merge):
   self.assertFalse(self.bridge.scheduleTask('task','','2032-01-05',540,fingerprint(task)))
  saved=self.store.read()
  self.assertEqual(next(e for e in saved if e['id']=='task'),task)
  self.assertIn(busy,saved)
 def test_atomic_check_excludes_only_the_moved_occurrence(self):
  task=event(id='task',task=True,repeat='daily',date='2032-01-05')
  self.store.merge([task],[]);self.bridge.reload()
  self.assertTrue(self.bridge.scheduleTask('task','2032-01-05','2032-01-05',540,fingerprint(task)))
  self.assertEqual(len(self.store.read()),2)

class DateBoundaryTests(unittest.TestCase):
 setUp=TestBridge.setUp
 tearDown=TestBridge.tearDown
 def test_week_headers_and_navigation_are_bounded(self):
  self.bridge.setView('week');self.bridge.selectDate('9999-12-31')
  rows=self.bridge.weekDays;self.assertEqual(len(rows),7);self.assertEqual(rows[-1]['date'],'')
  self.assertEqual(self.bridge.weekItems,[])
  self.bridge.navigate(1);self.assertEqual(self.bridge.selected,'9999-12-31')
  self.bridge.selectDate('1000-01-01');self.bridge.navigate(-1)
  self.assertEqual(self.bridge.selected,'1000-01-01')
  self.assertTrue(all(not r['date'] or r['date']>='1000-01-01' for r in self.bridge.weekDays))

if __name__=='__main__':unittest.main(verbosity=2)

class TestMergeEditorDraft(unittest.TestCase):
 setUp=TestBridge.setUp
 tearDown=TestBridge.tearDown
 def seed(self):
  a=event(title='Saved title',location='Office');b=event(id='b',title='Second',time='10:00',notes='Other notes')
  self.store.merge([a,b],[]);self.bridge.reload();return a,b
 def test_preview_commit_and_single_undo_use_draft(self):
  a,b=self.seed();draft=dict(a,title='Edited title',notes='Draft notes',location='Studio',time='08:30',minutes=120,category=3,reminder=60)
  args=[json.dumps(e) for e in (a,b,draft)]
  preview=self.bridge.mergePreview(*args)['event']
  self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[a,b])
  self.assertEqual(preview['title'],'Edited title / Second');self.assertEqual(preview['time'],'08:30');self.assertEqual(preview['minutes'],150)
  self.assertEqual(preview['notes'],'Draft notes\n\nOther notes');self.assertEqual(preview['location'],'Studio');self.assertEqual(preview['category'],3)
  self.assertTrue(self.bridge.mergeEvents(*args));self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[preview])
  self.bridge.undo();self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[a,b])
 def test_choices_follow_edited_date_and_all_day(self):
  a,b=self.seed();other=event(id='next-day',date='2026-10-29',allDay=True)
  self.store.merge([a,b,other],[a,b]);self.bridge.reload();draft=dict(a,date='2026-10-29',allDay=True)
  choices=self.bridge.mergeChoices(json.dumps(a),json.dumps(draft));self.assertEqual([e['id'] for e in choices],['next-day'])
  self.assertTrue(self.bridge.mergeEvents(json.dumps(a),json.dumps(other),json.dumps(draft)))
  merged=next(e for e in self.store.read() if e['id']=='a');self.assertEqual(merged['date'],'2026-10-29');self.assertTrue(merged['allDay'])
 def test_invalid_draft_or_identity_never_writes(self):
  a,b=self.seed()
  for changes in [dict(title=''),dict(id='forged'),dict(occurrenceOf='forged'),dict(repeat='daily'),dict(exceptions={'2026-10-29':{'cancelled':True}})]:
   draft=dict(a,**changes)
   self.assertIn('error',self.bridge.mergePreview(json.dumps(a),json.dumps(b),json.dumps(draft)))
   self.assertFalse(self.bridge.mergeEvents(json.dumps(a),json.dumps(b),json.dumps(draft)))
   self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[a,b])
 def test_whole_series_cannot_be_merged_as_an_edited_once_event(self):
  a,b=self.seed();series=dict(a,repeat='daily');self.store.merge([series,b],[a,b]);self.bridge.reload()
  self.assertFalse(self.bridge.mergeEvents(json.dumps(series),json.dumps(b),json.dumps(a)))
  self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[series,b])
 def test_concurrent_source_changes_preserved_with_editor_draft(self):
  a,b=self.seed();remote=dict(a,notes='Remote edit');self.store.merge([remote,b],[a,b])
  self.assertFalse(self.bridge.mergeEvents(json.dumps(a),json.dumps(b),json.dumps(dict(a,title='Local edit'))))
  self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[remote,b])
 def test_rescheduled_occurrence_cancels_original_day_only(self):
  series=event(repeat='weekly');b=event(id='b',date='2026-10-29')
  self.store.merge([series,b],[]);self.bridge.reload();source=occurrence_draft(series,'2026-10-28');draft=dict(source,date='2026-10-29',notes='Unsaved occurrence note')
  self.assertTrue(self.bridge.mergeEvents(json.dumps(source),json.dumps(b),json.dumps(draft)))
  saved=self.store.read();parent=next(e for e in saved if e['id']=='a');merged=next(e for e in saved if e['id']==source['id'])
  self.assertFalse(occurs(parent,parse('2026-10-28')));self.assertTrue(occurs(parent,parse('2026-11-04')))
  self.assertEqual(merged['date'],'2026-10-29');self.assertEqual(merged['notes'],'Unsaved occurrence note')
  self.bridge.undo();self.assertEqual(sorted(self.store.read(),key=lambda e:e['id']),[series,b])

 def test_moved_occurrence_can_merge_with_same_series_on_target_day(self):
  series=event(repeat='daily');self.store.merge([series],[]);self.bridge.reload()
  source=occurrence_draft(series,'2026-10-28');draft=dict(source,date='2026-10-29',title='Moved occurrence')
  choices=self.bridge.mergeChoices(json.dumps(source),json.dumps(draft));self.assertEqual(len(choices),1)
  self.assertEqual(choices[0]['occurrenceOf'],'a');self.assertEqual(choices[0]['occurrenceDate'],'2026-10-29')
  self.assertTrue(self.bridge.mergeEvents(json.dumps(source),json.dumps(choices[0]),json.dumps(draft)))
  parent=next(e for e in self.store.read() if e['id']=='a')
  self.assertFalse(occurs(parent,parse('2026-10-28')));self.assertFalse(occurs(parent,parse('2026-10-29')))
  self.assertTrue(occurs(parent,parse('2026-10-30')))
  self.bridge.undo();self.assertEqual(self.store.read(),[series])

 def test_parallel_identical_merge_with_distinct_occurrence_ids_rejected(self):
  series=event(repeat='daily');other=event(id='b');self.store.merge([series,other],[]);self.bridge.reload()
  remote=Bridge(self.store,True)
  try:
   first=occurrence_draft(series,'2026-10-28');second=occurrence_draft(series,'2026-10-28')
   self.assertNotEqual(first['id'],second['id'])
   self.assertTrue(remote.mergeEvents(json.dumps(first),json.dumps(other),json.dumps(dict(first,title='Remote edit'))))
   after=self.store.read()
   self.assertFalse(self.bridge.mergeEvents(json.dumps(second),json.dumps(other),json.dumps(dict(second,title='Local edit'))))
   self.assertEqual(self.store.read(),after)
  finally:remote.reload_timer.stop();remote.reminder_timer.stop()
