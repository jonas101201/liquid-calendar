"""Transactional shared storage; no writes without checking the editor's base version."""
import copy
import datetime as dt
import json
import os
import tempfile
import fcntl
from pathlib import Path
import sqlite3
from contextlib import contextmanager, closing
from logic import validate, fingerprint, validate_templates, slot_available, clean_groups

class ConflictError(ValueError):pass

class Store:
    def __init__(self,path,backup_dir=None):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.backup_dir=Path(backup_dir) if backup_dir else self.path.parent/'backups'
        self._backup_date=None
        with self.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS planner_reminders (key TEXT PRIMARY KEY, sent TEXT NOT NULL)')
        self.read()
    @contextmanager
    def connect(self):
        connection=sqlite3.connect(self.path,timeout=8)
        try:
            with connection:
                yield connection
        finally:
            connection.close()
    @staticmethod
    def read_conn(c):
        row=c.execute('SELECT value FROM state WHERE key=?',('events',)).fetchone()
        return validate(json.loads(row[0])) if row else []
    def read(self):
        with self.connect() as c:return self.read_conn(c)
    @classmethod
    def valid_backup(cls,path):
        if not path.is_file() or path.stat().st_size==0:return False
        try:
            with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,timeout=8)) as connection:
                if connection.execute('PRAGMA quick_check').fetchall()!=[('ok',)]:return False
                cls.read_conn(connection);cls.templates_conn(connection)
            return True
        except (OSError,ValueError,sqlite3.Error):return False
    def backup(self):
        today=dt.date.today()
        if self._backup_date==today:return
        self.backup_dir.mkdir(parents=True,exist_ok=True)
        target=self.backup_dir/('calendar-'+today.strftime('%Y%m%d')+'.sqlite')
        # Serialize first-of-day creation across the native app and shared clients.
        with (self.backup_dir/'.backup.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if not self.valid_backup(target):
                descriptor,name=tempfile.mkstemp(prefix='.'+target.stem+'-',suffix='.sqlite',dir=self.backup_dir)
                os.close(descriptor);temporary=Path(name)
                try:
                    with self.connect() as source,closing(sqlite3.connect(temporary)) as destination:source.backup(destination)
                    if not self.valid_backup(temporary):raise OSError('The automatic backup did not pass validation.')
                    with temporary.open('rb') as saved:os.fsync(saved.fileno())
                    os.replace(temporary,target)
                    descriptor=os.open(self.backup_dir,os.O_RDONLY|os.O_DIRECTORY)
                    try:os.fsync(descriptor)
                    finally:os.close(descriptor)
                finally:temporary.unlink(missing_ok=True)
            self._backup_date=today
            for old in sorted(self.backup_dir.glob('calendar-*.sqlite'))[:-14]:old.unlink()
    def merge(self,desired,base,allow_occurrences=False,project_name=None,planning_slot=None,unchanged_sources=None):
        validate(desired);validate(base);self.backup()
        desired_map={e['id']:copy.deepcopy(e) for e in desired};base_map={e['id']:e for e in base}
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            before=self.read_conn(c);remote={e['id']:e for e in before}
            if unchanged_sources and any(remote.get(ident)!=source for ident,source in unchanged_sources.items()):
                raise ConflictError("A merge source has changed. Reopen the events before merging.")
            if planning_slot is not None and not slot_available(before,*planning_slot):
                raise ConflictError("This time slot is no longer available. Search again.")
            if project_name is not None:
                members=lambda records:{i for i,e in records.items() if e['task'] and e.get('project','')==project_name}
                if members(base_map)!=members(remote):raise ConflictError("Project membership has changed. Refresh and reopen the project; no tasks were renamed.")
            for ident in base_map.keys()|desired_map.keys():
                old=base_map.get(ident);new=desired_map.get(ident)
                if old==new:continue
                current=remote.get(ident)
                if current!=old and current!=new:raise ConflictError("This entry has changed. Reopen it; your edits have not been saved.")
                if new is None:
                    children=[i for i,item in remote.items() if item.get('seriesId')==ident]
                    for child in children:
                        if remote[child]!=base_map.get(child):raise ConflictError("An occurrence of this series has changed. Reopen the series.")
                    for child in children:remote.pop(child,None)
                    remote.pop(ident,None)
                else:
                    if new.get('occurrenceOf'):
                        if not allow_occurrences:raise ValueError("A backup must not contain pending series edit commands.")
                        source=remote.get(new['occurrenceOf'])
                        if not source or fingerprint(source)!=new.get('originHash'):raise ConflictError("The series has changed. Reopen this occurrence.")
                        source=copy.deepcopy(source)
                        source.setdefault('exceptions',{})[new['occurrenceDate']]={'cancelled':True}
                        remote[source['id']]=source
                        new['seriesId']=new.pop('occurrenceOf');new['originalDate']=new.pop('occurrenceDate');new.pop('originHash',None)
                    remote[ident]=new
            after=clean_groups(list(remote.values()));validate(after)
            c.execute('INSERT OR REPLACE INTO state VALUES (?,?)',('events',json.dumps(after,ensure_ascii=False)))
        return before,after
    def patch(self,before,after):
        """Undo only this mutation. Reject overwriting a newer edit of the same record."""
        before_map={e['id']:e for e in before};after_map={e['id']:e for e in after}
        changes={i for i in before_map.keys()|after_map.keys() if before_map.get(i)!=after_map.get(i)}
        current=self.read();result={e['id']:e for e in current}
        for i in changes:
            if result.get(i)!=after_map.get(i):raise ConflictError("This entry has changed since your last edit. Undo was cancelled to preserve the newer changes.")
            if i in before_map:result[i]=copy.deepcopy(before_map[i])
            else:result.pop(i,None)
        return self.merge(list(result.values()),current)
    def settings(self):
        with self.connect() as c:
            row=c.execute('SELECT value FROM state WHERE key=?',('planner-settings',)).fetchone()
        return json.loads(row[0]) if row else {'reminders':True,'theme':'dark'}
    @staticmethod
    def templates_conn(c):
        row=c.execute('SELECT value FROM state WHERE key=?',('event-templates',)).fetchone()
        return validate_templates(json.loads(row[0])) if row else []
    def templates(self):
        with self.connect() as c:return self.templates_conn(c)
    def write_template(self,template,base=None):
        if template is not None:validate_templates([template])
        if base is not None:validate_templates([base])
        ident=template['id'] if template else base['id']
        if base and base['id']!=ident:raise ValueError('Template identity changed.')
        self.backup()
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE');items=self.templates_conn(c)
            current=next((t for t in items if t['id']==ident),None)
            if current!=base:raise ConflictError('This template has changed. Reopen the template library.')
            items=[t for t in items if t['id']!=ident]
            if template is not None:items.append(copy.deepcopy(template))
            validate_templates(items)
            c.execute('INSERT OR REPLACE INTO state VALUES (?,?)',('event-templates',json.dumps(items,ensure_ascii=False)))
        return items
    def set_settings(self,data):
        with self.connect() as c:c.execute('INSERT OR REPLACE INTO state VALUES (?,?)',('planner-settings',json.dumps(data)))
    def preferences(self,opacity,accent):
        with self.connect() as c:c.execute('INSERT OR REPLACE INTO state VALUES (?,?)',('preferences',json.dumps({'opacity':opacity,'accent':accent})))
    def notified(self,key):
        with self.connect() as c:return bool(c.execute('SELECT 1 FROM planner_reminders WHERE key=?',(key,)).fetchone())
    def mark_notified(self,key):
        with self.connect() as c:
            c.execute('INSERT OR REPLACE INTO planner_reminders VALUES (?,?)',(key,dt.datetime.now().isoformat()))
            c.execute('DELETE FROM planner_reminders WHERE sent < ?',((dt.datetime.now()-dt.timedelta(days=45)).isoformat(),))
