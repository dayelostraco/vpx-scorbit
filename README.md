# VPX Scorbit

An experimental framework for adding Scorbit score tracking to ROM-based
Visual Pinball X (VPX) tables. It provides a shared embedded VBScript runtime,
ROM-adapter generation and validation tools, and an AI-assisted integration
workflow that developers can follow with or without an AI assistant.

The goal is to implement the common Scorbit behavior once, then adapt and
validate each table's ROM data and display hooks. The first target is Medieval
Madness (`mm_109b`); Attack from Mars (`afm_113b`) follows MM qualification.
The tested pilot build is Windows VPX 10.8.1.5436, not every VPX 10.8.1 build.

**There is no finished Scorbit-enabled MM or AFM table to download here.**
MM has an offline pilot; AFM has static decoder eligibility only. There are no
qualified gameplay uploads or working VR QR surface yet. See the
[compatibility matrix](docs/compatibility.md) for exact evidence and limits.

## Start here

| Reader | Start with | What you can do now |
|---|---|---|
| Scorbit developer | [Technical review brief](docs/scorbit-review.md), [protocol implementation](docs/protocol.md) | Review identity, payload/claim assumptions, retries and the proposed onboarding process |
| Scorbit community manager or player | [Community overview and FAQ](docs/community.md) | Understand the goals, current status, intended setup and what can accurately be announced |
| Open-source contributor | [Developer guide](docs/development.md), [contributing](CONTRIBUTING.md) | Run offline tests, generate a decoder, improve the shared implementation or documentation |
| Table author/integrator | [Table integration guide](docs/table-integration.md), [validation record](docs/validation-template.md) | Investigate a map and build evidence for a table-specific adapter |

The [documentation index](docs/README.md) separates current guidance, review
material and historical evidence. No Scorbit account or ROM is needed for the
[offline developer walkthrough](docs/development.md#first-offline-exercise).
The [roadmap](ROADMAP.md) lists milestones and acceptance criteria without
unsubstantiated dates; [changelog](CHANGELOG.md) records the unreleased preview.

## How it works

PinMAME runs the table's original ROM. The table's existing controller exposes
memory; a ROM map tells the adapter where scores, player, ball and game state
live. The shared runtime validates those values, tracks game transitions, queues
score messages and manages temporary QR display using the established helper
approach. Table-specific integration supplies the timing and display hooks.

Pinball Memory Maps provides field descriptions, not Scorbit integrations or
an automatic table installer. The compiler currently accepts a narrow WPC-12K
subset. Rich modes/events require additional verified signals and agreed
Scorbit semantics. See [architecture](docs/architecture.md) for contracts.

## Player experience and default architecture

The intended default is a table package using the embedded VBScript Scorbit client
and existing sToken/sQRCode helpers, informed by seven existing integrations used
as development references. After release qualification, players would download
the table package, open it in their working VPX setup,
link it to their Scorbit app/account, and play. No Python environment, SDK build,
or provider configuration is a player installation step for this route.

A single VPX file is sufficient only when the required helper files already
exist. A clean installation must receive the required helpers through an
appropriate package or clearly documented prerequisite. Verify redistribution
terms before bundling executables; do not silently download or execute them.
Never package another player's tokens, device state, or ROMs.

QR codes must be square, front-facing, unobstructed, and readable in desktop
and VR use. Hide codes after pairing/claiming and after a timeout, with a way
to show them again. Validate the actual output with a QR decoder and a phone;
visibility alone is not proof of scannability.

## Current status

Live MM ROM memory access in attract mode and offline decoding are proven.
Full game lifecycle, correct Scorbit
machine identity, authentication/upload, and desktop/VR QR scanning remain
release requirements. Current staged artifacts are an earlier diagnostic pilot,
not the default player package. Live tables and launcher settings are preserved.

The [reusable skill](skills/vpx-scorbit/SKILL.md) describes investigation and
validation. [Research](docs/research.md) records evidence and unresolved issues.
Developers can start with [contributing](CONTRIBUTING.md), the
[architecture](docs/architecture.md), [table integration guide](docs/table-integration.md),
and [compatibility matrix](docs/compatibility.md). Scorbit reviewers can use the
[technical brief](docs/scorbit-review.md).
The included MM map and platform metadata are in `maps`; the full upstream
catalog is not bundled. Player runtime source is in `vbs`; Python reference
decoding and tests are in `vpx_scorbit` and `tests`. Python is developer tooling only for the
planned helper-based player package.

## Optional SDK route

SDK 2.0.4 remains an experimental alternative for features that justify it,
including possible complex non-ROM tables. Complexity or absence of a ROM
alone does not require that SDK. Choose it only for a concrete feature benefit
and validate its deployment requirements independently.

The earlier Python/native SDK prototype and its setup are retained in
[experimental SDK pilot notes](docs/experimental-sdk-pilot.md). Those instructions
are not the default player installation instructions. No native SDK has been
installed or successfully exercised by this project.

See [common runtime and packaging](docs/common-runtime.md) for the shared-client,
ROM-adapter, and helper-bundle design. The local helper bundler and embedded VBScript common-runtime pilot are
implemented. Production gameplay, claiming and VR qualification remain open.

## Build an offline common-runtime pilot

Start with [developer setup](docs/development.md). This advanced build requires
your own authorized table extraction and a trusted vpxtool executable. The input
script must exactly match [the MM profile](profiles/medieval-madness.json); a
similarly named table or different revision will be rejected. No table or ROM
is provided here. The commands below use placeholders you must replace.

```powershell
.venv/Scripts/python -m unittest discover -s tests -v
.venv/Scripts/python tools/build_common_pilot.py --extraction <original-mm-extraction> --output <new-staging-directory> --vpxtool <vpxtool.exe> --test-qr <offline-test.png>
```

Use a separate copy of the table INI and isolated desktop global INI for capture.
The generated VPX embeds all runtime scripts and needs no Python companion.
The diagnostic builder cannot enable network uploads. Its optional QR image is
an offline test asset, not a real Scorbit pairing code. Desktop captures have
decoded successfully in software; physical phone scanning is unverified.
VR QR is hidden pending implementation and headset validation.

See [MM capabilities](docs/mm-capabilities.md), [map audit](docs/map-coverage-notes.md),
and [catalog request draft](docs/scorbit-catalog-request.txt).

Current checkpoint and remaining qualification: [handoff](docs/HANDOFF.md).

## Acknowledgments and upstream projects

This project builds on substantial work by the pinball developer community.
Thank you to **Tom Collins (tomlogic) and the contributors to Pinball Memory
Maps and py-pinmame-nvmaps**: their documented memory layouts and readable
decoder make it possible to build on existing knowledge instead of rediscovering
each ROM's data. Their authorship and licenses remain part of this project.

Thank you to **the Scorbit team at Spinner Systems and its contributors** for
the Scorbit ecosystem and published integration projects. We appreciate the
opportunity to build toward that ecosystem and discuss alignment with their work.

| Upstream project | Its role here |
|---|---|
| [Pinball Memory Maps](https://github.com/tomlogic/pinball-memory-maps) · [ROM catalog](https://github.com/tomlogic/pinball-memory-maps/blob/main/maplist.md) | Source of ROM field descriptions; selected map/platform data is included with its ODbL/DbCL notices |
| [py-pinmame-nvmaps](https://github.com/tomlogic/py-pinmame-nvmaps) | Tom Collins's parser, vendored unchanged as the Python reference decoder with LGPL notices |
| [Scorbit SDK](https://github.com/scorbit-io/scorbit_sdk) | Basis of the separately identified optional SDK experiment; not the default player runtime |
| [Scorbit VPX plugin](https://github.com/scorbit-io/vpx-scorbit-plugin) | Related upstream integration effort reviewed for possible alignment; its code is not bundled here |
| [Visual Pinball](https://github.com/vpinball/vpinball) and [PinMAME](https://github.com/vpinball/pinmame) | The simulator and ROM-emulation foundation on which table integration depends |

We also thank the table authors and maintainers of existing Scorbit integrations
and helpers whose working implementations informed this approach. Their table
artwork, scripts, ROM assets and helper binaries are not ours to relicense.
Helper authorship and redistribution terms still need confirmation before any
binary package; acknowledgment does not imply permission or endorsement.

Exact source revisions and component terms are recorded in
[sources.lock.json](sources.lock.json) and [third-party notices](THIRD_PARTY_NOTICES.md).
Please preserve these credits and upstream notices when reusing the project or
generating table integration material.

Original code and documentation are MIT licensed; see [LICENSE](LICENSE) and
[third-party notices](THIRD_PARTY_NOTICES.md) for upstream components. This is an
independent project and does not imply Scorbit endorsement.
