# Community overview and FAQ

VPX Scorbit aims to make Scorbit integration repeatable across ROM-based virtual
pinball tables. A shared client handles common tasks; developers still adapt and
validate the memory layout and table behavior for each title. The project builds
on [Tom Collins's Pinball Memory Maps](https://github.com/tomlogic/pinball-memory-maps)
and the work of its contributors. We are grateful to them, the Scorbit team and
the wider VPX/PinMAME and table-author communities. The
[upstream acknowledgments](../README.md#acknowledgments-and-upstream-projects)
explain each project's contribution and link to the original repositories.

## What exists today?

There is source code, an offline Medieval Madness pilot, a map compiler, automated
tests and developer/AI-assisted integration guidance. The pilot read ROM memory
in attract mode, and desktop QR captures decoded in software. Complete MM gameplay
and Scorbit uploads are not qualified. Attack from Mars is the next target and is
not integrated. VR QR presentation is not implemented; phone scanning is pending.

No player-ready table download, ROM or Scorbit helper executable is included.
This is an independent project, not an official Scorbit release or endorsement.

## What would players install eventually?

The intended experience is a qualified table package plus any approved helper
prerequisites, then linking it in the Scorbit app. Players would not need Python,
an AI account, the development skill, or a separately installed native SDK for
the default helper route. A bare VPX works only where the required helpers already
exist. Helper redistribution and clean-install instructions still need approval
and validation. Players remain responsible for a compatible VPX setup and ROMs
they are authorized to use; this repository does not supply them.

## Will the QR cover the game?

The design calls for a square, unobstructed, temporary code outside active play.
Pairing associates the virtual machine with Scorbit; a player claim associates a
game seat with a player. These are different actions. The host has timeout and
hide-on-pair/claim logic, tested offline; real claim-response behavior is still
being confirmed. Offline MM captures verified a 30-second pairing-display timeout.
VR and physical phone readability must be tested before claiming player support.

## Does the map catalog mean hundreds of supported games?

No. At the pinned upstream revision, 1,589 ROM revisions are indexed and 258
revisions across 63 map files match this compiler's narrow subset. Revisions are
not unique game titles. Eligibility does not prove live scores, events, table
hooks, pairing, uploads or QR display. Use the [compatibility matrix](compatibility.md)
for support claims, and track scores and rich events separately.

## Why helpers rather than the SDK or upstream VPX plugin?

The first target is an existing Windows VPX build with working helper-based
integrations. Reusing that route aims to minimize player setup. The SDK is an
optional experiment, and alignment with Scorbit's plugin plans is a technical
discussion still to be had. The project does not claim to replace those efforts
or that helper and SDK features are equivalent.

## Terminology

| Term | Meaning here |
|---|---|
| VPX / PinMAME | Table simulator / emulator running the original machine's ROM |
| ROM revision | A specific version of a game's original program; different revisions may have different memory layouts |
| Memory map / adapter | Documented field locations / code that turns those bytes into validated game state |
| Attract mode | Idle presentation between games; stored scores here do not prove new gameplay scoring |
| DMD | The game's dot-matrix score/message display |
| VPIN catalog entry | Scorbit's virtual title identity, distinct from the physical machine listing |
| OPDB identifier | A pinball database identity used in the helper workflow; Scorbit must confirm the appropriate value |
| Pairing / claim | Linking a virtual machine / associating a game seat with a player |
| AI skill | Reusable developer instructions; no AI runs inside the table |

## How can the community help?

Developers can reproduce offline tests, review the protocol, improve QR rendering
or contribute carefully scoped adapters. Table authors can document authorized
table revisions and supply sanitized validation evidence using the
[integration guide](table-integration.md). Documentation and accessibility feedback
are useful too. There is no broad player beta yet or promised release date.

Scorbit can help establish the test/onboarding process, confirm the proper VPIN
identities and clarify helper contracts and redistribution. Read the
[technical brief](scorbit-review.md) for the specific questions. Public issues
should contain no tokens, account/device state or live pairing/claim QR images.

## Suggested public description

> VPX Scorbit is an independent experimental project developing shared tools and
> an embedded runtime for ROM-based VPX table integrations. Medieval Madness is
> the offline pilot and Attack from Mars is planned next. It is seeking technical
> collaboration; no finished MM/AFM Scorbit table or VR support is available yet.

Before a wider announcement, use [sharing readiness](sharing-readiness.md).
Before a player release, require the table-specific validation record and
service qualification. Passing code tests alone does not satisfy that release gate.
