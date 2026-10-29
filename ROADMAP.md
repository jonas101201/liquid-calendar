# Liquid Calendar Roadmap

This roadmap outlines ten beta milestones, from **0.1.0** through **0.10.0**, followed by release candidates and the first stable release.

It is a planning draft, not a delivery promise. Features and priorities may change based on feedback, testing and contributor availability. The first three milestones have been released; later milestones have no set release dates.

## Beta milestones

| Version | Focus | Planned features | Status |
| --- | --- | --- | --- |
| **0.1.0** | First public beta | Calendar, tasks, agenda and local storage | Released; last bug-fix beta: [`0.1.1-beta.1`](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.1.1-beta.1) |
| **0.2.0** | Task organization | Priorities, checklists and projects | Released 2026-10-28: [`0.2.0-beta.1`](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.2.0-beta.1) |
| **0.3.0** | Faster event creation | Quick entry, improved date and time selection, and event templates | Released 2026-10-28 as [`0.3.6-beta.1`](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.6-beta.1) |
| **0.4.0** | Flexible daily planning | Custom working hours, breaks, and splitting tasks across multiple time blocks | Planned |
| **0.5.0** | Multiple calendars | Show and hide separate personal, work and custom calendars | Planned |
| **0.6.0** | Import and sharing | ICS import with a preview and duplicate detection | Planned |
| **0.7.0** | Better reminders | Snooze and multiple reminders per event | Planned |
| **0.8.0** | Synchronization | CalDAV integration and clear handling of synchronization conflicts | Planned |
| **0.9.0** | Accessibility and languages | Full keyboard navigation, contrast options and a foundation for translations | Planned |
| **0.10.0** | Preparing for 1.0 | Updates, backup restoration, performance improvements and broader system testing | Planned |

English remains the primary interface language. The language milestone introduces the infrastructure for additional translations.

## Bug-fix releases and version naming

The current release is **0.3.9** (beta prerelease), including adaptive Liquid Glass themes, UI fixes and draft-aware merging after the third feature milestone. The next milestone is **0.4.0**, with configurable planning hours, breaks and task splitting. See the [release record](docs/RELEASE_0.3.6.md).

Each beta milestone can receive bug-fix releases as needed. These do not count as additional milestones in the ten-beta roadmap.

| Purpose | App display example | Version / GitHub tag |
| --- | --- | --- |
| New feature milestone | Liquid Calendar 0.3.0 Beta | `0.3.0-beta.1` / `v0.3.0-beta.1` |
| Bug-fix release for that milestone | Liquid Calendar 0.3.1 Beta | `0.3.1-beta.1` / `v0.3.1-beta.1` |
| Another bug-fix release | Liquid Calendar 0.3.2 Beta | `0.3.2-beta.1` / `v0.3.2-beta.1` |
| Another test iteration of the same version | Liquid Calendar 0.3.1 Beta 2 | `0.3.1-beta.2` / `v0.3.1-beta.2` |

For example, **0.3.1** is a bug-fix release for the third milestone. The **Beta** label remains visible until the stable release. The numeric milestone after **0.9.0** is **0.10.0**.

## After the beta milestones

After **0.10.0 Beta**, release candidates can be published as `1.0.0-rc.1`, `1.0.0-rc.2`, and so on, followed by **1.0.0** when the release is ready.

## Feedback and contributions

Share feature suggestions and reproducible bug reports through [GitHub Issues](https://github.com/jonas101201/liquid-calendar/issues). See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Development patch tracking

Each functional patch after the initial 0.3.0 development baseline received the next patch number, retaining `-beta.1`. Documentation-only commits were not numbered separately. **0.3.6-beta.1** publishes the cumulative result; 0.3.0–0.3.5 remain unpublished historical snapshots. Existing published tags are never moved. See the [per-patch changelog](CHANGELOG.md). Future bug fixes increment the patch number, for example 0.3.8-beta.1; the next feature milestone is 0.4.0-beta.1.

The **0.3.7-beta.1** bug-fix patch was released on 28 October 2026. It corrects exact-date search, atomic scheduling and supported date endpoints; the next feature milestone remains 0.4.0. See the [audit record](docs/BUG_AUDIT_0.3.7.md).

The maintenance refactor was published on 28 October 2026 as **0.3.8.1**. The 0.3.8-beta.1 development label was not published separately. This is maintenance of the third milestone; the next feature milestone remains 0.4.0. See the [release record](docs/RELEASE_0.3.8.1.md).

## 0.3.9 interface and editing update

Released on **29 October 2026** as [0.3.9](https://github.com/jonas101201/liquid-calendar/releases/tag/v0.3.9). This update improves the existing 0.3.x interface and editing workflow; it does not complete the planned 0.4.0 flexible-planning milestone.
