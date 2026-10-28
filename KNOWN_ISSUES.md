# Beta limitations

- Target: Fedora Linux with KDE Plasma 6. Windows/macOS and other Linux desktops are not validated.
- A fresh-user-account installation test was explicitly skipped. Automated isolated-data and offscreen Qt checks are not an installation certification.
- The installer requires network access to PyPI and Python 3.10–3.14 with venv/pip support; it is not an offline installer. Linux Qt platform libraries must be available from the operating system.
- The interface is English only. No language selector or complete localization framework yet. German date-query aliases are retained as input compatibility.
- Local storage only: no account sync, mobile app or collaborative calendars.
- Reminders require the app to stay open or run in the system tray. System notifications use notify-send. Closing the window may keep reminders running; Ctrl+Q fully quits.
- Time suggestions cover 09:00–18:00 and use local floating times; no timezone-aware invitations or travel-time planning.
- JSON import adds new IDs and preserves existing IDs. ICS export contains events, not tasks; ICS import is not implemented.
- App and widget share the existing Plasma database. When an old active widget is detected, editing is blocked until Connect reloads it. Reloading Plasma briefly refreshes the desktop and panels.
- Undo covers the last local app change and refuses to overwrite a newer edit of the same entry.
- Back up important data before using a beta. See the README for storage and backup locations.
