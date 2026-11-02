"""Attachment files are copied, transactional, portable and independent of source paths."""
import base64
import sys
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from contextlib import closing
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import QCoreApplication
from app import Bridge
from logic import new_event, validate, validate_attachments, search, occurrence_draft
from store import Store, ConflictError
app=QCoreApplication.instance() or QCoreApplication([])

class Attachments(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.store=Store(self.root/'calendar.sqlite');self.bridge=Bridge(self.store,True)
        self.task=new_event(dt.date(2026,11,2));self.task.update(id='task',title='Synthetic task',task=True,date='',time='',reminder=-1)
        self.payload=b'Example attachment\x00\xff\n'
        self.file=self.root/'Prüfung 日本語.pdf';self.file.write_bytes(self.payload)
    def tearDown(self):
        self.bridge.reload_timer.stop();self.bridge.reminder_timer.stop()
        if self.bridge._attachment_cache:self.bridge._attachment_cache.cleanup()
        self.temp.cleanup()
    def stage(self,paths=None,existing=None):
        result=self.bridge.stageAttachments([p.as_uri() for p in (paths or [self.file])],json.dumps(existing or []))
        self.assertEqual(result['error'],'');return result['attachments']
    def save(self):
        self.task['attachments']=self.stage();self.assertIsNotNone(self.bridge.commit([self.task]),self.bridge.error);return self.task['attachments'][0]
    def test_copy_survives_moving_original_and_restarting(self):
        item=self.save();self.file.unlink()
        self.assertEqual(self.store.attachment_data(item['id']),self.payload)
        self.assertFalse(self.bridge._pending_attachments)
        restored=Store(self.store.path)
        self.assertEqual(restored.attachment_data(item['id']),self.payload)
        self.assertNotIn(str(self.root),json.dumps(restored.read()))
        self.assertEqual(item['name'],'Prüfung 日本語.pdf')
    def test_staging_and_cancel_never_write_or_modify_task(self):
        items=self.stage();self.assertEqual(self.store.read(),[])
        with self.store.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM planner_attachments').fetchone()[0],0)
        self.bridge.discardAttachmentDrafts(json.dumps(items));self.assertEqual(self.bridge._pending_attachments,{})
    def test_duplicate_content_is_deduplicated(self):
        other=self.root/'another-name.txt';other.write_bytes(self.payload)
        items=self.stage([self.file,other]);self.assertEqual(len(items),1)
        self.assertEqual(self.stage([other],items),items)
    def test_bad_selection_is_all_or_nothing(self):
        missing=self.root/'missing.txt'
        result=self.bridge.stageAttachments([self.file.as_uri(),missing.as_uri()],'[]')
        self.assertTrue(result['error']);self.assertEqual(self.bridge._pending_attachments,{})
        self.assertTrue(self.bridge.stageAttachments(['https://example.invalid/file'],'[]')['error'])
        self.assertTrue(self.bridge.stageAttachments([self.root.as_uri()],'[]')['error'])
        pipe=self.root/'fifo';os.mkfifo(pipe)
        self.assertTrue(self.bridge.stageAttachments([pipe.as_uri()],'[]')['error'])
    def test_oversized_file_is_rejected(self):
        with patch('app.MAX_ATTACHMENT_BYTES',4):
            self.assertTrue(self.bridge.stageAttachments([self.file.as_uri()],'[]')['error'])
        self.assertEqual(self.bridge._pending_attachments,{})
    def test_empty_file_is_supported(self):
        self.file.write_bytes(b'');item=self.save();self.assertEqual(item['size'],0)
        self.assertEqual(self.store.attachment_data(item['id']),b'')
    def test_failed_commit_keeps_pending_file_for_retry(self):
        self.task['attachments']=self.stage()
        with patch.object(self.store,'merge',side_effect=OSError('synthetic failed save')):
            self.assertIsNone(self.bridge.commit([self.task]))
        self.assertTrue(self.bridge._pending_attachments);self.assertEqual(self.store.read(),[])
        self.assertIsNotNone(self.bridge.commit([self.task]));self.assertFalse(self.bridge._pending_attachments)
    def test_concurrent_conflict_never_commits_new_file(self):
        self.bridge.commit([self.task]);base=self.store.read();remote=copy.deepcopy(base);remote[0]['title']='Remote edit';self.store.merge(remote,base)
        self.task['attachments']=self.stage();self.assertIsNone(self.bridge.commit([self.task]))
        with self.store.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM planner_attachments').fetchone()[0],0)
        self.assertEqual(self.store.read(),remote)
    def test_remove_delete_and_undo_keep_file_data(self):
        item=self.save();plain=copy.deepcopy(self.task);plain['attachments']=[]
        self.bridge.commit([plain]);self.bridge.undo();self.assertEqual(self.store.read()[0]['attachments'],[item])
        self.bridge.commit([]);self.bridge.undo();self.assertEqual(self.store.attachment_data(item['id']),self.payload)
    def test_json_backup_round_trip_into_another_database(self):
        item=self.save();backup=self.root/'backup.json';self.bridge.exportFile(backup.as_uri(),'json')
        document=json.loads(backup.read_text());self.assertEqual(document['version'],2)
        self.assertEqual(base64.b64decode(document['files'][item['id']]),self.payload)
        target=Store(self.root/'other.sqlite');other=Bridge(target,True)
        try:
            other.importFile(backup.as_uri());self.assertEqual(other.error,'')
            self.assertEqual(target.read(),self.store.read());self.assertEqual(target.attachment_data(item['id']),self.payload)
        finally:other.reload_timer.stop();other.reminder_timer.stop()
    def test_corrupt_or_incomplete_import_is_rejected_without_writes(self):
        item=self.save();document=self.bridge.backup_document(self.store.read())
        for broken in [dict(document,files={}),dict(document,files={item['id']:base64.b64encode(b'wrong').decode()}),dict(document,version=1),dict(document,files={item['id']:'not base64!'})]:
            target=Store(self.root/'invalid.sqlite');other=Bridge(target,True)
            try:
                path=self.root/'invalid.json';path.write_text(json.dumps(broken));other.importFile(path.as_uri())
                self.assertTrue(other.error);self.assertEqual(target.read(),[])
                with target.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM planner_attachments').fetchone()[0],0)
            finally:other.reload_timer.stop();other.reminder_timer.stop()
    def test_automatic_database_backup_contains_files(self):
        item=self.save();self.store._backup_date=None
        self.bridge.commit([])
        backup=next(self.store.backup_dir.glob('calendar-*.sqlite'))
        # First daily snapshot predates the initial attachment; force a new day with a separate directory.
        fresh=Store(self.store.path,self.root/'later-backups');fresh.merge([],fresh.read())
        backup=next(fresh.backup_dir.glob('calendar-*.sqlite'));self.assertTrue(Store.valid_backup(backup))
        with closing(sqlite3.connect(backup)) as c:self.assertEqual(c.execute('SELECT data FROM planner_attachments WHERE id=?',(item['id'],)).fetchone()[0],self.payload)
    def test_migrates_legacy_database_without_changing_events(self):
        path=self.root/'legacy.sqlite'
        with closing(sqlite3.connect(path)) as c:
            c.execute('CREATE TABLE state (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            c.execute('INSERT INTO state VALUES (?,?)',('events',json.dumps([self.task])));c.commit()
        legacy=Store(path);self.assertEqual(legacy.read(),[self.task])
        with legacy.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM planner_attachments').fetchone()[0],0)
    def test_missing_second_file_rolls_back_inserted_blob_and_events(self):
        items=self.stage();items.append(dict(id='b'*64,name='missing.pdf',size=1))
        self.assertIsNone(self.bridge.commit([dict(self.task,attachments=items)]));self.assertEqual(self.store.read(),[])
        with self.store.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM planner_attachments').fetchone()[0],0)
    def test_task_count_and_calendar_size_limits(self):
        items=[dict(id=f'{i:064x}',name=str(i)+'.pdf',size=10*1024*1024) for i in range(11)]
        with self.assertRaises(ValueError):validate_attachments(items)
        with self.assertRaisesRegex(ValueError,'100 MiB'):Store.attachment_refs([dict(attachments=[item]) for item in items])
    def test_save_copy_and_open_dispatch_do_not_change_original(self):
        item=self.save();target=self.root/'saved-copy.pdf'
        with patch('app.QStandardPaths.writableLocation',return_value=str(self.root)):
            from PySide6.QtCore import QUrl
            self.assertEqual(QUrl(self.bridge.attachmentSaveUrl(json.dumps(item))).toLocalFile(),str(self.root/item['name']))
        self.assertTrue(self.bridge.saveAttachment(json.dumps(item),target.as_uri()));self.assertEqual(target.read_bytes(),self.payload)
        with patch('app.QDesktopServices.openUrl',return_value=True) as opener:
            self.assertTrue(self.bridge.openAttachment(json.dumps(item)))
            opened=Path(opener.call_args.args[0].toLocalFile());self.assertEqual(opened.name,item['name']);self.assertEqual(opened.read_bytes(),self.payload)
            self.assertEqual(opened.stat().st_mode&0o777,0o600)
            opened.write_bytes(b'Changed externally')
        self.assertEqual(self.store.attachment_data(item['id']),self.payload)
    def test_missing_and_tampered_blobs_fail_without_overwriting_export(self):
        item=self.save();target=self.root/'preserved.pdf';target.write_bytes(b'keep')
        with self.store.connect() as c:c.execute('UPDATE planner_attachments SET data=? WHERE id=?',(b'bad',item['id']))
        self.assertFalse(self.bridge.saveAttachment(json.dumps(item),target.as_uri()));self.assertEqual(target.read_bytes(),b'keep')
    def test_names_are_searchable_and_series_copy_keeps_attachments(self):
        self.save();self.assertEqual([row['id'] for row in search(self.store.read(),'prüfung',dt.date(2026,11,2))],['task'])
        series=copy.deepcopy(self.task);series.update(date='2026-11-02',time='09:00',repeat='weekly')
        child=occurrence_draft(series,'2026-11-09');self.assertEqual(child['attachments'],series['attachments'])
    def test_validation_rejects_paths_sizes_duplicates_and_preserves_legacy_conversion(self):
        item=dict(id=hashlib.sha256(self.payload).hexdigest(),name='file.pdf',size=len(self.payload))
        for changed in [dict(item,name='../escape'),dict(item,name='a\\b'),dict(item,name='\x00bad'),dict(item,size=True),dict(item,size=-1),dict(item,id='X'*64)]:
            with self.assertRaises(ValueError):validate_attachments([changed])
        with self.assertRaises(ValueError):validate_attachments([item,item])
        event=new_event(dt.date(2026,11,2));event.update(title='Legacy conversion',attachments=[item])
        self.assertEqual(validate([event]),[event])
        with self.assertRaises(ValueError):self.store.merge([dict(self.task,attachments=[item])],[])
