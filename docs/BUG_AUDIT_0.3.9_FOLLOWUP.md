# Calendar interaction follow-up — 29 October 2026

Released as **0.3.9.1**, following the 0.3.9 source snapshot.

- The Month/Week control previously supported clicking and animated its selection, but had no drag gesture. The selection now follows a held pointer, clamps to its bounds and selects the destination on release. Click and Space activation remain available; losing the visible control cancels the gesture.
- Month-card Open previously opened a whole repeating series. It now opens the selected occurrence through the native bridge. A separate Series action opens the parent schedule.
- Month/widget calendars omitted the following-day segment of overnight entries. Shared instance generation now includes carry-in with an explicit source occurrence date. Details show Continued at 00:00 with the remaining duration; editing and task completion target the source occurrence. Exact-midnight endings and all-day entries do not add a following-day segment.

Validation uses isolated synthetic data. Native Qt checks exercise real pointer input, cancellation, reduced motion, actual month-card buttons and Undo. JavaScript regressions cover carry identity, cancelled sources and daily repeats. The existing 144 Python tests, eight JavaScript suites and widget editor checks remain in the validation set.

An independent agent reproduced the month edit/carry defects, rechecked the fixes through actual Open/Series/completion clicks and checked the drag implementation with explicit mouse events whose held-button state is LeftButton. A suspected Ctrl+Z issue in search was disproved: text input handles it without changing calendar records. These checks do not establish that every desktop interaction is free of bugs.
