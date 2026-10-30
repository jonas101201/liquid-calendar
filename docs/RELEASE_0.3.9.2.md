# 0.3.9.2 source update record

Source version **0.3.9.2**, beta · **30 October 2026**.

The earlier event-merge implementation and display were incorrect for related, contained events: independent fields were combined or intentional relationships were shown as conflicts, and inner cards could obscure the outer title. This update replaces that behavior with independent linked records, nested timeline cards, protected headers and simpler styling. Unrelated conflicts remain visible. Existing destructive merges cannot be reconstructed automatically.

Includes the export, preference, date and navigation corrections recorded in [the follow-up audit](BUG_AUDIT_0.3.9.1_FOLLOWUP.md). [Event linking](EVENT_LINKS.md) documents interaction and compatibility boundaries.

Validation uses synthetic databases: 172 Python tests, eight JavaScript suites, native QML checks, dedicated nested-card geometry/individual edit targets in both themes, isolated widget editing, source synchronization and smoke launch. Installation in a fresh user account has not been tested. Remaining reminder defects are documented in [Known issues](../KNOWN_ISSUES.md).

This is a repository source update. No new download release or version tag is created by this update. Existing release tags/assets remain unchanged.
