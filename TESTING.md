# Testing

## Current beta: 0.1.1-beta.1

The [published release CI run](https://github.com/jonas101201/liquid-calendar/actions/runs/40712199654) passed on Python **3.10, 3.12 and 3.14**. It runs the Python suite, real offscreen QML checks, an application smoke launch and the JavaScript suites. This verifies automated behavior; it does not certify every desktop environment.

Current coverage:

- **60 Python tests:** storage conflicts and undo, repeats/exceptions, undated tasks, English date search, free-slot checks, per-occurrence task completion, legacy series reopening, stale/concurrent completion rejection, reminder text, deterministic SQLite closure and rollback, and randomized interval comparisons.
- **Six JavaScript suites:** calendar calculations, date/search behavior, undated tasks, shared-store merging, English aliases and task-occurrence completion.
- **14 offscreen QML views:** seven views at 980×680 in light and dark themes, plus actual task-slot dispatch, Unicode save checks, grouped deletion and both native app Undo and the hidden calendar fallback.
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
