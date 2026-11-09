# Focused bug audit — 0.3.9.5

8 November 2026. Inspected native/portal reminder dispatch, process completion, import transactions/cancellation, attachment staging/storage and refresh behavior. Tests use temporary synthetic data only.

## Reproduced failures in 0.3.9.4

1. `notify-send` received `--help` in the title position without `--`. It could print help and return success instead of delivering a reminder.
2. A synthetic 350 ms native sender delayed a 20 ms Qt timer to approximately 354 ms. Native delivery used `subprocess.run` on the GUI thread, with up to eight seconds of blocking per due reminder.
3. Nonzero native exits were not surfaced as delivery errors. Completion is now shared with the existing pending/success/failure tracking used by portal notifications.

## Corrections

Native delivery uses a serialized QProcess queue, explicit end-of-options separator, per-attempt eight-second timer and exactly-once completion. Only successful normal exits mark reminders delivered. Failed starts/exits/timeouts free the pending key for a later tick. Pausing successfully discards queued native attempts without recording them as delivered; failed preference writes preserve the active queue. Shutdown stops/reaps child processes. The Flatpak portal path is retained.

## Regression scope

218 Python tests include seven real-process cases and bridge acknowledgement/pause tests. Existing synthetic import, attachment, storage/conflict/Undo and refresh checks remain enabled, alongside nine JavaScript suites, offscreen QML interactions, portal checks and app/widget smoke checks. Packaging verifies source checksums and matching Flatpak payloads. See TESTING.md and the release record for final validation.

No other confirmed defect was established by this focused scan; this is not an exhaustive guarantee. Actual desktop notification display, host pickers/viewers, login/autostart prompts, live Plasma reload and a fresh-account install are outside isolated testing. Earlier tags/assets are unchanged.
