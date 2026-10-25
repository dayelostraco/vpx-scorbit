# Sharing readiness

The repository is intended for an initial **experimental technical review**, not
a finished MM/AFM player release. The email draft deliberately reflects that.

## Prepared locally

- MIT license for original code/documentation and explicit upstream notices.
- Contributor, architecture, compatibility, table-integration and security guides.
- Scorbit technical brief and unsent email draft with an unpublished-URL placeholder.
- Commit-pinned Windows CI with read-only repository permission, no persisted
  checkout credentials, native VBScript requirement and checksum-pinned scanners.
- Separate source-only checkout with a fresh Python 3.12 environment. Pinned
  dependency install, 36 tests, per-file Python coverage gates, Ruff, Semgrep,
  Trivy, pip-audit and Gitleaks pass locally. Security executables were supplied
  through explicit paths to isolated developer tooling; no live installation or
  Scorbit account was required. Hosted CI has not yet run.
- A separate initial-commit publication candidate uses a GitHub noreply identity.
  Original development history remains intact locally. The final candidate must
  be used for publication instead of pushing the private development history.

## Before sending the email

1. Publish the reviewed source-only candidate under the agreed repository name.
2. Run the hosted Windows workflow and address environment-specific failures.
3. Enable private vulnerability reporting and appropriate default-branch checks.
4. Replace the email's repository placeholder and confirm its status statements
   still match the current compatibility matrix.
5. Send only after the owner chooses recipients and explicitly authorizes sending.

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
