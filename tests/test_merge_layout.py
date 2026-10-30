import copy,datetime as dt,json,pathlib,tempfile,unittest
from logic import merge_events,instances,new_event,validate

def event(ident='a',**kw):
 e=new_event(dt.date(2026,10,28));e.update(id=ident,title=ident,time='09:00',minutes=60);e.update(kw);return e

class MergeTests(unittest.TestCase):
 def test_link_preserves_independent_contents_and_sources(self):
  a=event(notes='First',location='Office');b=event('b',time='09:30',notes='Second',location='Online',reminder=60)
  original=copy.deepcopy([a,b]);linked=merge_events(a,b)
  self.assertEqual(len(linked),2);self.assertEqual(linked[0]['groupId'],linked[1]['groupId'])
  for actual,expected in zip(linked,original):
   self.assertEqual({k:v for k,v in actual.items() if k!='groupId'},expected)
  self.assertEqual([a,b],original)
 def test_midnight_times_remain_independent(self):
  linked=merge_events(event(time='23:00'),event('b',time='23:30',minutes=120))
  self.assertEqual([(e['time'],e['minutes']) for e in linked],[('23:00',60),('23:30',120)])
 def test_long_contents_are_not_combined_or_truncated(self):
  a=event(title='x'*200,notes='a'*10000);b=event('b',title='y'*200,notes='b'*10000,time='23:00',minutes=1440)
  linked=merge_events(a,b);self.assertEqual([e['title'] for e in linked],[a['title'],b['title']]);self.assertEqual([e['notes'] for e in linked],[a['notes'],b['notes']])
 def test_same_entry_or_incompatible_rejected(self):
  for b in [event(),event('b',task=True),event('b',repeat='weekly'),event('b',seriesId='parent'),event('b',date='2026-10-29'),event('b',allDay=True),event('b',groupId='existing')]:
   with self.assertRaises(ValueError):merge_events(event(),b)
 def test_all_day_and_identical_titles_stay_separate(self):
  linked=merge_events(event(title='Same',allDay=True),event('b',title='Same',allDay=True))
  self.assertEqual(len(linked),2);self.assertEqual({e['id'] for e in linked},{'a','b'});self.assertTrue(all(e['allDay'] for e in linked))

class LayoutTests(unittest.TestCase):
 def rows(self,*events):return instances(list(events),dt.date(2026,10,28),1)
 def test_ten_simultaneous_events(self):
  rows=self.rows(*(event(str(n)) for n in range(10)))
  self.assertEqual({r['lane'] for r in rows},set(range(10)));self.assertTrue(all(r['lanes']==10 and r['laneSpan']==1 and r['conflict'] for r in rows))
 def test_short_nonoverlaps_get_visual_lanes_without_conflict(self):
  rows=self.rows(event(minutes=5),event('b',time='09:05',minutes=5))
  self.assertEqual([r['lanes'] for r in rows],[2,2]);self.assertFalse(any(r['conflict'] for r in rows))
 def test_adjacent_long_events_full_width(self):
  rows=self.rows(event(),event('b',time='10:00'));self.assertTrue(all(r['lanes']==1 and not r['conflict'] for r in rows))
 def test_expansion_does_not_cover_other_lanes(self):
  rows=self.rows(event(minutes=180),event('b',minutes=30),event('c',minutes=30),event('d',time='10:00'))
  d=next(r for r in rows if r['id']=='d');self.assertEqual(d['laneSpan'],2)
  for a in rows:
   for b in rows:
    if a is not b and a['start']<b['layoutEnd'] and b['start']<a['layoutEnd']:
     self.assertTrue(a['lane']+a['laneSpan']<=b['lane'] or b['lane']+b['laneSpan']<=a['lane'])
 def test_carry_in_conflicts(self):
  rows=self.rows(event(date='2026-10-27',time='23:30',minutes=90),event('b',time='00:30'))
  self.assertTrue(all(r['conflict'] for r in rows));self.assertTrue(rows[0]['carry'])

 def test_randomized_layout_against_overlap_oracle(self):
  import random
  rng=random.Random(310)
  for _ in range(80):
   entries=[]
   for n in range(30):
    minute=rng.randrange(0,1400)
    entries.append(event(str(n),time=f'{minute//60:02}:{minute%60:02}',minutes=rng.randrange(5,120)))
   rows=self.rows(*entries)
   for a in rows:
    self.assertEqual(a['conflict'],any(a is not b and a['start']<b['end'] and b['start']<a['end'] for b in rows))
    for b in rows:
     if a is not b and a['start']<b['layoutEnd'] and b['start']<a['layoutEnd']:
      self.assertTrue(a['lane']+a['laneSpan']<=b['lane'] or b['lane']+b['laneSpan']<=a['lane'])

class NestedLayoutTests(unittest.TestCase):
 def rows(self,*events,category=-1):return {e['id']:e for e in instances(list(events),dt.date(2026,10,28),1,category=category)}
 def school(self):return event('school',time='07:00',minutes=420,groupId='school-day'),event('exam',time='09:00',minutes=60,groupId='school-day')
 def test_school_and_exam_use_one_lane_without_conflict(self):
  school,exam=self.school();rows=self.rows(school,exam)
  self.assertTrue(rows['school']['hasNested']);self.assertTrue(rows['exam']['nested'])
  self.assertEqual(rows['exam']['parentId'],'school');self.assertEqual(rows['exam']['parentTitle'],'school')
  self.assertTrue(all(v['lanes']==1 and not v['conflict'] for v in rows.values()))
  self.assertEqual((rows['exam']['start'],rows['exam']['end']),(540,600))
 def test_unrelated_booking_still_conflicts(self):
  school,exam=self.school();rows=self.rows(school,exam,event('external',time='09:30'))
  self.assertTrue(all(v['conflict'] for v in rows.values()));self.assertEqual(rows['school']['lanes'],2)
  self.assertEqual(rows['exam']['lane'],rows['school']['lane']);self.assertNotEqual(rows['exam']['lane'],rows['external']['lane'])
 def test_external_event_only_overlapping_parent_does_not_flag_child(self):
  school,exam=self.school();rows=self.rows(school,exam,event('external',time='12:00'))
  self.assertTrue(rows['school']['conflict']);self.assertTrue(rows['external']['conflict']);self.assertFalse(rows['exam']['conflict'])
 def test_partial_link_is_not_falsely_nested(self):
  school,exam=self.school();exam.update(time='13:30',minutes=120);rows=self.rows(school,exam)
  self.assertFalse(any(v['nested'] or v['hasNested'] or v['conflict'] for v in rows.values()))
  self.assertTrue(all(v['lanes']==2 for v in rows.values()))
 def test_filtered_out_parent_does_not_leave_child_inset(self):
  school,exam=self.school();exam['category']=1;rows=self.rows(school,exam,category=1)
  self.assertEqual(set(rows),{'exam'});self.assertFalse(rows['exam']['nested']);self.assertEqual(rows['exam']['lanes'],1)
 def test_short_parent_falls_back_to_readable_separate_cards(self):
  school,exam=self.school();school.update(minutes=80);exam.update(time='07:30',minutes=30)
  rows=self.rows(school,exam)
  self.assertFalse(any(v['nested'] or v['hasNested'] for v in rows.values()))
  self.assertFalse(any(v['conflict'] for v in rows.values()))
 def test_carry_segments_can_nest(self):
  school=event('school',date='2026-10-27',time='23:00',minutes=300,groupId='overnight')
  exam=event('exam',time='01:00',minutes=60,groupId='overnight');rows=self.rows(school,exam)
  self.assertTrue(rows['school']['carry']);self.assertTrue(rows['exam']['nested']);self.assertFalse(any(v['conflict'] for v in rows.values()))
 def test_randomized_link_conflicts_match_independent_oracle(self):
  import random
  rng=random.Random(83)
  for _ in range(60):
   entries=[]
   for n in range(40):
    minute=rng.randrange(100,1200)
    entries.append(event(str(n),time=f'{minute//60:02}:{minute%60:02}',minutes=rng.randrange(5,160),groupId='group-'+str(n//2)))
   rows=list(self.rows(*entries).values())
   for a in rows:
    expected=any(a is not b and a['event']['groupId']!=b['event']['groupId'] and a['start']<b['end'] and b['start']<a['end'] for b in rows)
    self.assertEqual(a['conflict'],expected)

class OccurrenceMergeTests(unittest.TestCase):
 def test_link_keeps_occurrence_commands_for_transaction(self):
  from logic import occurrence_draft
  a=occurrence_draft(event(repeat='weekly',weekdays=[2]),'2026-10-28')
  b=occurrence_draft(event('b',repeat='daily'),'2026-10-28')
  m=merge_events(a,b)
  self.assertEqual(len(m),2);self.assertTrue(all(e['repeat']=='none' and e['exceptions']=={} for e in m))
  self.assertEqual([e['occurrenceOf'] for e in m],['a','b'])
  self.assertFalse(any('weekdays' in e for e in m))
  with self.assertRaises(ValueError):merge_events(a,dict(a,id='different-draft-id'))
