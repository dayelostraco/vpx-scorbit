---
name: vpx-scorbit
description: Investigate and stage Scorbit integrations for ROM-driven VPX tables using the shared experimental VBScript runtime, verified ROM memory, and existing helpers. Use for table adapters and validation; not an automatic installer or a claim of supported tables.
---

Use this repository's tools and evidence to adapt an existing table, starting
with Medieval Madness. Read [the project README](../../README.md) and
[compatibility findings](../../docs/research.md) before selecting a transport.
The repository root is two directories above this file (resolve junctions).
Read the [integration guide](../../docs/table-integration.md) for deliverables and
the [validation template](../../docs/validation-template.md) for evidence levels.
The helper-based MM builder is offline; AFM and VR QR remain unimplemented.

## Establish the actual target

Read the installation's AGENTS.md and existing notes. Identify the exact VPX
executable/build, table and embedded script hashes, ROM ZIP/revision, sidecar
script overrides, and active PinMAME backend. Keep the user's working build.
Extract scripts to staging: a .vbs beside a live .vpx overrides its script.
Never distribute table/ROM assets or device/provider credentials with patches.

Distinguish the older embedded VBScript Scorbit class plus sToken/sQRCode
helpers from native SDK 2.0.4. Existing helper authentication is not evidence of
SDK 2.0.4 provisioning. Only for the optional SDK route, check native-library
availability and provider identity early. Public sample credentials describe the upstream staging example, not the
user's production provider or the table's machine identity.

## Prove ROM telemetry before connecting scores

Look up the exact ROM revision in the memory-map index; record the map commit
and its license. Identify CPU-address versus file-offset translation, encoding,
byte order, game-over semantics, seats, current player, ball, and final scores.
Do not assume an NVRAM file on disk updates during play. Probe the existing
table's Controller.NVRAM and compare decoded fields with the actual DMD.

The current decoder intentionally supports only the WPC 12K pilot's required
field encodings. Reject unsupported map semantics until implemented and tested.
Use CDbl for five-byte BCD arithmetic: these integer values fit exactly in
Double but exceed signed 32-bit CLng. VBScript has no CDec conversion. Never infer a mode or achievement solely from a score jump.
Rich events need their own documented and validated RAM/switch/lamp evidence.

Validate attract, fresh game, 1-4 seats, turns, ball changes, extra balls, tilt,
bonus/final scores, restart, and early exit. Simulated inputs stay offline.
Telemetry gaps, ROM reset, or application exit must not submit completed games.
The pilot requires attract before a fresh game and rejects score regression;
late attachment and score rollover are not currently supported.

## Select the player runtime

Use the embedded VBScript Scorbit client with the established sToken/sQRCode
helpers by default, as explicitly requested by the user. Keep ROM decoding in
the table runtime; Python may generate and validate code during development but
must not be required for players. Reuse client behavior, never another table's
identity or credentials. Test both existing-helper and clean-package scenarios.
Only promise a single-file VPX download when its helper prerequisites exist.

Keep the native SDK route optional for a demonstrated feature need. The
following SDK-specific guidance applies only to that experimental route.

## Optional SDK

Keep SDK networking outside VPX's script thread. Feed snapshots into the
bridge; update final scores BEFORE set_game_finished(), which commits
immediately. Bind stable provisioned identity to the correct table/provider;
never borrow another table's machine ID or authentication material.

Persist SDK device keys locally outside Git. Copy callback data before returning
from native callbacks. Pairing links come from pair_deeplink; seat claim links
come from PlayersUpdated. Generate QR images from those exact links, with a
quiet zone. Hide absent/claimed codes and validate refresh behavior.

## Shared QR presentation

For the default helper route, use helper-generated images and the host's
pairing/claim state; do not assume SDK callbacks exist in the legacy protocol.
See [protocol assumptions](../../docs/protocol.md), especially claim-seat mapping.
Keep QR overlays temporary and out of active play. The MM pilot uses 30 seconds
for pairing and 15 for claiming, with a table option to show again. Its shooter
and launch switch guards are MM-specific; verify equivalents for other tables.

On the proven Windows BGFX build, WIA.ImageFile -> ARGBData -> a dedicated
flasher's DMDColoredPixels works. The script property is **DMD**, not IsDMD.
Use DMDWidth/DMDHeight. World-space panels used depth_bias -10000; screen-space
backdrop panels require zero on the tested build. Expand small PNG pixels before
DMD rendering and decode the actual capture; a visible QR can still be unreadable. Do not rely on QRView screen
capture or legacy FlexDMD pixel-copy APIs. This WIA path is Windows-specific.

## Stage, verify, and report

Use tools/build_common_pilot.py for the pinned offline embedded-runtime MM pilot.
tools/stage_mm.py is the historical Python-bridge diagnostic, not the default.
Both builders guard one script revision. Adapt hooks explicitly for
other versions; don't broadly regex-rewrite game logic. Test a staged copy with
an isolated desktop INI, retaining live VR, frontend, and unrelated settings.
Use the existing QOI-capable recorder where available. Inspect runtime logs
AND captures; clean logs alone do not prove a QR panel is visible.

Keep offline display-test QR codes clearly separate from real SDK pairing.
Require square, front-facing QR output with no perspective skew or scene
occlusion. Decode captured QR output, then verify phone scanning in desktop
and native VR use. Do not claim headset or camera testing from desktop captures.
Back up and hash affected files before live deployment; provide exact rollback.
Report each level independently: decoder tests, live-memory observation, game
lifecycle validation, QR visibility, chosen-transport authentication, pairing, claimed-player
game upload, and headset play. Never label a staged/offline pilot complete.

## Reuse across ROMs

Follow [common runtime boundaries](../../docs/common-runtime.md). Change shared
source and rebuild embedded scripts; do not fork the client per table. Use the
hash-pinned helper packager for local bundles. A discovered map is not a tested
integration: record ROM-level and feature-level validation independently.

Use tools/build_common_pilot.py for the current offline embedded-runtime MM
pilot. tools/stage_mm.py is the earlier Python-bridge diagnostic. Require a
verified VPIN catalog ID; the discovered physical MM/AFM IDs are not substitutes.
The current shared pilot hides desktop QR in VR pending proper validation.
