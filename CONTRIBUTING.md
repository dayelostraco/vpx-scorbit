# Contributing

Start with the [developer guide](docs/development.md), [architecture and
contracts](docs/architecture.md), and [current compatibility](docs/compatibility.md).
For a new table, follow the [table integration guide](docs/table-integration.md).
The [AI skill](skills/vpx-scorbit/SKILL.md) supports that same workflow; it does
not replace developer review, permission from table authors, or real-game tests.

## Pick a contribution

| Scope | Useful first deliverable |
|---|---|
| Documentation/community | Clarify a confusing step or support claim and verify its links/examples |
| Shared runtime | A small failing offline regression plus the fix; preserve queue/lifecycle invariants |
| ROM adapter | Exact map revision, supported fields and offline decode fixtures; no table support claim yet |
| Table integration | Staged changes and a [validation record](docs/validation-template.md), with untested rows explicit |
| Protocol/QR | Confirmed contract evidence or reproducible rendering measurements, without private payloads |

MM qualification is the immediate target; AFM is the next reuse test. Broader
maps, rich events and other platforms are later work, not promised release dates.
Discuss architectural changes in an issue before spending time on a new transport
or generator format. Offline fixes and documentation can be proposed directly.

## Submit a change

Fork [the repository](https://github.com/dayelostraco/vpx-scorbit), create a focused
branch, and open a pull request against `main`. During private technical review, provide a
patch or review notes through the agreed channel. Contributors do not need a
Scorbit account for offline changes, and AI-generated changes receive the same
human review and test requirements as other contributions.

`main` requires a pull request, an up-to-date successful GitHub Actions `quality`
check and resolved conversations; these protections also apply to administrators.
Force pushes and deletion are disabled. There is no mandatory approving-review
count while the project has one maintainer; this is not independent review signoff.

Explain the before/after behavior and list commands actually run. Link a public,
sanitized validation record for new table claims. Include any known omissions;
do not replace "not tested" with "should work." Use the
[PR template](.github/pull_request_template.md) as the review checklist.

Keep each change focused: explain the problem, resulting behavior, validation,
and any remaining limits. Provide synthetic offline regression fixtures instead
of player data. Never include ROMs, VPX binaries, private research, tokens, keys,
device identities or live pairing QR images in a commit or issue.

Run `scripts/check-quality.ps1` on Windows before requesting review. It exercises
the real VBScript engine as well as Python tooling. First-party Python files
must individually meet 80% line and branch coverage. VBScript requires behavioral
tests; Python coverage does not measure it. Do not remove a safety check or
weaken a gate merely to accommodate a fixture.

Document public interfaces, units, ownership, failure semantics and non-obvious
safety decisions. There is no comment-per-line quota.
The quality runner checks [interface documentation presence](docs/comment-review.md);
reviewers still assess whether those comments are useful and accurate.
Update the compatibility matrix and evidence when claims change. Never present static map eligibility or
synthetic tests as proof that a table works with Scorbit.

Submit original contributions under the root MIT license; preserve the separate
upstream licenses described in [third-party notices](THIRD_PARTY_NOTICES.md).
Do not vendor external code without recording its source, revision and license.
Report suspected credential exposure privately using [SECURITY.md](SECURITY.md).
