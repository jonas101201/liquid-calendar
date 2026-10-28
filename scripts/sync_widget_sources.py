#!/usr/bin/env python3
"""Keep standalone-widget copies in sync with the canonical files in qml/."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED_FILES = (
    'Calendar.js',
    'DatePicker.qml',
    'TimePicker.qml',
    'ActionMenu.qml',
    'ActionMenuItem.qml',
    'GlassTextField.qml',
    'GlassCheckBox.qml',
    'GlassSpinBox.qml',
)


def check_shared(root=ROOT):
    widget = root / 'companion-widget/contents/ui'
    mismatches = [
        name for name in SHARED_FILES
        if not (widget / name).is_file()
        or (root / 'qml' / name).read_bytes() != (widget / name).read_bytes()
    ]
    if mismatches:
        raise ValueError(
            'Widget copies differ: ' + ', '.join(mismatches)
            + '. Edit qml/ and run python scripts/sync_widget_sources.py.'
        )


def sync_shared(root=ROOT):
    widget = root / 'companion-widget/contents/ui'
    for name in SHARED_FILES:
        data = (root / 'qml' / name).read_bytes()
        (widget / name).write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail on drift without writing files')
    args = parser.parse_args()
    if args.check:
        check_shared()
    else:
        sync_shared()
    print('Shared app/widget sources match.')


if __name__ == '__main__':
    main()
