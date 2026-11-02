# Liquid Calendar 0.3.9.4

Beta prerelease · **2 November 2026** · [Downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.4).

## New and improved

- **Task file attachments:** add, open, save copies and remove local files. Copies remain available after moving/deleting their originals, appear in filename search and survive Undo, restart and complete JSON backup/restore. Up to 10 files per task, 10 MiB each and 100 MiB of current unique file contents per calendar.
- **Faster keyboard workflows:** Ctrl+K searches commands; F1 shows shortcuts. Contextual key hints, dismissible Undo feedback and separate text-field Undo make common actions easier to discover.
- **Readable titles and continuous glass contours:** long event/task titles use up to two balanced lines where space allows. Rows grow around their metadata/checklists. Glass surfaces, menus, cards and dialogs share vector continuous-corner outlines.
- **Stable updates:** refreshes preserve the visible record and scroll offset, selection, expanded checklists and week viewport.
- **Background JSON import:** the interface stays available while a worker reads/checks/saves. Slow imports show progress, a reading-stage skeleton and Cancel; fast imports do not flash a loader. Accepted cancellation rolls back new events and file blobs. The final atomic commit is labelled Finishing and cannot be cancelled.
- **Interruptible motion:** popup/dialog opening and closing retarget from the current frame; reduced motion settles immediately. The command menu waits for its exit before handing focus to the next dialog.
- **Additional corrections:** retain a preselected startup date, prevent repeated Save from creating duplicate events, and protect calendar Undo while editing text or importing.

## Validation and downloads

210 Python tests, nine JavaScript suites, actual Qt calendar/editor/file/shortcut/refresh/animation interactions in both themes, private D-Bus portal checks, isolated widget editing, native/Flatpak smoke launches, shared-source synchronization, AppStream validation and package checksum checks form the release validation set. All tests use synthetic records and temporary files/databases.

Downloads include native source ZIP/TAR archives, an x86_64 Flatpak bundle, its build receipt and SHA256SUMS. Flatpak stores its data separately by default; transfer through desktop JSON export/import. This is not a Flathub publication. See [installation](flatpak/README.md).

## Compatibility and limits

- JSON exports with file attachments use **backup format version 2**. Use 0.3.9.4 desktop import to restore them. Plain version-1 backups remain supported. Widget-only text backup controls direct file-bearing calendars to the desktop app; ICS contains no attached file contents.
- Opened attachment copies do not write external edits back into the stored file. Removed contents remain for Undo/recovery; there is no compaction control yet.
- The two native `notify-send` issues remain open. Host picker/viewer acceptance, real login/autostart acceptance, live Plasma reload and installation in a fresh account are not established by isolated tests. See [Known issues](KNOWN_ISSUES.md).

Quit completely with **Ctrl+Q** before reopening an updated installation. Reload an existing companion widget after updating its sources. Earlier tags and release assets remain unchanged.
