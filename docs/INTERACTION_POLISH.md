# Interaction polish — 0.3.9.4

This change adapts the interaction patterns to a local Linux desktop calendar. Included in 0.3.9.4. Earlier release assets and version tags are unchanged.

| Pattern | Application |
| --- | --- |
| Skeleton loaders | Local records stay visible. A real background JSON import shows a delayed details skeleton, progress and Cancel only when it lasts more than 300 ms. Fast imports show no loader. |
| Optimistic updates | Local writes already update the UI immediately on success. Failed/conflicting writes retain the existing records; no speculative success state is introduced. |
| Command menu | Ctrl+K or Commands in the sidebar. Search multiple words across action titles and keywords; arrows wrap, Enter runs and Escape cancels. Actions reuse normal editors and validation. Unavailable Undo is omitted. |
| Shortcut hints | F1 shows a keyboard guide. Primary actions show contextual tooltips and Quick add shows its shortcut in the Tools menu. |
| Undo toasts | Actual calendar mutations show a dismissible hint. It pauses while hovered/focused or the window is inactive. Expiration does not remove Undo history. No-op or failed writes do not announce success. |
| Stale-while-revalidate | Existing local records stay displayed during periodic store checks. Refresh lists restore their visible record and pixel offset, selected entry and context; checklist expansion and the week viewport are preserved. |
| Pre-rendering | Existing view components remain instantiated; command definitions are ready immediately. No hidden network work or artificial loading state. |
| BlurHash placeholders | No remote image feed exists. No placeholder encoder is added. |
| View transitions | Rapid section changes retarget from the current frame instead of resetting opacity and position. Reduced motion immediately settles all section transitions. |
| Swipe-to-dismiss sheets | Desktop menus/dialogs use Escape, close controls and their normal outside-click policies. Editor drag gestures are not repurposed. |
| Interruptible animations | Popups and dialogs share one motion controller. Opening and closing retarget from the current visual progress; reduced motion stops interpolation immediately. The command palette dispatches the next dialog after its exit. |
| Predictive back | Android-specific back gestures are not part of this desktop application. |
| Hit slop | Date/time picker buttons are at least 38px high; spin buttons widen to 38px without overlapping neighboring targets. Main action buttons already provide 38px targets. |
| Safe-area insets | Existing window margins, minimum size and viewport-bounded popup widths are retained; the app has no mobile display cutout. |
| One-time-code autofill | No account or authentication flow exists. |
| Tabular numbers | Timeline hours, event time ranges, date/time picker digits and duration input use OpenType tabular numerals while retaining the system font. |
| Balanced headlines | Titles in list cards and sufficiently tall timeline blocks use measured two-line balancing. Dynamic row heights keep metadata/checklists separate; small blocks and parent headers stay compact. |
| Continuous corners | Glass surfaces, menus, dialog backgrounds and event cards share cubic corners whose curvature reaches zero at the straight edges. The outline is drawn as a vector shape; no image mask or per-frame canvas is used. |
| Idempotency keys | Existing store snapshots and conflict checks remain the authority. The event editor accepts one successful Save per open draft, preventing duplicate creation during close; failed saves remain retryable. No payment/network endpoint exists that would need idempotency keys. |
| Menu safe triangle | Current action menus contain no cascading submenu. Pointer travel is not delayed or intercepted. Revisit when nested menus are introduced. |

## Validation

`tests/check_interaction_polish.py` exercises the actual QML with synthetic records and keyboard input in both themes. It additionally checks retention of a preselected date in another week, retry after a failed Save, and duplicate Save rejection. Existing calendar/editor, nested event and widget checks remain required. No test uses a personal database.
