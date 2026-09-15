# ADR-001: License

## Status

Accepted, 2026-09-03. Supersedes the initial Unlicense that shipped in the
GitHub repo creation.

## Context

The program brief specified MIT. GitHub's repo-creation flow installed the
Unlicense by default. Aayush directed on 2026-09-03: use the most restrictive
option among GitHub's preexisting licenses.

GitHub's license picker (backed by choosealicense.com) offers a small set of
standard licenses. Ranked roughly by restrictiveness:

- Unlicense, 0BSD, MIT, BSD-2/3, Apache-2.0: permissive, allow closed-source
  derivatives.
- LGPL-2.1 / LGPL-3.0: weak copyleft, library boundary carve-out.
- MPL-2.0: file-level copyleft.
- GPL-2.0 / GPL-3.0: strong copyleft, source disclosure required for
  distributed derivatives.
- **AGPL-3.0: strongest copyleft.** Extends GPL-3.0's source-disclosure
  requirement to network use, so a hosted service built on NEUROSPINE must
  publish its source to its users.

## Decision

Adopt **GNU Affero General Public License v3.0** (AGPL-3.0).

Rationale:
- Strongest of the preexisting GitHub options, as requested.
- Closes the SaaS loophole in GPL-3.0. A vendor cannot silently host a
  derivative of NEUROSPINE as a closed API.
- Compatible with the program's stance that neural-grounded auditing
  instruments should not be quietly commercialized without upstream benefit.

`LICENSE` file replaced with the AGPL-3.0 text from GitHub's `licenses`
endpoint (`gh api /licenses/agpl-3.0`).

## Consequences

- **Downstream friction is real.** Anyone distributing or network-hosting a
  derivative must publish source, license under AGPL, and preserve notices.
  This is the intended cost.
- **Some collaborators cannot merge AGPL code into their internal or
  differently licensed projects.** If a specific partner needs a permissive
  cut, that requires a separate contributor agreement or a dual-license ADR.
- **Compatible with GPL-3.0 derivatives one-way** (AGPL to GPL is not
  freely permitted; GPL-3.0 to AGPL is via the compatibility clause). Third
  party inclusion needs a license audit.
- Reversing this decision on a merged public commit is difficult without a
  contributor sign-off; downstream forks made under AGPL retain their rights.
- Academic citation remains the primary attribution mechanism; AGPL adds a
  legal one on top.

## Follow-ups

- Remove the license-confirm bullet from `issues_to_open.md`.
- Add a `NOTICE` file if any third-party code with attribution clauses is
  bundled.
- Add an `AGPL compliance` section to `instrument/README.md` once code lands.
