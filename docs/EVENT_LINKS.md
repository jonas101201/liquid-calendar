# Linked events — 0.3.9.2 Beta 2

Two linked events remain separate calendar records. Linking preserves each event's title, date, time, duration, category, location, notes and reminder. The editor includes unsaved changes in the link preview and final save.

## Create a link

1. Open a saved event or an individual occurrence of a recurring event.
2. Choose **More → Link with another event…**.
3. Choose another unlinked event on the edited date with the same all-day mode.
4. Review the two separate cards, then choose **Link events**.

The original records remain independent. For recurring sources, only the selected occurrences are detached; future repeats keep their existing schedule. Stale or concurrent source changes cancel the entire operation without partial writes. Cancel keeps the editor draft.

## Recognize and edit a group

Cards display the same **Linked** label and identify their partner. When one linked timed event fully contains the other, the week view uses the longer event as a background card with the shorter card inset at its scheduled time. For example, School 07:00–14:00 contains Exam 09:00–10:00. The group occupies one outer lane, and both cards remain separately clickable and draggable. Each shows its own time range. A containing segment needs at least 90 minutes of display space; equal, very short or partially overlapping intervals remain separate cards with shared labels/connection lines.

Linked members do not raise overlap warnings against one another. Unrelated events still produce real conflict indicators and separate outer lanes, including when they overlap a containing event or its child. All-day entries retain shared link labels.

Open either card to edit it individually. Moving one event preserves its link, including across dates. Its partner's time, details and reminder remain unchanged. When the partner is outside the visible date/filter, its title still identifies the relationship. Shared labels are display identifiers, not permanent group names.

## Unlink or delete

Choose **More → Unlink group** from either member. Both events remain; valid unsaved editor changes are saved in the same operation. Undo restores the previous saved state. Deleting one member retains the other and removes its stale link. Converting a member into a task or recurring series also clears a leftover singleton relationship. Undo covers the last local operation, including these relationship changes.

## Backups and compatibility

JSON exports preserve the optional `groupId` relationship. ICS exports two individual events and does not transfer the app-specific link. Older destructive merges cannot be automatically split back into the original events; no historical data is rewritten. The desktop app creates/unlinks groups; the companion widget displays and preserves links during normal edits. Existing groups must be unlinked before selecting a different partner.

This behavior is included in 0.3.9.2 Beta 2. The previously published 0.3.9.1 archives retain the old behavior.
