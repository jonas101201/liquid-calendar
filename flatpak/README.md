# Liquid Calendar Flatpak beta

Application ID: `io.github.jonas101201.LiquidCalendar`. The current package uses KDE Platform 6.10 and PySide BaseApp 6.10. The native pip requirements remain separate; this BaseApp currently supplies PySide 6.10.3 and Python 3.13.

## Install the local bundle

```bash
flatpak install --user ./liquid-calendar-0.3.9.3-x86_64.flatpak
flatpak run io.github.jonas101201.LiquidCalendar
```

The menu entry is **Liquid Calendar (Flatpak Beta)**. It is separate from the native installation. KDE Platform is a shared dependency, not included in the bundle's download size. A first installation may need a substantial runtime download.

## Data and compatibility

By default the Flatpak uses its own database under:

```text
~/.var/app/io.github.jonas101201.LiquidCalendar/data/liquid-glass-planner/calendar.sqlite
```

It does not read or migrate the existing Plasma calendar automatically. To bring events/tasks across, export JSON from the native app and import it using Flatpak Settings. JSON event backups do not include the separate template library. Keep the original installation until the imported data has been checked. File import/export uses the desktop's file chooser; the manifest grants no general home or network access.

Reminders use the Notification portal asynchronously. The app records a notification only after the portal acknowledges it; acknowledgment does not guarantee that the desktop displayed it (for example during Do Not Disturb). Autostart uses the Background portal and may require a desktop permission prompt. Timed-out requests are closed remotely before retrying; alternative returned request handles are supported. Its displayed state is the last acknowledged request; changing permission outside the app may require enabling it again. Login launches the app through its desktop entry.

The companion Plasma widget is installed separately with the native installer. It cannot be installed or reloaded by the Flatpak. An advanced, optional shared-storage launch is available:

```bash
flatpak run \
  --filesystem=xdg-data/plasmashell/QML/OfflineStorage/Databases \
  io.github.jonas101201.LiquidCalendar \
  --database "$HOME/.local/share/plasmashell/QML/OfflineStorage/Databases/DATABASE_FILENAME.sqlite"
```

Replace `DATABASE_FILENAME.sqlite` with the database filename shown in the native app Settings. This one-run filesystem grant exposes the Plasma OfflineStorage database directory, including its other widget databases, and permits SQLite journal files. Use a current widget with sharing protocol 3; editing is blocked otherwise. Update/reload the widget outside the Flatpak and choose **Check again**. Shared mode is optional and is not part of the default package permissions. Live shared-widget testing is separate from the isolated database checks.

## Build locally

Install Flatpak and its shared dependencies once:

```bash
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.kde.Platform//6.10 io.qt.PySide.BaseApp//6.10
python3 flatpak/build.py
```

The helper uses Flatpak's built-in build/export commands. Because it copies Python/QML source without compilation, the installed Platform also serves as its build environment; the large compiler SDK is not required for this path. A regular `flatpak-builder` manifest is also provided and uses `org.kde.Sdk` in the standard way.

Outputs are in `dist/flatpak/`: the installable bundle, SHA256SUMS, local OSTree repository and build-info.json with the exact runtime/BaseApp commits. A build directory is temporary by default. `--build-dir PATH --reuse-base` can reuse an initialized staging directory with this application ID; this replaces only its staged app files and exported metadata.

The BaseApp cleanup and explicit pruning remove WebEngine, NumPy, code generators and unused Python bindings. The calendar keeps QtCore, Gui, Widgets, QML, Quick, QuickControls2, QuickWidgets, Network, DBus, OpenGL, SVG and QtTest bindings. Qt libraries, platform plugins and translations come from the shared KDE runtime.

## Validation and distribution

- Native and installed-sandbox Python regressions use synthetic records.
- `tests/check_desktop_portals.py` exercises real D-Bus marshalling against an isolated synthetic portal service, including autostart enable/disable/denial and literal notification titles.
- Native QML and nested-card checks run offscreen with temporary databases; AppStream metadata is validated locally.
- The installed bundle is smoke-tested with `--smoke-test`, which selects a temporary database.

The beta bundle is distributed through the [0.3.9.3 GitHub prerelease](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.3). It is not a Flathub publication or a signed update channel. File-chooser interaction and real login/autostart prompts still require an interactive desktop acceptance check. No production database is used in the automated checks.
