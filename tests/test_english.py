import os,sys,pathlib,datetime as dt,unittest,tempfile,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from logic import *
from store import Store
TODAY=dt.date(2026,10,28)
def entry(ident,date,**kw):
 e=dict(id=ident,title='Meeting',date=date,time='10:00',minutes=30,allDay=False,task=False,done=False,repeat='none',until='',category=1,location='Büro 東京',notes='Préparation العربية',reminder=10);e.update(kw);return e
class English(unittest.TestCase):
 def test_day_month_names(self):
  self.assertEqual(WEEKDAYS[0],'Monday');self.assertEqual(MONTHS[9],'October');self.assertEqual(CATEGORIES,['Personal','Work','Important','Leisure'])
 def test_english_hints(self):
  for query,date in [('today','2026-10-28'),('tomorrow','2026-10-29'),('day after tomorrow','2026-10-30'),('wed','2026-10-28'),('nov','2026-11-01')]:
   self.assertEqual(date_hints(query,TODAY)[0]['date'],date)
  self.assertEqual(date_hints('morgen',TODAY)[0]['label'],'Tomorrow')
  self.assertEqual(date_hints('Okt',TODAY)[0]['label'],'October')
 def test_exact_relative_search(self):
  rows=[entry('today','2026-10-28'),entry('tomorrow','2026-10-29'),entry('after','2026-10-30'),entry('repeat','2026-10-01',repeat='daily')]
  for query,ident in [('today','today'),('tomorrow','tomorrow'),('day after tomorrow','after'),('morgen','tomorrow')]:
   self.assertEqual({r['id'] for r in search(rows,query,TODAY)}, {ident,'repeat'})
 def test_english_partial_search(self):
  self.assertEqual(search([entry('a','2032-11-10')],'nov',TODAY)[0]['date'],'2032-11-10')
  self.assertEqual(search([entry('a','2026-10-28')],'wed',TODAY)[0]['id'],'a')
 def test_validation_english(self):
  with self.assertRaisesRegex(ValueError,'Duration must be'):validate([entry('a','2026-10-28',minutes=0)])
 def test_data_unchanged(self):
  source=entry('a','2026-10-28',title='Besprechung mañana 日本語')
  with tempfile.TemporaryDirectory() as d:
   store=Store(pathlib.Path(d)/'calendar.sqlite');store.merge([source],[]);search(store.read(),'wed',TODAY);self.assertEqual(store.read(),[source]);self.assertEqual(json.loads(json.dumps(source,ensure_ascii=False)),source)
if __name__=='__main__':unittest.main()
