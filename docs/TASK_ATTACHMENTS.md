# Local task file attachments

Included in Liquid Calendar 0.3.9.4 (beta prerelease). Earlier 0.3.9.3 release archives remain unchanged.

Open a task and use **+ Files** in the Files section. Select one or more local files, then save the task. The calendar stores copies; moving or deleting the originals does not break the attachments. The task list shows a file count, and filename text participates in search.

- Attach up to **10 files per task**, **10 MiB per file**, and **100 MiB of unique attached file contents across the calendar**. Repeated use of identical contents is deduplicated.
- **Open** asks the desktop to open a temporary copy using its associated application. Editing that copy does not change the stored attachment. Temporary copies are removed when the calendar exits.
- **Save copy…** writes a copy to a chosen destination. The file dialog confirms replacement of an existing file.
- **×** removes a file from the draft. Save to apply removal; Close/Escape discards it. Undo can restore a saved removal or a deleted task.
- Newly selected files are staged in memory. Cancelling the editor writes no file data. Failed/conflicting saves retain the draft and remain retryable.
- Tasks must have their files removed before conversion to regular events. Duplicating or editing a repeating task preserves its file references; a single occurrence can have its own attachment list.

## Storage and backups

Attachment metadata contains a content hash, filename and byte length. File contents live in a separate SQLite table, outside QML event models; no original filesystem paths are retained. A save commits event metadata and file contents in the same transaction. Original files are never moved or deleted. The table is added to an existing database without rewriting its records.

Automatic SQLite backups include file contents. Contents of removed attachments remain in the database for Undo and recovery; removing an attachment does not immediately reclaim disk space. There is currently no file-store compaction control.

Desktop **JSON export** produces version 2 when attachments are present and includes their bytes. Import checks filenames, bounds, complete file membership, lengths and SHA-256 integrity before saving. Ordinary version-1 JSON backups without attachments remain supported. A portable backup with attachments is larger and may contain sensitive documents: choose its destination accordingly. ICS exports do not include attachment contents and show a corresponding notice.

The companion widget preserves task attachment metadata when editing/completing tasks in a shared database. Its text-only backup controls direct attachment-bearing calendars to desktop JSON export/import instead of silently producing an incomplete backup. Adding/opening attachments is a desktop app feature. Reload an existing widget after updating its sources. Attachment metadata is tolerated on regular events as well, so a legacy widget changing a task type cannot make the shared calendar unreadable; the desktop editor requires removal before conversion.

## Desktop integration and validation

The UI uses [Qt FileDialog](https://doc.qt.io/qt-6/qml-qtquick-dialogs-filedialog.html) for selection and save destinations and [QDesktopServices](https://doc.qt.io/qt-6/qdesktopservices.html) for external-open requests. No extra filesystem permissions are added to the Flatpak manifest. A successful open request does not guarantee that the external viewer accepted the file.

See [testing](../TESTING.md). Automated checks use isolated files/databases and mocked external-open dispatch. Interactive host file chooser/viewer acceptance remains a desktop integration check.
