"""Post-0.3.6 audit regressions, using synthetic records only."""
import datetime as dt
import unittest
from unittest.mock import patch
from logic import new_event,search,free_slots,slot_available,next_occurrence,representative,instances

class AuditTests(unittest.TestCase):
 def event(self,**kw):
  e=new_event(dt.date(2026,10,7));e.update(title='Weekly',repeat='weekly');e.update(kw);return e
 def test_exact_date_does_not_return_cancelled_occurrence(self):
  e=self.event(exceptions={'2026-10-07':{'cancelled':True}})
  for q in ['2026-10-07','7.10.2026','7.10']:
   self.assertEqual(search([e],q,dt.date(2026,10,28)),[])
 def test_exact_date_targets_the_occurrence(self):
  e=self.event()
  for q in ['2026-11-04','4.11.2026','4.11']:
   self.assertEqual(search([e],q,dt.date(2026,10,28))[0]['date'],'2026-11-04')
 def test_date_search_excludes_undated_title_matches(self):
  e=self.event(task=True,date='',time='',repeat='none',reminder=-1,title='tomorrow 2026-10-28')
  for q in ['tomorrow','2026-10-28']:self.assertEqual(search([e],q,dt.date(2026,10,28)),[])
  self.assertEqual(len(search([e],'2026',dt.date(2026,10,28))),1)
 def test_started_minute_is_not_available(self):
  class Now(dt.datetime):
   @classmethod
   def now(cls,tz=None):return cls(2032,1,5,9,0,59)
  with patch('logic.dt.datetime',Now):
   self.assertEqual(free_slots([],dt.date(2032,1,5),30)[0]['time'],'09:15')
   self.assertFalse(slot_available([],dt.date(2032,1,5),30,540))
   self.assertTrue(slot_available([],dt.date(2032,1,5),30,555))
 def test_exact_quarter_minute_is_still_available(self):
  class Now(dt.datetime):
   @classmethod
   def now(cls,tz=None):return cls(2032,1,5,9,15)
  with patch('logic.dt.datetime',Now):
   self.assertEqual(free_slots([],dt.date(2032,1,5),30)[0]['time'],'09:15')

 def test_recurrence_stays_in_supported_date_range(self):
  e=self.event(date='9999-12-31',weekdays=[0])
  self.assertIsNone(next_occurrence(e,dt.date(2026,10,28)))
  self.assertIsNone(representative(e,dt.date(2026,10,28)))
  self.assertEqual(search([e],'Weekly',dt.date(2026,10,28)),[])
  e=self.event(date='9999-12-31',repeat='none',time='23:30',minutes=120)
  self.assertEqual(len(instances([e],dt.date(9999,12,31),7)),1)
