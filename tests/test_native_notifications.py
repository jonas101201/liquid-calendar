"""Real child processes and Qt timers; no desktop notifications or personal data."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QCoreApplication,QTimer
from app import NativeNotifications
application=QCoreApplication.instance() or QCoreApplication([])

class NativeNotificationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.sender=self.root/'notify-send';self.output=self.root/'args.json'
        self.backend=NativeNotifications(timeout_ms=1500);self.results=[]
        self.backend.finished.connect(lambda *args:self.results.append(args))
        self.env=patch.dict(os.environ,{'PATH':str(self.root)+os.pathsep+os.environ.get('PATH','')});self.env.start()
    def tearDown(self):
        self.backend.shutdown();application.processEvents();self.env.stop();self.temp.cleanup()
    def script(self,body):
        self.sender.write_text('#!'+sys.executable+'\n'+body);self.sender.chmod(0o755)
    def wait(self,condition,timeout=3):
        end=time.monotonic()+timeout
        while not condition() and time.monotonic()<end:application.processEvents();time.sleep(.002)
        self.assertTrue(condition())
    def test_option_like_and_unicode_titles_are_literal_arguments(self):
        self.script('import sys,json\nfrom pathlib import Path\nPath('+repr(str(self.output))+').write_text(json.dumps(sys.argv[1:]))\n')
        self.backend.notify('key','--help','09:00 · Büro 東京');self.wait(lambda:len(self.results)==1)
        args=json.loads(self.output.read_text());self.assertEqual(args[-3:],['--','--help','09:00 · Büro 東京'])
        self.assertEqual(self.results,[('key',True,'')])
    def test_slow_child_keeps_event_loop_responsive_and_serializes_queue(self):
        self.script('import time\ntime.sleep(.35)\n')
        ticks=[];start=time.monotonic();QTimer.singleShot(20,lambda:ticks.append(time.monotonic()-start))
        self.backend.notify('one','First','Body');self.backend.notify('two','Second','Body')
        self.wait(lambda:bool(ticks));self.assertLess(ticks[0],.25);self.assertEqual(self.results,[])
        self.wait(lambda:len(self.results)==2);self.assertEqual([r[0] for r in self.results],['one','two'])
        self.assertTrue(all(r[1] for r in self.results))
    def test_nonzero_exit_is_failure_and_queue_continues(self):
        self.script('import sys\nsys.exit(3 if sys.argv[-1]=="fail" else 0)\n')
        self.backend.notify('bad','Title','fail');self.backend.notify('good','Title','ok')
        self.wait(lambda:len(self.results)==2)
        self.assertFalse(self.results[0][1]);self.assertIn('3',self.results[0][2]);self.assertTrue(self.results[1][1])
    def test_missing_executable_is_reported_once(self):
        with patch.dict(os.environ,{'PATH':str(self.root)}):
            self.backend.notify('missing','Title','Body');self.wait(lambda:len(self.results)==1)
        application.processEvents();self.assertEqual(len(self.results),1);self.assertFalse(self.results[0][1])
    def test_timeout_reports_once_and_next_notification_runs(self):
        self.backend.timeout_ms=150
        self.script('import sys,time\nif sys.argv[-1]=="slow":time.sleep(2)\n')
        self.backend.notify('slow','Title','slow');self.backend.notify('next','Title','fast')
        self.wait(lambda:len(self.results)==2)
        self.assertEqual(self.results[0],('slow',False,'Notification delivery timed out.'))
        self.assertEqual(self.results[1],('next',True,''));application.processEvents();self.assertEqual(len(self.results),2)
    def test_cancel_discards_queue_and_allows_new_delivery(self):
        self.script('import sys,time\nif sys.argv[-1]=="slow":time.sleep(5)\n')
        self.backend.notify('active','Title','slow');self.backend.notify('queued','Title','slow')
        self.assertEqual(set(self.backend.cancel()),{'active','queued'})
        self.backend.notify('new','Title','fast');self.wait(lambda:len(self.results)==1)
        self.assertEqual(self.results,[('new',True,'')])
    def test_shutdown_kills_active_and_discards_queued_jobs_without_success(self):
        self.script('import time\ntime.sleep(5)\n')
        self.backend.notify('active','Title','Body');self.backend.notify('queued','Title','Body')
        self.backend.shutdown();application.processEvents()
        self.assertEqual(self.results,[]);self.assertIsNone(self.backend.active);self.assertFalse(self.backend.queue)

if __name__=='__main__':unittest.main()
