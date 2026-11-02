"""Cancellable backup preparation and one atomic import transaction off the UI thread."""
import json
import os
import stat
from pathlib import Path
import threading
from PySide6.QtCore import QObject,Signal
from logic import validate
from store import Store

class ImportCancelled(Exception):pass

class ImportJob(QObject):
    progress=Signal(int,str,bool)
    finished=Signal(object)
    def __init__(self,path,database,backup_dir,decode_files,parent=None):
        super().__init__(parent)
        self.path=Path(path);self.database=Path(database);self.backup_dir=Path(backup_dir)
        self.decode_files=decode_files
        self.cancelled=threading.Event();self.lock=threading.Lock();self.sealed=False
        self.thread=threading.Thread(target=self.run,name='calendar-import',daemon=False)
    def start(self):self.thread.start()
    def cancel(self):
        with self.lock:
            if self.sealed:return False
            self.cancelled.set();return True
    def check(self):
        if self.cancelled.is_set():raise ImportCancelled()
    def seal(self):
        # Once sealed, the only remaining operation is SQLite's atomic commit.
        with self.lock:
            self.check();self.sealed=True
        self.progress.emit(99,'Finishing import',False)
    def read_document(self):
        self.check()
        data=bytearray()
        with os.fdopen(os.open(self.path,os.O_RDONLY|os.O_NONBLOCK),'rb') as source:
            info=os.fstat(source.fileno());size=info.st_size
            if not stat.S_ISREG(info.st_mode):raise ValueError('Choose a regular local JSON backup file.')
            if size>180_000_000:raise ValueError('The backup is too large.')
            while True:
                self.check();chunk=source.read(1024*1024)
                if not chunk:break
                data.extend(chunk)
                if len(data)>180_000_000:raise ValueError('The backup is too large.')
                self.progress.emit(min(45,int(len(data)*45/max(1,size))),'Reading backup',True)
        self.check();self.progress.emit(46,'Checking entries',True)
        document=json.loads(data)
        if not isinstance(document,dict) or document.get('format')!='liquid-glass-calendar' or type(document.get('version')) is not int or document['version'] not in [1,2]:raise ValueError('Not a compatible JSON backup.')
        entries=validate(document['events']);self.check()
        if any(any(key in event for key in ['occurrenceOf','occurrenceDate','originHash']) for event in entries):raise ValueError('A backup must not contain pending series edit commands.')
        files=self.decode_files(document,entries,self.check,lambda value:self.progress.emit(50+int(value*35),'Checking attached files',True))
        self.check();return entries,files
    def run(self):
        result={}
        try:
            entries,files=self.read_document();self.check()
            store=Store(self.database,self.backup_dir);before=store.read();ids={event['id'] for event in before}
            new=[event for event in entries if event['id'] not in ids]
            self.progress.emit(88,'Saving imported entries',True)
            original,after=store.merge(before+new,before,attachment_files=files,check_cancel=self.check,before_commit=self.seal)
            result={'before':original,'after':after,'count':len(new)}
        except ImportCancelled:result={'cancelled':True}
        except Exception as error:result={'error':str(error)}
        self.finished.emit(result)
