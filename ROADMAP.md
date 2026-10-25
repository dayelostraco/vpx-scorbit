# Roadmap

This is an experimental technical preview, not a player release. Milestones are
ordered by dependencies, not promised calendar dates. Estimates should follow
agreement on the Scorbit test route and hands-on gameplay/VR investigation.
Use [compatibility](docs/compatibility.md) for evidence already obtained.

| Milestone | Acceptance criteria | Status / dependencies |
|---|---|---|
| Public technical preview | Sanitized source, MIT/upstream notices, repeatable local checks, passing hosted Windows CI, private security reporting and protected main branch | Published October 25, 2026; initial hosted run passed and repository protections verified |
| Scorbit technical agreement | Correct VPIN identities, approved test process, confirmed claim/entry/retry contracts and helper distribution terms | Requires Scorbit collaboration; no requests sent automatically |
| MM gameplay and service qualification | Complete scoring, 1–4 players, bonus/final scores, tilt/extra balls, claims, uploads, reset/exit and failure/retry evidence | Offline pilot exists; real gameplay and service validation pending |
| Desktop and VR QR qualification | Square/unobstructed output, actual phone and headset scanning, safe display windows, timeout/hide/recall | Desktop software decode only; VR surface not implemented |
| AFM reuse validation | Separate adapter/table wiring using common runtime; same validation record; no copy of a private client or identity | Follows MM qualification; map eligible but table not integrated |
| Broader ROM and feature support | Verified adapters for additional layouts/revisions; individually mapped rich events with agreed Scorbit semantics | No automatic claim of support for the upstream catalog |

## Candidate improvements

Authentication renewal, persistent pending entries and server-confirmed duplicate
handling are reliability work to resolve before a player release. Rich modes,
additional ROM families and an optional native SDK route are future work whose
scope depends on evidence and a concrete user benefit. The SDK is not a required
upgrade merely because a table is complex or non-ROM.

Do not remove existing safety guards to reach a milestone. Each table needs its
own [validation record](docs/validation-template.md), and each released artifact
needs source/helper hashes and rollback instructions. Publication of source is
not completion of any gameplay, service or headset milestone.
