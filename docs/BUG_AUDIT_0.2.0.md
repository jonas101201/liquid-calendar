# 0.2.0 task organization audit — 2026-10-28

Scope: preparation branch for 0.2.0-beta.1, using isolated synthetic records. Implementation review and independent verification covered task organization, shared storage and real offscreen QML interactions. This is a targeted audit, not a guarantee of bug-free software.

## Confirmed and corrected

| Finding | Reproduction | Correction and regression |
| --- | --- | --- |
| Project Undo leaves an empty filtered list | Select Launch, rename to Renamed, Undo: records return to Launch but filter still selects Renamed. | Restore the rename's previous filter only if the user has not subsequently selected another filter; cover rename, clear and no-op operations. |
| Project summary is quadratic | 5,000 tasks in distinct projects take about 4 seconds to summarize on the development machine. | Single-pass aggregation plus name sorting; about 0.007 seconds on the same machine. A traversal-count test checks the algorithm without a hardware-dependent time threshold. |
| Unicode validation disagrees across clients | Python accepts 41 emoji in a project or 101 in a checklist title while JS counts UTF-16 units and rejects the database. | JS counts Unicode code points like Python. Editor fields can hold the corresponding UTF-16 capacity; opening/saving long valid emoji texts preserves data. Duplicate titles are cut at code-point boundaries. Boundary tests cover IDs, titles, projects, locations, notes and steps. |
| Inline checklist collapses after each click | Expand an entry, toggle one step, and the replaced ListView delegate starts closed. | Keep expansion in the window using a stable occurrence key, including detached recurring occurrences. Actual Qt tests verify the state after a toggle and detachment. |
| Concurrent project rename is incomplete | A second client adds a Launch task before polling; rename changes only the old snapshot yet reports success. | Compare source-project membership under the same SQLite write transaction as the rename. Reject a changed membership atomically; refresh/retry includes the new tasks. |

The earlier typed-checklist-input fix also remains covered by actual keyboard events, add/remove actions, checkbox changes, Save and reopen.

## Validation

77 Python tests, seven JavaScript suites, real offscreen QML interaction checks and a temporary-database app smoke launch. Hosted checks run for the preparation pull request. The independent reviewer re-ran the 77 Python tests, Qt interaction checks and JavaScript organization suite and verified the final corrections without finding another concrete regression in the reviewed diff. Source packages are built from an explicit allowlist with manifests and checksums.

No personal calendar database was opened for tests. No fresh-account installation test or live Plasma desktop compatibility claim is made. Existing platform, reminder, synchronization and beta limitations remain in KNOWN_ISSUES.md.
