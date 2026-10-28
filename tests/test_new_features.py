import os,sys,pathlib,tempfile,unittest,datetime as dt
os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QCoreApplication
from app import Bridge
from store import Store
from logic import *
application=QCoreApplication.instance() or QCoreApplication([])
def event(ident,**kw):
 e=dict(id=ident,title=ident,date='2032-01-05',time='09:00',minutes=60,allDay=False,task=False,done=False,repeat='none',until='',category=0,location='',notes='',reminder=-1);e.update(kw);return e
class Features(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=Store(pathlib.Path(self.temp.name)/'calendar.sqlite');self.b=Bridge(self.store,True)
 def tearDown(self):self.b.reload_timer.stop();self.b.reminder_timer.stop();self.temp.cleanup()
 def put(self,events):self.store.merge(events,self.store.read());self.b.reload()
 def test_agenda_occurrences(self):
  self.put([event('series',repeat='weekly'),event('undated',date='',time='',task=True),event('done',task=True,done=True),event('night',time='23:30',minutes=90),event('all',allDay=True)])
  self.b.selectDate('2032-01-05');self.b.setView('agenda');self.b.setAgendaDays(14);rows=self.b.agendaItems
  self.assertEqual(sum(v['id']=='series' for v in rows),2);self.assertFalse(any(v['id'] in ['undated','done'] for v in rows));self.assertTrue(any(v['carry'] and v['date']=='2032-01-06' for v in rows));self.assertTrue(any(v['allDay'] for v in rows))
 def test_combined_filters_reset_and_sort(self):
  self.put([event('Z',task=True,category=1),event('A',task=True,date='',time='',minutes=30,category=1),event('B',task=True,category=0)])
  self.b.setView('tasks');self.b.setFilter('open',1);self.b.setPlanningFilter('undated');self.assertEqual([r['id'] for r in self.b.results],['A'])
  self.b.setPlanningFilter('planned');self.assertEqual([r['id'] for r in self.b.results],['Z'])
  self.b.setPlanningFilter('all');self.b.setTaskOrder('duration');self.assertEqual([r['id'] for r in self.b.results],['A','Z'])
  self.b.setTaskOrder('planned');self.assertEqual([r['id'] for r in self.b.results],['Z','A'])
  self.b.setView('today');self.assertEqual(self.b.category,-1);self.assertEqual(self.b.kind,'all')
 def test_dates(self):
  self.assertEqual(self.b.resolveDate('15.11.2032')['date'],'2032-11-15');self.assertTrue(self.b.resolveDate('2032-02-30')['error']);self.assertTrue(self.b.resolveDate('ma')['error']);self.assertEqual(self.b.resolveDate('morgen')['date'],(dt.date.today()+dt.timedelta(days=1)).isoformat())
 def test_plan_other_day_undo_all_day(self):
  self.put([event('t',task=True,allDay=True)]);selected=self.b.selected;slots=self.b.slotsOn('t','2032-01-05','2032-01-06');self.assertEqual(self.b.selected,selected);self.assertTrue(slots)
  self.assertTrue(self.b.scheduleTask('t','2032-01-05','2032-01-06',slots[0]['minute'],fingerprint(self.store.read()[0])));self.assertFalse(self.store.read()[0]['allDay']);self.b.undo();self.assertTrue(self.store.read()[0]['allDay'])
 def test_changed_occupancy_exact_interval(self):
  t=event('t',date='',time='',task=True);self.put([t]);self.b.slotsOn('t','','2032-01-05')
  self.store.merge([t,event('new',minutes=15)],[t]);self.assertTrue(self.b.scheduleTask('t','','2032-01-05',600,fingerprint(t)))
 def test_occupied_stale_or_past_rejected(self):
  t=event('t',date='',time='',task=True);self.put([t,event('busy',time='10:00')]);self.assertFalse(self.b.scheduleTask('t','','2032-01-05',600,fingerprint(t)));self.assertEqual(next(e for e in self.store.read() if e['id']=='t')['date'],'')
  self.assertEqual(self.b.slotsOn('t','','2020-01-01'),[])
  self.assertFalse(self.b.scheduleTask('t','','2032-01-05',660,'wrong'))
 def test_availability_midnight_and_done(self):
  self.assertFalse(slot_available([event('night',date='2032-01-04',time='23:00',minutes=720)],parse('2032-01-05'),60,600))
  self.assertTrue(slot_available([event('done',task=True,done=True)],parse('2032-01-05'),60,540))
if __name__=='__main__':unittest.main()
