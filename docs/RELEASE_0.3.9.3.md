# 0.3.9.3 release record

**Liquid Calendar 0.3.9.3** · Beta prerelease · **31 October 2026** · Tag `v0.3.9.3`.

[Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9.3) · [Release notes](../RELEASE_NOTES.md) · [Audit and resolutions](BUG_AUDIT_0.3.9.2_BETA_2_FOLLOWUP.md).

Corrects three reproduced Beta 2 failures: incomplete automatic daily backups suppressing retries, nested horizontal dragging changing start times, and Flatpak autostart timeout leaving the remote request active. Backup copies are serialized, validated and atomically published; invalid current daily files are repaired. Dragging uses original times and movement deltas. Timeout closes the actual request handle and permits clean retries.

Validation includes 182 Python tests, eight JavaScript suites, actual Qt mouse interactions, isolated widget editing, private D-Bus request cancellation/late-grant/retry, AppStream validation, smoke launches, shared sources and source/Flatpak checksum matching. Tests use synthetic data. Native notify-send defects remain open. Live login/file-picker acceptance and a fresh-account install are not established by these tests.

The source archives and Flatpak refer to the same versioned source snapshot. Older published tags/assets remain unchanged. Repair does not recreate old backup contents; it snapshots current live data before saving a new change.
