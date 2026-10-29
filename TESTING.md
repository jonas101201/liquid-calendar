# Testing

## Current release: 0.3.9 interface and editing checks

Adaptive palette checks cover all five accents in light and dark themes, verify hue propagation to calendar/popup glass and check text contrast against panel colors. Opacity-drag regression checks remain enabled.

Opacity regression checks sample 60 real pointer moves: no settings writes or calendar refresh notifications while held, one write on release and one debounced write for a keyboard burst. Appearance notification and duplicate-write suppression have separate unit coverage.

Theme checks exercise all three design choices, persisted selection, live desktop-palette changes in System mode and themed filter/sort menus. Light/dark previews are visually checked at both supported screenshot sizes.

The UI audit adds native keyboard shortcut dispatch, modal guards, appearance controls and persistence/failure handling, frozen week time labels and interrupted popup closure. There are 144 Python tests. Merge regressions cover unsaved form values, edited-date candidate selection, Cancel without writes, invalid drafts, immutable identity, concurrent changes and moved series occurrences (including another date of the same series). The independent Qt review additionally covers opacity limits and keyboard control in both themes, palette propagation and persistence through a fresh Bridge. See [the UI audit](docs/UI_AUDIT_2026-10-29.md).

The actual QML check covers consolidated Calendar navigation, intermediate animation frames, rapid section changes, popup close/reopen, and reduced motion interrupting a running section transition. It also presses and drags both calendar scrollbars before releasing the mouse, checks thumb grab offsets and keyboard endpoints, and verifies initial selection and overflow visibility. It uses an isolated database and synthetic events.

## Historical baseline: 0.3.8.1 maintenance refactor

133 Python tests, all eight JavaScript suites, actual app/widget QML checks and synthetic before/after screenshots cover the extracted controls and occurrence-helper reuse. Two distribution checks verify that stale widget copies are rejected and synchronization preserves widget-specific files. See [the refactor record](docs/REFACTOR_0.3.8.md). The release version is 0.3.8.1, marked as a beta prerelease.

## Historical baseline: 0.3.7-beta.1

The targeted post-release audit adds exact-day search, elapsed-minute planning, atomic booking and date-boundary regressions. Checks use synthetic data only. See [the audit record](docs/BUG_AUDIT_0.3.7.md) for 131 Python tests, eight JavaScript suites, actual Qt checks, isolated widget editing, smoke launches and the two independent review rounds. Hosted checks are associated with the release commit.

## Historical baseline: 0.3.6-beta.1

The [current source tests](https://github.com/jonas101201/liquid-calendar/actions/runs/40774771194) passed on Python **3.10, 3.12 and 3.14**, including 122 Python tests, actual Qt checks, smoke launch and eight JavaScript suites. [Security analysis](https://github.com/jonas101201/liquid-calendar/actions/runs/40774765474) also passed. These results cover source snapshot [`ff0988d`](https://github.com/jonas101201/liquid-calendar/commit/ff0988d6478d9f260b5df96a2f1b85065ab7e908); final checks are associated with the release tag commit. Automated results do not certify every desktop environment.

0.3.x cumulative coverage:

- **122 Python tests:** all 127 weekly-day subsets, legacy defaults, bounds, exclusions, search, reminders, per-occurrence changes and matching ICS DTSTART/BYDAY export, plus quick-entry defaults, English/German dates and explicit times, am/pm, ambiguity and invalid input, template field allowlists, fresh identity, persistence, caps and concurrent stale changes, plus task priorities, projects, checklist validation, project rename/merge/clear, atomic conflict and membership rejection, project Undo filter context, single-pass project aggregation, Unicode code-point limits, JSON round trips, occurrence-specific checklist progress and scheduling preservation, plus storage conflicts and undo, repeats/exceptions, undated tasks, English date search, free-slot checks, per-occurrence task completion, legacy series reopening, stale/concurrent completion rejection, reminder text, deterministic SQLite closure and rollback, and randomized interval comparisons.
- **Eight JavaScript suites:** weekly-day validation, next/last occurrence, export and backup preservation, plus task-detail validation and backup/search preservation in app and widget, plus calendar calculations, date/search behavior, undated tasks, shared-store merging, English aliases and task-occurrence completion.
- **14 offscreen QML views:** seven views at 980×680 in light and dark themes, plus four additional task renders at 980×680 and 1280×860, editor Save/reopen/invalid-step rejection, real keyboard input into new steps, draft retention after adding/removing steps, editor checkbox persistence, preserved expansion after edits/detachment, long emoji-field round trips and checklist Undo, actual dropdown mouse click and focus, quick-preview-to-editor flow, calendar/time picker signals, template Save/Use/Rename/Delete without accidental event writes, actual task-slot dispatch, Unicode save checks, grouped deletion and both native app Undo and the hidden calendar fallback.
- Independent review additionally compared overlap results against a simple pairwise reference and checked concurrent completion, midnight occurrence dates, connection lifetime and undo alongside unrelated edits.

The 840-occurrence agenda benchmark improved from about 1.55 seconds before the fix to about 0.02 seconds on the development machine. Timings depend on hardware; randomized correctness and operation-count regression checks complement the benchmark.

## Run the checks

From the repository root with requirements installed in a virtual environment:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software python tests/check_qml.py
python tests/check_widget_editor.py
python app.py --smoke-test
```

The smoke test automatically uses a temporary database. The QML check also creates an isolated database. Never point test commands at your personal calendar.

For widget logic, install Node.js and run:

```bash
node tests/test-calendar.cjs
node tests/test-search.cjs
node tests/test-undated.cjs
node tests/test-widget-sharing.cjs
node tests/test-english.cjs
node tests/test-task-completion.cjs
node tests/test-task-organization.cjs
node tests/test-weekdays.cjs
```

## Graphics dependencies and screenshots

Hosted Ubuntu CI installs Qt system libraries including libegl1 and libopengl0, even for offscreen checks. This is automated test-environment setup.

To render public screenshots from synthetic data:

```bash
python scripts/screenshots.py
```

Screenshots show the VERSION of the checked-out source. They do not use a personal calendar.

## Validation limits and audit clarification

Installation in a fresh user account has not been validated. Offscreen checks and CI do not replace live desktop testing across supported systems.

The initial audit overstated the reachability of the calendar fallback Undo issue. The native app already hid that action when persistence was attached; its visible global Undo already restored full groups. The internal fallback is now corrected and explicitly tested too.

## Historical baseline: 0.1.0-beta.1

The first public beta had 48 Python tests and five JavaScript suites. Its hosted CI result is preserved [here](https://github.com/jonas101201/liquid-calendar/actions/runs/40687586088). Those historical counts do not describe the current beta.

## 0.2.0 follow-up audit

An independent review reproduced Unicode validation differences, inline checklist collapse and concurrent project membership changes, then reviewed the corrections. Additional reproductions covered project Undo filtering and quadratic project summaries. See [the audit record](docs/BUG_AUDIT_0.2.0.md) for scope and limits.

Selected-weekday checks also exercise the actual day buttons, the last-day guard and save/reopen behavior. `check_widget_editor.py` loads the real widget editor against a temporary offline database with only the unavailable Kirigami theme lookup stubbed; it verifies weekday editing and preservation of existing priority/project/checklist values. This does not constitute live Plasma testing. Sharing protocol tests reject old version 2 and accept version 3.

## Additional 0.3 pre-release scan

122 Python tests include merge content/limits, stale edits before and after reload, atomic writes and Undo, ten simultaneous entries, short neighboring entries, midnight carry-in and 80 deterministic randomized layout scenarios checked against an overlap oracle. Actual Qt tests exercise the merge dialog preview/confirmation/Undo and synchronized horizontal week scrolling. Eight JavaScript suites, the isolated widget editor and temporary-database smoke launch remain required. These checks use synthetic data and do not establish that all bugs are absent. Final publication checks apply to the release commit.

Selected-occurrence merge tests cover two series, mixed event/occurrence source order, matching-day candidates, self/cancelled exclusion, forged snapshots, concurrent series edits, future-repeat preservation and Undo. Actual Qt tests reproduce the occurrence editor menu and assert that hidden actions occupy zero height with no leading blank row.
