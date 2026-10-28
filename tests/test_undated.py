import pathlib,sys,datetime as dt,tempfile,unittest,copy,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from logic import *
from store import Store

def task(**kw):
 e=dict(id='undated',title='Konzept ausarbeiten',date='',time='',minutes=45,allDay=False,task=True,done=False,repeat='none',until='',category=1,location='',notes='Nächster Schritt',reminder=-1,exceptions={});e.update(kw);return e
class UndatedTest(unittest.TestCase):
 def test_valid_undated(self):self.assertEqual(validate([task()])[0]['date'],'')
 def test_date_still_required_for_event(self):
  with self.assertRaises(ValueError):validate([task(task=False)])
 def test_no_repeat_or_reminder(self):
  for change in [dict(repeat='weekly'),dict(reminder=10),dict(allDay=True),dict(until='2027-01-01'),dict(exceptions={'2026-10-28':{'cancelled':True}})]:
   with self.subTest(change=change),self.assertRaises(ValueError):validate([task(**change)])
 def test_not_on_timeline_or_busy(self):
  date=parse('2028-01-03');self.assertEqual(instances([task()],date,7),[]);self.assertIsNone(next_occurrence(task(),date));self.assertEqual(free_slots([task()],date,45)[0]['time'],'09:00')
 def test_search_and_filters(self):
  result=search([task()],'kon',parse('2026-10-28'),'open');self.assertTrue(result[0]['unscheduled']);self.assertEqual(result[0]['date'],'')
  self.assertEqual(search([task(done=True)],'',parse('2026-10-28'),'open'),[]);self.assertEqual(len(search([task(done=True)],'',parse('2026-10-28'),'done')),1)
 def test_json_roundtrip_and_undo_planning(self):
  with tempfile.TemporaryDirectory() as d:
   store=Store(pathlib.Path(d)/'calendar.sqlite');base=[task()];store.merge(base,[])
   self.assertEqual(validate(json.loads(json.dumps(store.read()))),base)
   before,after=store.merge([task(date='2028-01-03',time='09:00')],base)
   self.assertEqual(len(instances(after,parse('2028-01-03'),1)),1)
   store.patch(before,after);self.assertTrue(is_undated(store.read()[0]))
 def test_existing_dated_tasks_unchanged(self):
  dated=task(id='dated',date='2027-03-01',time='10:00',reminder=10);self.assertEqual(validate([task(),dated])[1],dated)
 def test_ics_omits_undated_tasks(self):self.assertNotIn('BEGIN:VEVENT',export_ics([task()]))
if __name__=='__main__':unittest.main(verbosity=2)
