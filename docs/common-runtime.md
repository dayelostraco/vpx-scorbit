# Common helper implementation

Decision: one versioned integration source, built into each VPX, and one shared
helper bundle in the installation's Tables directory. No Python, native SDK,
PuP installation, or AI skill is intended as a player prerequisite. The native
QR display implementation must prove that PuP/QRView can be omitted before we
remove compatibility helpers from the bundle.

## Responsibilities

These are intended component boundaries, not a list of completed features.
Token refresh/reconnect, real claims/uploads and VR rendering remain unqualified
or unimplemented. See [compatibility](compatibility.md) for current status and
[protocol](protocol.md) for implemented behavior and service assumptions.

- Common client: helper discovery, authentication, heartbeat, session transport,
  player claiming, final-score ordering, reconnect handling, and local state.
- Common lifecycle: validated start/turn/ball/finish transitions; never finish
  on missing telemetry, reset, or table exit. No upload from synthetic tests.
- Common QR renderer: links supplied by the client, quiet zone, screen-aligned
  desktop presentation, verified VR presentation, timeout, hide-on-claim,
  manual recall. No per-table copy of the renderer.
- ROM adapter: exact supported revisions, memory layout, encoding, current
  scores/player/ball/game-over, and independently verified event signals.
- Table adapter: initialization, polling timer, shutdown, display objects and
  positioning, launch guards, and verified Scorbit catalog identity.

Client and renderer must consume adapter state, never arbitrary globals such
as Score(), Balls, or PlayersPlayingGame from the donor table. Each adapter
supplies four score slots plus participating player count. Decode five-byte BCD
without signed 32-bit overflow. Unknown fields remain unknown, not zero events.

State belongs to the installation and correct table/device identity. Never
share a token/session across unrelated tables or ship developer pairing state.
Helper location is installation-relative; no hard-coded developer drive paths.
Preserve existing working table identities when migrating a deployed client.

## Build and distribution

Keep the common source in this repository. Generate an embedded, versioned
script during table assembly: players receive it inside the VPX, with no loose
VBS override to install. Fixes are made once in source, then tables rebuilt;
embedded scripts do not automatically update already downloaded tables.

`packaging/helpers.lock.json` pins the actual helper bytes from the seven-table
installation. `tools/package_helpers.py` creates an explicit local development
bundle from those files. It fails on missing/changed files and existing output,
and includes only the allowlisted executables and manifest. It never copies
an entire table directory or executes a helper. QRView remains a compatibility
component pending native-renderer validation. Public distribution terms have
not yet been verified; this bundle is not a public release.

A release can put the VPX and common helpers in one download. Existing users
reuse matching helpers. Installation must not overwrite a different helper
version silently. Ship a manifest identifying runtime, adapter, helper hashes,
table revision and supported ROM revisions; do not bundle ROMs or private state.

## Scaling and acceptance

Memory-map availability is discovery, not a compatibility claim. Track each ROM
as discovered, decoder eligible, offline tested, gameplay validated, and service qualified.
Record live-memory observations as evidence, not a substitute for full gameplay.
Scores/lifecycle and rich events have separate evidence. Map audits or historic
high scores must not be mislabeled as current-game events. Share a ROM adapter
between revisions only after verifying that their layouts and semantics match.

First qualify MM with this common runtime; then use AFM to expose accidental
MM dependencies. Respect AFM's existing effective sidecar script. Neither table
is currently qualified. Hundreds of maps do not imply hundreds of tested games.

The common VBScript modules and MM offline builder now exist in vbs/ and
tools/build_common_pilot.py. The player pilot uses no Python bridge. Scores and
finish are queued together; busy/error responses retain the head. A real
read-only heartbeat and offline failure tests pass, but live entry/claim schema,
retry semantics, catalog identities, full gameplay and VR remain unqualified.
See [research](research.md) for dated evidence. The older Python pilot is diagnostic only.
