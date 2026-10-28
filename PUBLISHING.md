# Publishing this beta

The source package is prepared for a **public** GitHub repository named `liquid-calendar` and a GitHub **prerelease** tagged `v0.1.1-beta.1`.

## Current status

Local repository, versioned source, English docs, GPL license, automated test workflow and downloadable archives are prepared. A remote repository or hosted release is only public once GitHub confirms its creation. An authenticated GitHub connection is required; the preparation itself does not publish anything.

## Through the GitHub CLI

Install the official GitHub CLI (https://cli.github.com/), authenticate with `gh auth login`, then run from this repository:

```bash
./scripts/publish_github.sh
```

The script uses your authenticated personal account. To choose an organization where you have repository-creation rights:

```bash
./scripts/publish_github.sh ORGANIZATION
```

It builds the archives, creates a public repository, pushes the main branch and beta tag, and attaches the tar.gz, zip and checksums to a prerelease. It refuses an unrelated existing origin or an existing release rather than replacing content.

The local seed commit uses a reserved, non-contact `maintainer@localhost.invalid` author email to avoid exposing a personal address. Set your preferred public/noreply Git identity before future commits if desired.

## Through the web interface

1. Create an empty public repository named `liquid-calendar`, without adding a separate license/README.
2. Push this repository's main branch and tag using the commands GitHub provides.
3. Create release `v0.1.1-beta.1`, title **Liquid Calendar 0.1.1 Beta 1**.
4. Paste RELEASE_NOTES.md, attach the files listed in `dist/release.json`, and mark **This is a pre-release**.

Do not upload the whole development workspace, installed runtime, real calendar database, logs or backups. The release builder uses an explicit source allowlist. See `dist/SHA256SUMS` for download checksums. Rebuild with `python3 scripts/build_release.py` after any source change.

Fresh-account installation testing was deliberately omitted, as requested. This is documented in the README and release notes.
