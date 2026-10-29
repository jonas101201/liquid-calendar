# Targeted maintenance refactor — released as 0.3.8.1

Scope: reduce duplicated implementation while preserving the existing public behavior after 0.3.7. No new feature, visual redesign, database format change or personal-data migration. Published as **0.3.8.1** (beta prerelease). The 0.3.8-beta.1 preparation was not published separately. See [the release record](RELEASE_0.3.8.1.md).

## Changes

- Extract GlassTextField.qml, GlassCheckBox.qml and GlassSpinBox.qml with explicit palette properties. Editors retain their existing local aliases, IDs and handlers. Date/time pickers reuse the same spin implementation, including editable-value commit behavior.
- Use qml/ as the canonical source for the eight files listed in scripts/sync_widget_sources.py. Standalone Plasma deployment still contains physical copies. CI, archive building and the installer check for drift; synchronization updates only the listed files, leaving the widget-specific editor intact.
- Reuse occurrence_draft for completion, checklist progress and moving an individual recurring occurrence. Checklist changes happen after snapshot construction, retaining the original series fingerprint for conflict checking. Existing storage/Undo logic is unchanged.
- List Python logic dependencies explicitly and expand Bridge initialization. App and widget keep their separate runtime implementations where Plasma requires JavaScript; no additional service layer is introduced.

## Verification

133 Python tests and eight JavaScript suites passed. Existing actual Qt checks exercise typing, checklist edits, pickers, templates, merging, recurring occurrences, Undo and endpoint rendering. The isolated widget check loads the real widget editor with only the Kirigami theme lookup stubbed. Distribution tests reject stale copies and preserve widget-specific files during synchronization.

Eight of nine controlled synthetic before/after renders were pixel-identical, including the editor, date picker, quick entry, templates, task view and weekly-repeat controls. The week render differed only in the six-pixel horizontal-scrollbar band (animation timing); its content was pixel-identical. Captures used the same hash seed and version so storage iteration order/version labels could not hide a layout change.

Both source archive manifests and all extracted shared-component copies were verified. The extracted TAR's app completed its smoke launch using a temporary database; the source installer help/import check also passed without performing an installation. Installation in a fresh user account has not been tested. Test databases are temporary; updater operations copy backed-up program files only and do not open personal calendar records.
