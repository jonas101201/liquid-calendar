# Liquid Calendar — Local-First Security Plan

**Status: Proposed requirements, not implemented functionality.** The current Calendar beta stores user data in an **unencrypted SQLite database** and maintains local backups. Do not describe the application as providing database-at-rest encryption until a tested implementation is released.

## Security and privacy goals

- Local-first: the planner works without a Liquid account and, for its core planning features, without an internet connection.
- No compulsory analytics, tracking, or sharing of calendar contents.
- Users own their data: clear local storage paths, export, backup, restore, and deletion controls.
- Secure by design: confidentiality, data integrity, recovery, and accessibility are all release quality criteria.
- Optional network functions (e.g. future CalDAV) require explicit setup and transparent behavior.

## Proposed encrypted storage

- Evaluate **SQLCipher** for SQLite at-rest encryption; confirm compatible bindings, licensing, package distributions and Flatpak support first.
- Encrypt **sensitive local attachments, backups and any other persisted copies**. Audit WAL/journal files, indexes, thumbnails, debug logs, transient files, and JSON/ICS exports to avoid plaintext leakage.
- Create a distinct random database key. Prefer OS-backed key protection, e.g. KDE Wallet / Secret Service, for a low-friction default unlock experience.
- Offer optional stronger, password-based protection and timed app lock. Evaluate **Argon2id** for password-based key wrapping; avoid storing plaintext keys or hardcoding secrets.
- When secure OS credential storage is absent or locked, fail transparently and offer a safe unlock flow, not silent plaintext fallback.
- Design a tested recovery / device-migration workflow. Explain honestly when a missing key or forgotten password makes recovery impossible.
- The existing Plasma widget must not embed keys in QML or bypass encryption. Explore an authenticated, minimal local data-access API with least-privilege access; preserve reminders and offline behavior.

### Protection boundaries

Encryption at rest helps against copying data files or stolen backup media when keys are unavailable. It does not prevent access via an already unlocked application, malicious code running under the logged-in user, or a compromised operating system. Recommend system full-disk encryption as an additional layer.

## Implementation / release checklist

- [ ] Create a threat model, data-flow map and inventory of plaintext persistence.
- [ ] Prototype supported SQLCipher + credential-store integration on Fedora/KDE and in Flatpak.
- [ ] Document precise lock/unlock UX and key lifecycle, including wallet-unavailable conditions.
- [ ] Prototype encrypted database and attachment storage without duplicating secrets in memory or logs.
- [ ] Design reversible, interruption-safe migration of current users' plaintext databases; preserve backup integrity.
- [ ] Cover reminder scheduling and Plasma widget access when the UI is closed or locked.
- [ ] Design backup encryption, restore verification, recovery-key handling and imports/exports.
- [ ] Test failure cases (bad passwords, key loss, wallet reset, disk full, interrupted upgrade and downgrade).
- [ ] Include negative/security tests and real-user usability tests.
- [ ] Update README, docs and release notes only when encryption actually ships.

## Roadmap placement

Perform architecture, threat-model and migration feasibility work **during the remaining Calendar betas**. Aim to resolve production encryption scope by **0.10.0 / 1.0 release readiness**, with any shift to the official milestones explicitly documented in [ROADMAP.md](../ROADMAP.md). Never rush or silently ship a breaking data format change just to meet a version target.

See the [Liquid Ecosystem security principles](https://github.com/jonas101201/liquid-ecosystem/blob/main/SECURITY_PRINCIPLES.md). Future apps may share security interfaces, but should have separate keys and independent data stores.
