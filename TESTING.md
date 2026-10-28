# Testing

From the repository root, with requirements installed in a virtual environment:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software python tests/check_qml.py
python app.py --smoke-test
```

The smoke test automatically uses a temporary database. Never point test commands at your personal calendar. The QML check uses its own temporary database and includes both themes, language checks and lossless handling of synthetic Unicode content.

For widget logic, Node.js is optional:

```bash
node tests/test-calendar.cjs
node tests/test-search.cjs
node tests/test-undated.cjs
node tests/test-widget-sharing.cjs
node tests/test-english.cjs
```

Development checks included storage conflict/undo tests, repeats and exceptions, tasks without dates, English relative/date search, availability rechecking, app/widget SQLite interoperability, and native QML interactions. Offscreen rendering covered 980×680 and 1280×860 in light and dark themes.

**Not performed for this public beta:** fresh-user-account installation validation (explicitly excluded by the maintainer). Automated CI is provided but a hosted CI run is only verified after publication. Live desktop compatibility beyond the development machine is not certified.

## Checks completed for 0.1.0-beta.1

- 48 Python functional tests passed from the release repository.
- Five Node.js calendar/widget suites passed.
- 14 real offscreen QML views at 980×680 passed in both themes, including Unicode data preservation on save.
- Source app smoke launch and `--version` passed using the existing development Qt runtime.
- Independent packaging review found a temporary screenshot-output path bug; fixed and rerun successfully.
- Installer and publishing script were reviewed without installing or contacting a remote repository.
- Release archives were checked for excluded data/binaries, internal manifest hashes and deterministic rebuilds.

The fresh-account installation check remains deliberately unperformed. No hosted CI run or public upload is claimed by these local results.
