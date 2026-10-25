# Sharing readiness

The repository is intended for an initial **experimental technical review**, not
a finished MM/AFM player release. The email draft deliberately reflects that.

## Prepared locally

The [public source repository](https://github.com/dayelostraco/vpx-scorbit) was
published on October 25, 2026 from sanitized initial commit `136fb34`. The
[initial hosted Windows run](https://github.com/dayelostraco/vpx-scorbit/actions/runs/40205322892)
passed. This completed the source-review publication milestone, not a player release.

- MIT license for original code/documentation and explicit upstream notices.
- Contributor, architecture, compatibility, table-integration and security guides.
- Scorbit technical brief and unsent email draft with the public repository URL.
- Commit-pinned Windows CI with read-only repository permission, no persisted
  checkout credentials, native VBScript requirement and checksum-pinned scanners.
- Separate source-only checkout with a fresh Python 3.12 environment. Pinned
  dependency install, 36 tests, per-file Python coverage gates, Ruff, Semgrep,
  Trivy, pip-audit and Gitleaks pass locally. Security executables were supplied
  through explicit paths to isolated developer tooling; no live installation or
  Scorbit account was required. The initial hosted Windows CI run also passed.
- A separate initial-commit publication candidate uses a GitHub noreply identity.
  Original development history remains intact locally and was not pushed. Future
  public changes must use the published history and protected PR workflow.
- Interface documentation scan passes: 24/24 scoped Python interfaces and 40/40
  scoped VBS procedures/properties. See [comment review](comment-review.md) for limits.
- Private vulnerability reporting is enabled. Main requires PRs, the up-to-date
  `quality` check and resolved conversations, including for administrators;
  force pushes/deletion are disabled. Mandatory approval count is zero for the
  single-maintainer workflow; the checks are not independent human signoff.

## Before sending the email

1. Confirm the current public commit's hosted checks remain green.
2. Confirm the email's status statements match the current compatibility matrix.
3. Send only after the owner chooses recipients and explicitly authorizes sending.

No ROM/table/helper binaries, private research, pairing QR images or device keys
belong in the public source. Player packages require additional gameplay, VR,
catalog, service-protocol and helper-license qualification described in the
[handoff](HANDOFF.md). The published source should not be advertised as a ready
Scorbit integration for either pilot title.

## Comment coverage

Code comments/docstrings were reviewed for shared boundaries and supplemented
with contracts for decoding, snapshots, clocks, errors and builder side effects.
There is no measured "full comment coverage" claim. Python line/branch coverage
measures tests, not documentation; VBScript behavior is exercised with cscript.
Continue reviewing changed public interfaces and non-obvious decisions rather
than enforcing a quota of comments on individual lines.
