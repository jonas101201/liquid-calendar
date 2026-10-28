"""Distribution checks for the independently installed companion widget."""
from pathlib import Path
import tempfile
import unittest

from scripts.sync_widget_sources import ROOT, SHARED_FILES, check_shared, sync_shared


class SharedSourceTests(unittest.TestCase):
    def test_distributed_widget_copies_are_current(self):
        check_shared(ROOT)

    def test_drift_is_rejected_and_sync_preserves_widget_only_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'qml'
            widget = root / 'companion-widget/contents/ui'
            source.mkdir()
            widget.mkdir(parents=True)
            for name in SHARED_FILES:
                (source / name).write_text('canonical ' + name)
                (widget / name).write_text('stale copy')
            (widget / 'CalendarView.qml').write_text('widget-specific editor')
            with self.assertRaisesRegex(ValueError, 'Widget copies differ'):
                check_shared(root)
            self.assertEqual((widget / SHARED_FILES[0]).read_text(), 'stale copy')
            sync_shared(root)
            check_shared(root)
            self.assertEqual((widget / 'CalendarView.qml').read_text(), 'widget-specific editor')
