# Liquid Calendar 0.3.9

Beta prerelease · **29 October 2026**. [Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9).

## A more coherent Liquid Glass interface

- One Calendar entry contains month and week views and remembers the selected presentation.
- Dark glass, Light glass and System designs have previews. System follows live desktop palette changes.
- Five accents recolor the background, glass panels, fields, menus, timeline and reflections, with readable text contrast in both themes.
- Sliding selections, gentle view/dialog transitions, hover reflections and press feedback respect reduced motion.
- Calendar scrollbars respond while held and dragged; the week time axis stays visible when scrolling horizontally.
- Settings restores persistent app-wide accent and opacity controls. Opacity dragging previews locally and saves once after release, avoiding repeated calendar rebuilds and database writes.

## Safer editing and merging

- Merge previews and results include unsaved editor changes. Candidates follow the edited date and all-day mode; Cancel writes nothing and Undo restores both original saved sources.
- Moving and merging a series occurrence affects only the selected original dates. Future repeats remain available.
- Merge sources are checked inside the write transaction, rejecting concurrent edits and duplicate merges from another client.
- Native shortcuts have one owner. Picker and menu palettes follow the chosen design, and the Settings scrollbar no longer overlaps content.

## Validation and update

144 Python tests, eight JavaScript suites, actual app/widget QML checks, opacity stress checks with 1,000 synthetic events and source synchronization checks passed locally. Independent Qt reviews checked the UI fixes, draft merging and concurrent-client protection. Hosted validation is attached to the release commit. Offscreen testing does not establish that every desktop environment is bug-free; installation in a fresh user account has not been tested.

Extract a release archive and run `python3 installieren.py`. Fully quit the app with **Ctrl+Q** before reopening; reload an active Plasma widget after updating shared files. Calendar storage and sharing protocol remain unchanged (protocol 3); no calendar-record migration is performed.

[Known issues](KNOWN_ISSUES.md) · [Roadmap](ROADMAP.md) · [UI audit](docs/UI_AUDIT_2026-10-29.md).
