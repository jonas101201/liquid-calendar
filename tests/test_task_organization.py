"""0.2 task organization: storage, concurrency, recurrence and backup contracts."""
import copy
import json
import pathlib
import tempfile
import unittest
from test_new_features import event
from app import Bridge
from store import Store
from logic import validate, fingerprint, parse, occurs, search, occurrence

class TaskOrganization(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store(pathlib.Path(self.temp.name)/'calendar.sqlite');self.b=Bridge(self.store,True)
    def tearDown(self):
        self.b.reload_timer.stop();self.b.reminder_timer.stop();self.temp.cleanup()
    def put(self,events):
        self.store.merge(events,self.store.read());self.b.reload()
    def task(self,ident='t',**kw):
        return event(ident,task=True,date='',time='',priority=2,project='Launch',checklist=[{'id':'step','title':'Review mockup','done':False}],**kw)
    def test_old_records_require_no_migration(self):
        old=event('old',task=True,date='',time='')
        self.put([old]);self.b.setView('tasks')
        self.assertEqual(self.store.read(),[old]);self.assertEqual(self.b.results[0]['priority'],0)
        self.assertEqual(self.b.results[0]['checklist'],[])
    def test_invalid_details(self):
        for field,values in {'priority':[-1,4,True,1.5,'high'],'project':[None,True,'x'*81,'*'],'checklist':[None,{},[{}],[{'id':'s','title':'','done':False}],[{'id':'s','title':'ok','done':1}],[{'id':'s','title':'ok','done':False}]*2,[{'id':str(i),'title':'ok','done':False} for i in range(101)]]}.items():
            for value in values:
                with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                    e=self.task();e[field]=value;validate([e])
    def test_combined_project_priority_status_and_sort(self):
        self.put([self.task('medium'),self.task('high',done=True)|{'priority':3},self.task('other')|{'project':'Other'},event('old',task=True,date='',time='')])
        self.b.setView('tasks');self.b.setTaskFilters('Launch',-1);self.b.setTaskOrder('priority')
        self.assertEqual([v['id'] for v in self.b.results],['high','medium'])
        self.b.setFilter('open',-1);self.b.setTaskFilters('Launch',2)
        self.assertEqual([v['id'] for v in self.b.results],['medium'])
        self.b.setFilter('tasks',-1);self.b.setTaskFilters('',-1)
        self.assertEqual([v['id'] for v in self.b.results],['old'])
    def test_project_counts_rename_merge_clear_undo(self):
        self.put([self.task(),self.task('done',done=True),self.task('other')|{'project':'Other'}])
        self.assertEqual(next(p for p in self.b.projects if p['name']=='Launch'),{'name':'Launch','total':2,'done':1})
        self.b.renameProject('Launch','Other');self.assertEqual(len(self.b.projects),1);self.assertEqual(self.b.projects[0]['total'],3)
        self.b.undo();self.assertEqual(len(self.b.projects),2)
        self.b.renameProject('Launch','');self.assertEqual(sum(e.get('project')=='' for e in self.store.read()),2)
        self.assertEqual(len(self.store.read()),3)
    def test_rename_rejects_stale_write_atomically(self):
        initial=[self.task(),self.task('other')];self.put(initial)
        remote=copy.deepcopy(initial);remote[1]['title']='Changed elsewhere';self.store.merge(remote,initial)
        self.b.renameProject('Launch','Renamed');self.assertTrue(self.b.error)
        self.assertEqual(sorted(self.store.read(),key=lambda e:e["id"]),sorted(remote,key=lambda e:e["id"]))
    def test_checklist_toggle_undo_and_completed_independence(self):
        source=self.task();self.put([source]);self.b.toggleChecklist('t','','step',fingerprint(source))
        self.assertTrue(self.store.read()[0]['checklist'][0]['done']);self.assertFalse(self.store.read()[0]['done'])
        self.assertEqual(occurrence(self.store.read()[0],None)['checklistDone'],1)
        self.b.undo();self.assertEqual(self.store.read(),[source])
    def test_stale_checklist_toggle_preserves_remote(self):
        source=self.task();self.put([source]);remote=copy.deepcopy(source);remote['notes']='Concurrent edit';self.store.merge([remote],[source])
        self.b.toggleChecklist('t','','step',fingerprint(source));self.assertTrue(self.b.error);self.assertEqual(self.store.read(),[remote])
    def test_repeated_checklist_is_per_occurrence(self):
        source=self.task()|{'date':'2032-01-05','time':'09:00','repeat':'weekly'};self.put([source])
        self.b.toggleChecklist('t','2032-01-12','step',fingerprint(source))
        parent=next(e for e in self.store.read() if e['id']=='t');child=next(e for e in self.store.read() if e['id']!='t')
        self.assertFalse(parent['checklist'][0]['done']);self.assertTrue(child['checklist'][0]['done']);self.assertTrue(occurs(parent,parse('2032-01-19')))
        self.assertFalse(occurs(parent,parse('2032-01-12')));self.assertEqual(child['project'],'Launch')
        self.b.undo();self.assertEqual(self.store.read(),[source])
    def test_backup_import_preserves_details(self):
        source=self.task();self.put([source]);file=pathlib.Path(self.temp.name)/'backup.json'
        self.b.exportFile(file.as_uri(),'json');self.b.commit([]);self.b.importFile(file.as_uri())
        saved=self.store.read()[0]
        for field in ['priority','project','checklist']:self.assertEqual(saved[field],source[field])
    def test_project_and_step_search_all_dates(self):
        self.put([self.task(),self.task('dated')|{'date':'2032-01-05','time':'09:00'}])
        for query in ['lau','mock']:
            self.assertEqual({v['id'] for v in search(self.store.read(),query,parse('2026-10-28'))},{'t','dated'})
    def test_schedule_preserves_details(self):
        source=self.task();self.put([source]);self.assertTrue(self.b.scheduleTask('t','','2032-01-05',600,fingerprint(source)))
        for field in ['priority','project','checklist']:self.assertEqual(self.store.read()[0][field],source[field])

    def test_project_undo_restores_selected_filter(self):
        for target in ['Renamed','']:
            self.put([self.task()]);self.b.setView('tasks');self.b.setTaskFilters('Launch',-1)
            self.b.renameProject('Launch',target);self.b.undo()
            self.assertEqual(self.b.projectFilter,'Launch');self.assertEqual(len(self.b.results),1)
    def test_project_undo_preserves_later_user_filter(self):
        self.put([self.task(),self.task('other')|{'project':'Other'}]);self.b.setView('tasks');self.b.setTaskFilters('Launch',-1)
        self.b.renameProject('Launch','Renamed');self.b.setTaskFilters('Other',-1);self.b.undo()
        self.assertEqual(self.b.projectFilter,'Other');self.assertEqual([v['id'] for v in self.b.results],['other'])
    def test_noop_project_rename_keeps_undo_context(self):
        self.put([self.task()]);self.b.setView('tasks');self.b.setTaskFilters('Launch',-1)
        self.b.renameProject('Launch','Renamed');self.b.renameProject('Renamed','Renamed');self.b.undo()
        self.assertEqual(self.b.projectFilter,'Launch');self.assertEqual(len(self.b.results),1)
    def test_project_summary_visits_each_record_once(self):
        class CountingList(list):
            visits=0
            def __iter__(self):
                for e in super().__iter__():self.visits+=1;yield e
        self.b._events=CountingList([self.task(str(i))|{'project':f'Project {i}'} for i in range(1000)])
        self.assertEqual(len(self.b.projects),1000);self.assertEqual(self.b._events.visits,1000)
    def test_project_rename_rejects_new_concurrent_members(self):
        original=self.task();self.put([original]);remote=[original,self.task('added')]
        self.store.merge(remote,[original]);self.b.renameProject('Launch','Renamed')
        self.assertIn('membership',self.b.error)
        self.assertEqual({e['project'] for e in self.store.read()},{'Launch'})
        self.b.reload();self.b.renameProject('Launch','Renamed');self.assertFalse(self.b.error)
        self.assertEqual({e['project'] for e in self.store.read()},{'Renamed'})
    def test_unicode_limits_are_code_points(self):
        source=self.task()|{'id':'🚀'*150,'title':'🚀'*200,'project':'🚀'*80,'location':'🚀'*500,'notes':'🚀'*10000,'checklist':[{'id':'🚀'*150,'title':'🚀'*200,'done':False}]}
        validate([source]);self.put([source]);self.assertEqual(self.store.read(),[source])
        for field,limit in [('id',150),('title',200),('project',80),('location',500),('notes',10000)]:
            with self.subTest(field=field),self.assertRaises(ValueError):validate([source|{field:'🚀'*(limit+1)}])
