# 0.3.9.2 Beta 2 follow-up audit — 31 October 2026

Scope: the published Beta 2 source and current matching runtime logic. This record describes failures reproduced in Beta 2 and their subsequent corrections in 0.3.9.3. The original audit did not alter application behavior or published assets. Calendar tests use isolated synthetic databases. The portal reproduction uses a private D-Bus service.

## 1. Interrupted automatic backup is accepted as the daily backup

Priority: high for backup reliability. Status: corrected in 0.3.9.3.

`Store.backup()` writes directly to the final daily filename and treats an existing filename as a completed backup. A failed copy leaves that filename behind; the next call skips it without checking completeness.

Reproduction: seed an isolated live SQLite database with 15 synthetic records containing long notes. Invoke the real SQLite backup operation with one-page copying and a progress callback that raises an I/O error after the first page. The destination remains a zero-byte file. Restore normal I/O and save an edited event through `Store.merge()`. The save succeeds, the zero-byte backup is unchanged and opening it reports `no such table: state`.

Expected: incomplete destinations must not suppress a later backup attempt. The live database remains readable; this finding concerns the missing recovery snapshot rather than immediate deletion of live events. Retain a separate verified JSON backup after an error.

## 2. Horizontal dragging of header-displaced nested cards shifts the time

Priority: medium. Status: corrected in 0.3.9.3.

The inner card's `homeY` includes header clearance. The week DropArea calculates the target minute directly from the displayed drop position without subtracting that visual-only offset.

Reproduction: create a linked School event at 09:00–12:40 and Exam at 09:30–10:30. Use actual held-pointer Qt events to move Exam exactly one day to the right, keeping the pointer's vertical coordinate constant. The saved date advances one day but the start changes from 09:30 to 09:45. The parent stays unchanged. No QML warning is emitted.

Expected: a horizontal-only reschedule preserves the original start time, rounded only for an intentional vertical change. Until corrected, change the date in the editor and check the time.

## 3. Flatpak autostart timeout does not close the remote request

Priority: medium. Status: corrected in 0.3.9.3.

`BackgroundRequest.finish()` disconnects the response handler and deletes its local request object after timeout, but never calls the portal Request interface's `Close()` method. The remote interaction can remain active.

Reproduction: use a private synthetic portal that returns a valid request handle, records Close calls and grants permission after a delay. Shorten the app timer to 25 ms to exercise the existing 120-second timeout branch; emit a successful grant at 120 ms. The app reports timeout, the service receives zero Close calls, and the later grant is ignored by the app even though the service records permission granted. No real desktop permission is modified.

Expected: cancel the remote interaction when giving up, so a late grant cannot silently diverge from the app's local autostart state. The official [Request interface](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html) defines Close as ending the related interaction.

## Verification and limits

All 176 existing Python tests pass. The new findings are outside the current regression coverage: pointer-driven nested rescheduling, a genuine interrupted SQLite copy followed by a successful retry, and remote-request lifetime after portal timeout. Passing the existing suite does not invalidate these reproductions.

The two previously documented native notify-send defects (option-like titles and blocking notification delivery) also remain open; they are not counted as new findings here. No fixes or release were performed in this audit. This is a bounded review, not a claim that all other behavior is bug-free.

## Resolution in 0.3.9.3

Backups now use serialized, validated temporary copies and atomic publication; incomplete existing daily files are repaired. Dragging applies the movement delta to the original time, preserving horizontal-only times even when the card is visually displaced. Autostart timeout sends Close to the actual portal request, ends its listener and supports a clean retry.

Regression validation adds six Python backup cases (182 total), actual held-pointer drag cases and a private D-Bus cancellation/late-grant/retry scenario. No historical backup contents are reconstructed; a repaired daily backup records current live data before the next edit.
