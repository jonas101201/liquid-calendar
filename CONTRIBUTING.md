# Contributing

Thank you for helping improve Liquid Calendar. Use English for code, documentation and issue reports. Small focused fixes are welcome.

1. Create a Python 3.10–3.14 virtual environment and install requirements.txt.
2. Run the automated checks in TESTING.md using isolated data.
3. Describe the problem, resulting behavior and checks in your pull request.
4. For UI changes, include screenshots made with synthetic data.

Report your OS, Plasma/Python versions, beta version and reproducible steps. Remove private event details, credentials, database paths and personal information from logs/screenshots. Do not attach real calendar databases.

Contributions are made under GPL-3.0-or-later, the same license as this project. Do not submit code or assets you do not have permission to contribute.

The current public beta is **0.3.9.1**, including the adaptive interface, draft-aware merging and earlier audited fixes. Read [KNOWN_ISSUES.md](KNOWN_ISSUES.md) before reporting a limitation and [ROADMAP.md](ROADMAP.md) before proposing planned features. Include your exact version when reporting bugs.

## Shared app/widget sources

Edit the common files listed in `scripts/sync_widget_sources.py` under `qml/` only, then run `python scripts/sync_widget_sources.py`. The widget keeps deployable copies because Plasma installs it independently of the app. `python scripts/sync_widget_sources.py --check` detects drift without writing; CI, the source builder and installer enforce it. Keep widget-specific `CalendarView.qml` separate. Current version: **0.3.9.1** (beta prerelease).
