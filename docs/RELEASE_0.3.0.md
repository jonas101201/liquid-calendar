# 0.3.0-beta.1 preparation

Branch: `prepare/0.3.0-beta.1`. Not published; no release date scheduled. Current public release: 0.2.0-beta.1.

## Scope

- [x] Multiple selected weekdays for weekly repeats, matching calendar/search/reminder behavior and JSON/ICS export; legacy defaults and per-occurrence changes preserved.
- [x] Existing main layout retained, with Tools and editor More dropdowns for additional functions.
- [x] Deterministic quick-entry parser with English/German dates, times, durations and a reviewable draft.
- [x] Date/month/year grid and time selection, including repeat-end dates, in desktop and widget editors.
- [x] Desktop event-template save/use/rename/delete with date-independent defaults and fresh IDs.
- [x] Transactional template state, validation/caps and snapshot-based concurrent-edit rejection.
- [x] Existing calendar data left unchanged; templates are in a separate database key.
- [x] Python, JavaScript and actual offscreen QML interaction checks.
- [x] [Hosted tests](https://github.com/jonas101201/liquid-calendar/actions/runs/40749293714) and [security analysis](https://github.com/jonas101201/liquid-calendar/actions/runs/40749289194) passed for implementation commit `5492bc9` on Python 3.10, 3.12 and 3.14.
- [ ] Publication requested; final metadata, source archives/tag and prerelease published.

The [draft preparation PR](https://github.com/jonas101201/liquid-calendar/pull/2) contains the latest source and check status. The local development app/widget were updated with program-file backups; installed-app smoke launch passed without opening personal calendar data.

## Verification scope

102 Python tests and eight JavaScript suites, plus actual Qt preview/review, calendar/time picker, template Save/Use/Rename/Delete and final event Save/reopen behavior. Test databases and screenshots use synthetic data. Offscreen rendering covers the existing small-window/theme views; it does not establish live Plasma compatibility on every system. Fresh-account installation testing remains excluded.

## Publication steps

When publication is explicitly requested: inspect current branch and CI, finalize VERSION/widget metadata and English documentation, update roadmap/changelog/current-version links, merge the verified preparation into main, require final CI, build and verify source archives/manifests, tag that exact commit and publish a prerelease with ZIP/TAR/SHA256SUMS. Never overwrite existing published tags or assets.

The limited quick-entry grammar and template backup/Undo scope are documented in README.md and KNOWN_ISSUES.md. Template storage remains separate from events. Selected-weekday repeats require sharing protocol 3; reload an active older widget with Connect before editing.
