import copy,datetime as dt,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from logic import *
from store import Store,ConflictError

def event(**kw):
    e=dict(id='a',title='Termin',date='2026-10-28',time='09:00',minutes=60,allDay=False,task=False,done=False,repeat='none',until='',category=0,location='',notes='')
    e.update(kw);return e
class PlannerTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store(pathlib.Path(self.temp.name)/'calendar.sqlite')
    def tearDown(self):self.temp.cleanup()
    def test_parallel_different_records(self):
        base=[event(),event(id='b')];self.store.merge(base,[])
        first=copy.deepcopy(base);first[0]['title']='App';self.store.merge(first,base)
        second=copy.deepcopy(base);second[1]['title']='Widget';_,result=self.store.merge(second,base)
        self.assertEqual({e['title'] for e in result},{'App','Widget'})
    def test_parallel_same_record_rejected(self):
        base=[event()];self.store.merge(base,[]);self.store.merge([event(title='Andere App')],base)
        with self.assertRaises(ConflictError):self.store.merge([event(title='Veraltetes Formular')],base)
        self.assertEqual(self.store.read()[0]['title'],'Andere App')
    def test_undo_keeps_later_additions(self):
        base=[event()];self.store.merge(base,[]);before,after=self.store.merge([],base)
        self.store.merge([event(id='b',title='Später')],[]);self.store.patch(before,after)
        self.assertEqual({e['id'] for e in self.store.read()},{'a','b'})
    def test_undo_rejects_newer_edit(self):
        self.store.merge([event()],[]);before,after=self.store.merge([event(title='Neu')],[event()]);self.store.merge([event(title='Noch neuer')],after)
        with self.assertRaises(ConflictError):self.store.patch(before,after)
    def test_individual_series_edit(self):
        base=[event(repeat='weekly')];self.store.merge(base,[])
        single=event(id='single',date='2026-11-05',repeat='none',occurrenceOf='a',occurrenceDate='2026-11-04',originHash=fingerprint(base[0]))
        before,after=self.store.merge(base+[single],base,allow_occurrences=True)
        parent=next(e for e in after if e['id']=='a');child=next(e for e in after if e['id']=='single')
        self.assertFalse(occurs(parent,parse('2026-11-04')));self.assertTrue(occurs(parent,parse('2026-11-11')))
        self.assertEqual(child['seriesId'],'a');self.assertNotIn('occurrenceOf',child)
        self.store.patch(before,after);self.assertEqual(self.store.read(),base)
    def test_stale_series_draft_rejected(self):
        base=[event(repeat='weekly')];self.store.merge(base,[]);self.store.merge([dict(base[0],title='Neue Serie')],base)
        single=event(id='single',occurrenceOf='a',occurrenceDate=base[0]['date'],originHash=fingerprint(base[0]))
        with self.assertRaises(ConflictError):self.store.merge(base+[single],base,allow_occurrences=True)
    def test_midnight_segments_and_conflict(self):
        a=event(date='2026-10-27',time='23:30',minutes=120);b=event(id='b',time='00:30',minutes=30)
        rows=instances([a,b],parse('2026-10-28'),1)
        self.assertEqual(len(rows),2);carry=next(e for e in rows if e['id']=='a')
        self.assertEqual(carry['occurrenceDate'],'2026-10-27');self.assertEqual(carry['segmentMinutes'],90);self.assertTrue(all(e['conflict'] for e in rows))
    def test_adjacent_events_do_not_conflict(self):
        rows=instances([event(),event(id='b',time='10:00')],parse('2026-10-28'),1);self.assertFalse(any(v['conflict'] for v in rows))
    def test_free_slot_uses_duration(self):
        rows=free_slots([event(time='09:00',minutes=90)],parse('2028-01-03'),60)
        self.assertEqual(rows[0]['time'],'09:00')
        rows=free_slots([event(date='2028-01-03',time='09:00',minutes=90)],parse('2028-01-03'),60)
        self.assertEqual(rows[0]['time'],'10:30')
    def test_all_day_blocks_planning(self):
        self.assertEqual(free_slots([event(date='2028-01-03',allDay=True)],parse('2028-01-03'),30),[])
    def test_cross_midnight_blocks_morning(self):
        rows=free_slots([event(date='2028-01-02',time='23:00',minutes=720)],parse('2028-01-03'),60)
        self.assertEqual(rows[0]['time'],'11:00')
    def test_month_end_leap_and_exceptions(self):
        e=event(date='2024-02-29',repeat='yearly',exceptions={'2028-02-29':{'cancelled':True}})
        self.assertEqual(next_occurrence(e,parse('2026-10-28')),parse('2032-02-29'))
        self.assertEqual(next_occurrence(event(date='2026-01-31',repeat='monthly'),parse('2026-02-01')),parse('2026-03-31'))
    def test_search_across_years_and_accents(self):
        rows=search([event(date='2032-01-01',title='Müller Zahnarzt')],'mull zah',parse('2026-10-28'));self.assertEqual(rows[0]['date'],'2032-01-01')
    def test_relative_search_series(self):
        rows=search([event(repeat='daily',title='Zahnarzt')],'morgen zah',parse('2026-10-28'));self.assertEqual(rows[0]['date'],'2026-10-29')
    def test_ics_exception_and_line_folding(self):
        text=export_ics([event(title='Überraschung '*16,repeat='weekly',exceptions={'2026-11-04':{'cancelled':True}})])
        self.assertIn('EXDATE:20261104T090000',text);self.assertTrue(all(len(line.encode())<=75 for line in text.split('\r\n')))
    def test_invalid_input_never_overwrites(self):
        self.store.merge([event()],[])
        with self.assertRaises(ValueError):self.store.merge([event(minutes=-1)],[event()])
        self.assertEqual(self.store.read(),[event()])
    def test_preserves_unknown_optional_fields(self):
        base=[event(reminder=30,custom={'a':1})];self.store.merge(base,[]);_,result=self.store.merge([dict(base[0],title='Neu')],base);self.assertEqual(result[0]['custom'],{'a':1})
    def test_no_tasks_in_ics(self):self.assertNotIn('BEGIN:VEVENT',export_ics([event(task=True)]))
if __name__=='__main__':unittest.main(verbosity=2)
