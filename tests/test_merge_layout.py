import copy,datetime as dt,json,pathlib,tempfile,unittest
from logic import merge_events,instances,new_event,validate

def event(ident='a',**kw):
 e=new_event(dt.date(2026,10,28));e.update(id=ident,title=ident,time='09:00',minutes=60);e.update(kw);return e

class MergeTests(unittest.TestCase):
 def test_union_preserves_content_and_source(self):
  a=event(notes='First',location='Office');b=event('b',time='09:30',notes='Second',location='Online',reminder=60)
  original=copy.deepcopy([a,b]);merged=merge_events(a,b)
  self.assertEqual(merged['minutes'],90);self.assertEqual(merged['title'],'a / b')
  self.assertEqual(merged['notes'],'First\n\nSecond');self.assertEqual(merged['location'],'Office · Online')
  self.assertEqual(merged['id'],'a');self.assertEqual(merged['reminder'],60);self.assertEqual([a,b],original)
 def test_midnight_union(self):
  self.assertEqual(merge_events(event(time='23:00'),event('b',time='23:30',minutes=120))['minutes'],150)
 def test_limits_reject_without_truncating(self):
  for b in [event('b',title='x'*200),event('b',time='23:00',minutes=1440)]:
   with self.assertRaises(ValueError):merge_events(event(),b)
 def test_same_entry_or_incompatible_rejected(self):
  for b in [event(),event('b',task=True),event('b',repeat='weekly'),event('b',seriesId='parent'),event('b',date='2026-10-29'),event('b',allDay=True)]:
   with self.assertRaises(ValueError):merge_events(event(),b)
 def test_all_day_and_duplicate_content(self):
  a=event(title='Same',notes='Same',allDay=True);b=event('b',title='Same',notes='Same',allDay=True)
  m=merge_events(a,b);self.assertEqual(m['title'],'Same');self.assertEqual(m['notes'],'Same');self.assertTrue(m['allDay'])

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

class OccurrenceMergeTests(unittest.TestCase):
 def test_pure_merge_drops_pending_commands(self):
  from logic import occurrence_draft
  a=occurrence_draft(event(repeat='weekly',weekdays=[2]),'2026-10-28')
  b=occurrence_draft(event('b',repeat='daily'),'2026-10-28')
  m=merge_events(a,b)
  self.assertEqual(m['repeat'],'none');self.assertEqual(m['exceptions'],{})
  self.assertFalse(any(k in m for k in ('occurrenceOf','occurrenceDate','originHash','weekdays')))
  with self.assertRaises(ValueError):merge_events(a,dict(a,id='different-draft-id'))
