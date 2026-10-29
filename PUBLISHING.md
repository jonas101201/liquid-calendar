# Publishing Liquid Calendar

## Current public beta

**0.3.9** is published as **Liquid Calendar 0.3.9** (beta prerelease) on **29 October 2026**.

- [Public repository](https://github.com/jonas101201/liquid-calendar)
- [Release and downloads](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9)
- [Release record](docs/RELEASE_0.3.9.md) and [UI audit](docs/UI_AUDIT_2026-10-29.md).

The release includes source ZIP and TAR archives plus SHA256SUMS. It is marked as a prerelease. Published tags and assets identify fixed snapshots; documentation updates on main do not replace an existing release archive.

## 0.2.0 release record

Version 0.2.0-beta.1 was released on **28 October 2026**. See [the release record](docs/RELEASE_0.2.0.md).

## 0.3.6 release record

Version 0.3.6-beta.1 is the first published 0.3.x beta, including all six development patches after the 0.3.0 baseline. See [the release record](docs/RELEASE_0.3.6.md). Earlier published tags/assets remain unchanged; intermediate development versions were not published separately.

## 0.3.7 release record

The audited bug-fix patch was released on 28 October 2026. See [the release record](docs/RELEASE_0.3.7.md) and [independent audit](docs/BUG_AUDIT_0.3.7.md). Existing published tags and assets remain unchanged.

## 0.3.8.1 release record

Version **0.3.8.1** was released on 28 October 2026. The earlier 0.3.8-beta.1 preparation was not published separately; the release is still marked as a prerelease. Shared sources pass the sync check before packaging and installation. See [the release record](docs/RELEASE_0.3.8.1.md) and [refactor record](docs/REFACTOR_0.3.8.md).

## Preparing a future release

1. Choose the next version using ROADMAP.md. Bug fixes increment the patch version; feature milestones increment the minor version.
2. Update VERSION and companion-widget/metadata.json together, followed by README.md, CHANGELOG.md, RELEASE_NOTES.md, KNOWN_ISSUES.md and TESTING.md as applicable.
3. Regenerate synthetic-data screenshots if the UI/version display changed: `python scripts/screenshots.py` with the development Qt environment active.
4. Run the checks in TESTING.md. Record what actually passed and any checks not performed.
5. Commit the reviewed source on main, then create the matching version tag on that exact commit. For example, after selecting a new VERSION, use `git tag -a "v$(cat VERSION)" -m "Liquid Calendar $(cat VERSION)"`.
6. Publish the new tag as a prerelease and attach archives built from that same source snapshot.

Do not move an already published tag or replace its downloads to conceal later changes. Release another patch or beta iteration instead. Historical version numbers belong in the changelog and previous-release references.

## Through the GitHub CLI

Install the official GitHub CLI (https://cli.github.com/), authenticate with `gh auth login`, then run from a clean, reviewed and tagged repository:

```bash
./scripts/publish_github.sh
```

The script uses your authenticated personal account. To select an organization with repository-creation rights, supply it as an argument. For this existing repository, use its owner:

```bash
./scripts/publish_github.sh jonas101201
```

The script builds the archives, pushes main and its version tag, and creates a prerelease. It checks that HEAD matches the tag, rejects an unrelated origin and refuses to replace an existing release. Do not rerun it to overwrite 0.2.0-beta.1.

## Through the web interface

1. Open the existing repository's Releases page and choose **Draft a new release**.
2. Select the new version tag and verify its commit.
3. Set the versioned title and paste the matching RELEASE_NOTES.md.
4. Attach the assets listed in dist/release.json and mark **Pre-release**.
5. Verify filenames, uploaded checksums and CI results, then publish.

Do not upload the development workspace, installed runtime, real calendar database, logs or backups. The builder uses an explicit source allowlist:

```bash
python3 scripts/build_release.py
```

The resulting dist/SHA256SUMS applies to those newly built archives. Rebuilding modified main with an old VERSION does not reproduce the old published source snapshot; check out its release tag to reproduce that release.
