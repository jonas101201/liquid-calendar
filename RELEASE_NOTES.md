# Liquid Calendar 0.3.9.3

Beta prerelease · **31 October 2026**. [Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.3).

## Fixed

- **Smooth early popup closing:** closing a popup during its opening animation no longer briefly increases its scale.

- **Reliable automatic backups:** interrupted copies no longer leave an accepted empty daily backup. Copies are validated before atomic publication; existing empty/corrupt daily files are repaired before saving. Concurrent clients retain the first valid daily snapshot, and failures remain retryable.
- **Correct nested-event rescheduling:** dragging an inner event horizontally to another day preserves its start time. The previously reproduced 09:30 → 09:45 drift is fixed. Vertical dragging applies 15-minute movement increments while preserving an existing non-quarter-hour time offset.
- **Flatpak autostart cancellation:** a timed-out permission request is closed remotely, so the old dialog does not remain active after the app gives up. Alternative returned handles are followed and a subsequent request can succeed.

## Validation and downloads

182 Python tests, eight JavaScript suites, real native/Flatpak QML interactions, private D-Bus portal checks, isolated widget editing, AppStream validation, source-copy synchronization, smoke launches and archive/asset checksums form the validation set. Tests use synthetic records and temporary databases.

Native source ZIP/TAR archives, a separate Flatpak bundle, a build receipt and SHA256SUMS are included. The Flatpak uses separate storage by default; transfer existing events/tasks through JSON. It is not a Flathub release. See [Flatpak instructions](flatpak/README.md).

The two native notify-send issues remain documented in [Known issues](KNOWN_ISSUES.md). Interactive file-picker/login acceptance and installation in a fresh user account have not been tested. Previously damaged backup history cannot be reconstructed; repair snapshots the current live data. Existing release tags/assets remain unchanged.

Fully quit with **Ctrl+Q** before reopening an updated installation. See [the audit resolution](docs/BUG_AUDIT_0.3.9.2_BETA_2_FOLLOWUP.md).
