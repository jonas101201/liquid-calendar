"""Transactional shared storage; no writes without checking the editor's base version."""
import copy
import datetime as dt
import json
from pathlib import Path
import sqlite3
from logic import validate, fingerprint

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
    def connect(self):return sqlite3.connect(self.path,timeout=8)
    @staticmethod
    def read_conn(c):
        row=c.execute('SELECT value FROM state WHERE key=?',('events',)).fetchone()
        return validate(json.loads(row[0])) if row else []
    def read(self):
        with self.connect() as c:return self.read_conn(c)
    def backup(self):
        if self._backup_date==dt.date.today():return
        self.backup_dir.mkdir(parents=True,exist_ok=True)
        target=self.backup_dir/('calendar-'+dt.date.today().strftime('%Y%m%d')+'.sqlite')
        if not target.exists():
            with self.connect() as source,sqlite3.connect(target) as dest:source.backup(dest)
        self._backup_date=dt.date.today()
        for old in sorted(self.backup_dir.glob('calendar-*.sqlite'))[:-14]:old.unlink()
    def merge(self,desired,base,allow_occurrences=False):
        validate(desired);validate(base);self.backup()
        desired_map={e['id']:copy.deepcopy(e) for e in desired};base_map={e['id']:e for e in base}
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            before=self.read_conn(c);remote={e['id']:e for e in before}
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
            after=list(remote.values());validate(after)
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
