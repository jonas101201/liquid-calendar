# Calendar polish — 0.3.9.4

Included in Liquid Calendar 0.3.9.4 (beta prerelease). Earlier release archives and tags remain unchanged.

## Readable titles and contours

`BalancedTitle.qml` measures candidate word breaks using the displayed font. Titles that fit two lines use a balanced split; longer ones wrap and elide within two lines, with full text available on hover. List rows grow to keep dates, projects, action buttons and expanded checklists separate. Small timeline blocks and headers above nested events keep one line so children cannot obscure the parent title.

`ContinuousShape.qml` defines cubic corner segments with zero curvature at the joins to straight edges. Glass panels, menus, dialog backgrounds and event cards use that shared outline. Qt Quick Shapes draws the contour as vector geometry; no raster mask, texture generator or per-frame canvas is involved. Border widths and the existing palette/opacity controls remain supported.

## Refresh without losing position

Before a bridge model notification, refresh-aware lists record the first visible record, its pixel offset and the selected record. After replacement they restore those identities, falling back to a nearby position if the anchor was removed. Small context histories keep different views/queries independent. Checklist expansion remains keyed by task/occurrence identity, and week content-width changes clamp the existing scroll offset instead of recentering it.

The existing records remain visible when a store check fails. Date selection and an open editing draft are not replaced by refreshes.

## Background JSON import

The file picker starts a worker that reads, validates, checks attachment data and saves a single SQLite transaction. Progress updates do not rebuild calendar models. Current records remain visible. A progress dialog, including a details skeleton during the read stage, appears only if the operation exceeds 300 ms. Short operations do not flash a loading state.

Cancel is supported while reading, validating, waiting for the backup lock and preparing the transaction. An accepted cancellation rolls back new events and file blobs; existing data and Undo history remain. Immediately before SQLite commit, the job crosses a locked cancellation boundary and the button changes to Finishing. Cancellation after that boundary cannot claim that committed data was discarded.

Imports preserve existing IDs and changes made by another client. The local editor is paused during an import. Quitting cancels an unfinished import, or waits for its already-started atomic commit, before leaving the application. The worker uses its own store connections and never touches QML objects.

## Interruptible motion

Popups and dialogs share `PopupMotion.qml`. A new opening/closing target starts from the currently displayed progress. An independent animation can stop immediately when reduced motion is enabled, while popup lifetimes still respect the visual exit. The command menu retains its deferred dispatch so a new editor/dialog receives focus after the menu has closed.

## Validation

`tests/check_polish_details.py` uses actual Qt views and synthetic data in both themes. `tests/test_async_import.py` includes cancellation inside a transaction and at the commit boundary, shared-store updates, Undo, lock waits and malformed input. The existing calendar/editor, attachments, widget, nested-event, JavaScript and smoke checks remain required. The native host file chooser and live Plasma reload are not automated by these tests.
