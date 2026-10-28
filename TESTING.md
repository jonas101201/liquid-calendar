# Testing

## Preparing 0.3.0-beta.1

The [0.2.0 preparation CI run](https://github.com/jonas101201/liquid-calendar/actions/runs/40734583186) passed on Python **3.10, 3.12 and 3.14** for source commit [`fee524e`](https://github.com/jonas101201/liquid-calendar/commit/fee524ee31f0de11a8d4efd3d2a8090c84de3346). It runs the Python suite, real offscreen QML checks, application smoke launch and all seven JavaScript suites. [Security analysis also passed](https://github.com/jonas101201/liquid-calendar/actions/runs/40734571556). These links record the audited preparation snapshot; final release checks are attached to the exact commit identified by `v0.2.0-beta.1`. Automated checks do not certify every desktop environment.

0.3.0 local coverage (hosted CI pending for this preparation):

- **92 Python tests:** quick-entry defaults, English/German dates and explicit times, am/pm, ambiguity and invalid input, template field allowlists, fresh identity, persistence, caps and concurrent stale changes, plus task priorities, projects, checklist validation, project rename/merge/clear, atomic conflict and membership rejection, project Undo filter context, single-pass project aggregation, Unicode code-point limits, JSON round trips, occurrence-specific checklist progress and scheduling preservation, plus storage conflicts and undo, repeats/exceptions, undated tasks, English date search, free-slot checks, per-occurrence task completion, legacy series reopening, stale/concurrent completion rejection, reminder text, deterministic SQLite closure and rollback, and randomized interval comparisons.
- **Seven JavaScript suites:** task-detail validation and backup/search preservation in app and widget, plus calendar calculations, date/search behavior, undated tasks, shared-store merging, English aliases and task-occurrence completion.
- **14 offscreen QML views:** seven views at 980×680 in light and dark themes, plus four additional task renders at 980×680 and 1280×860, editor Save/reopen/invalid-step rejection, real keyboard input into new steps, draft retention after adding/removing steps, editor checkbox persistence, preserved expansion after edits/detachment, long emoji-field round trips and checklist Undo, quick-preview-to-editor flow, calendar/time picker signals, template Save/Use/Rename/Delete without accidental event writes, actual task-slot dispatch, Unicode save checks, grouped deletion and both native app Undo and the hidden calendar fallback.
- Independent review additionally compared overlap results against a simple pairwise reference and checked concurrent completion, midnight occurrence dates, connection lifetime and undo alongside unrelated edits.

The 840-occurrence agenda benchmark improved from about 1.55 seconds before the fix to about 0.02 seconds on the development machine. Timings depend on hardware; randomized correctness and operation-count regression checks complement the benchmark.

## Run the checks

From the repository root with requirements installed in a virtual environment:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software python tests/check_qml.py
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
```

## Graphics dependencies and screenshots

Hosted Ubuntu CI installs Qt system libraries including libegl1 and libopengl0, even for offscreen checks. This is automated test-environment setup.

To render public screenshots from synthetic data:

```bash
python scripts/screenshots.py
```

Screenshots show the VERSION of the checked-out source. They do not use a personal calendar.

## Validation limits and audit clarification

Fresh-user-account application-installation validation remains deliberately unperformed at the maintainer's request. Offscreen checks and CI do not replace live desktop testing across supported systems.

The initial audit overstated the reachability of the calendar fallback Undo issue. The native app already hid that action when persistence was attached; its visible global Undo already restored full groups. The internal fallback is now corrected and explicitly tested too.

## Historical baseline: 0.1.0-beta.1

The first public beta had 48 Python tests and five JavaScript suites. Its hosted CI result is preserved [here](https://github.com/jonas101201/liquid-calendar/actions/runs/40687586088). Those historical counts do not describe the current beta.

## 0.2.0 follow-up audit

A separate agent reproduced Unicode validation differences, inline checklist collapse and concurrent project membership changes, then reviewed the corrections. Additional reproductions covered project Undo filtering and quadratic project summaries. See [the audit record](docs/BUG_AUDIT_0.2.0.md) for scope and limits.
