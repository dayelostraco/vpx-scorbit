# Research and evidence - October 25, 2026

This is historical development evidence. Private captures/backups and the
recovered session archive are not public repository dependencies. Use
[compatibility](compatibility.md) for qualification claims and
[developer setup](development.md) for reproducible offline work.

## Chosen implementation

The user selected the established sToken/sQRCode helper approach, packaged with
embedded VBScript. No Python or native SDK installation is a player requirement.
The newer SDK remains an optional experiment for specific additional features.
The common runtime is in vbs/; tools/build_common_pilot.py embeds it in a staged
VPX. The earlier file/Python bridge is diagnostic history, not the player runtime.

## Comparison with recovered prior research

The supplied bundle was recovered from Downloads/scorbit-vpx-lab-research and read;
its documents are archived locally in ignored docs/prior-research, not distributed.
It correctly identified the
WPC 12K layout, extra PinMAME trailer, live Controller.NVRAM route, invalid BCD
risk, four-seat parser limitation, and the need for conservative game lifecycle.
We retain those findings and use the pinned upstream Python decoder as a test
reference. Our VBScript generator compiles only explicitly supported map fields;
it does not attempt to port the whole map schema into a second parser.

The earlier proposal preferred an external SDK companion. That is now optional:
the user prioritized downloading a table package and using the existing helpers.
This reduces player setup and matches the seven paired tables, while requiring
separate validation of the older protocol's event and claim capabilities. Native
SDK features must not be assumed to exist in the helper protocol.

Our live tests advance beyond the prior research: this installation returns
12,334-byte snapshots, and the embedded VBScript pilot runs on its existing VPX
build. Full gameplay remains unverified; retained attract scores are not proof
of a newly scored game.

## Pinned sources

- Memory maps: https://github.com/tomlogic/pinball-memory-maps/tree/f0c422099f0b50b69bfdf6d071a6653a8b25a6fd
  Unchanged MM map and platform metadata; ODbL/DbCL licenses retained in maps/.
- Python reference decoder: py-pinmame-nvmaps at
  4a8d77c39badb8fd893672238b90b541ed056581, vendored unchanged with its license.
- Optional SDK research: 8ce6eb4f8c6e73ccec0a4c139650da0e0a46214e, still VERSION
  2.0.4, contains post-tag Windows/API fixes. Release tag 2.0.4 is instead
  807ad452cae989e9b968c3ba743d1df10eaa9db2. Do not equate the version label with
  identical API capabilities. No matching native SDK was installed/tested here.
- Legacy PinMAME NVRAM getter:
  https://github.com/vpinball/pinmame/blob/ecd032e55481b261cce4820b53fd28fe478c70b4/src/win32com/Controller.cpp
- VPX rendering inspected at af26b2d9392b4c9ec3e3edff4bbd69562085a44c. On this
  build the flasher property is DMD, not IsDMD; TablesDirectory resolves the
  installation helpers without embedding this PC's drive path.

## Installed target

Medieval Madness VPW 1.1 / mm_109b; VPX 10.8.1.5436.af26b2d93. Original table,
ROM ZIP, table INI, global VR INI and deployed launcher configuration preserved.
Input hashes are in profiles/medieval-madness.json. Tests use the existing
legacy COM controller; no PinMAME/backend or VPX upgrade.

The snapshot comprises 12,288 WPC bytes and 46 PinMAME trailer bytes. Attract
contains game_over=1, count=1, player=1, ball=1, and P1=24,697,230 from a prior
game. Tests also observed boot state with player/ball zero; it must be rejected.
See mm-capabilities.md for field-by-field status and unsupported rich events.

## Verified in this development pass

- Actual Windows VBScript tests for large BCD scores, four distinct seats,
  invalid digits/bounds, ROM identity, lifecycle settling, resets and gaps.
- JSON parsing with punctuation/Unicode names and malformed response rejection.
- Fake HTTP tests retain final scores through a busy request, 503, timeout,
  subsequent game and authentication rejection; no test traffic is sent.
- The common HTTP client authenticated a real READ-ONLY heartbeat for the already
  paired Blood Machines device: HTTP 200, machine assigned, zero queued entries.
  The new helper bootstrap also authenticated the same existing BM device and
  generated a claim QR matching the installed table, without changing its identity.
  No game score was submitted. Entry/claim response shape and retry semantics
  still need real service validation.
- Staged mm-common-v1.vpx runs embedded common VBScript without a Python bridge,
  has clean startup capture logs, and its offline QR decodes from the full
  5120x2160 and 1920x1080 images. It is screen-aligned, outside the playfield and DMD. Backdrop
  depth bias must be zero; -10000 hid the backdrop. Expanding small PNG pixels
  before DMD rendering eliminated decoder failure caused by the dot pattern.
- The embedded VPX was tested with no sidecar override. A longer capture shows
  an initially decodable QR disappearing after the 30-second wall-clock timeout.
- Actual phone and headset scanning remain untested. The current common pilot
  deliberately hides its desktop-only QR in VR rather than claiming VR support.
- Static audit: 1,589 ROM revisions (excluding index metadata); 258 across 63 map files match the current
  decoder subset. This does not qualify their gameplay or uploads.

## Catalog dependency

Authenticated read-only /api/machines/?search= queries returned six physical or
remake MM entries and four physical or remake AFM entries, with no VPIN entries.
Guardians has separate VPIN entries, including 2108 used by the installed table.
Do not substitute physical MM 1389 or AFM 1056 for a verified VPIN identity.
scorbit-catalog-request.txt is a draft for the user to send; nothing was sent.

The common pilot has networking disabled and catalog ID zero. SDK provider/key
provisioning is NOT a prerequisite for this chosen helper route; the correct
helper-compatible VPIN catalog identity and redistribution terms still matter.

## Existing-table fixes

GetName used the wrong cache index in Blood Machines, CyberRace and SpongeBob;
these are corrected and tested for seats 1-4. BM/Sponge now use per-table token
paths. All three startup captures are clean and remain paired/authenticated.
The other four already have the correct name index. Original VPX backups and
hash manifests are in Staging/2026-10-24-scorbit-common-fixes and
Backups/Scorbit-CommonFixes-20261024. Author-ready patches/notes are in Downloads.
No identities changed, no re-pairing required, no synthetic score uploads.

All seven clients also had eager 10,000,001-slot log arrays. These now allocate
1,024 slots only on the first logged row and grow as needed. An isolated actual
client-class measurement saved about 229 MiB of private memory; 4,097-row
retention/reset tests passed. All seven staged startups and paired heartbeats
passed; embedded and installed bytes were verified. Backups are under
Backups/Scorbit-LogBuffer-20261025; author ZIP is Scorbit-author-fixes-2026-10-25.zip.
This does not constitute a full game-log upload or headset test.

## Outstanding qualification

Normal-play focus was unavailable because the Windows computer-use native pipe
could not connect. Attract-mode scripted coin/start inputs did not establish a
new game. The scoped diagnostic process was closed and saved ROM state restored.
Do not count these attempts as full-game validation. MM still needs real scoring,
1-4 players, turns/balls, extra balls, tilt, final bonus, finish, reset/exit, and
claimed-player upload checks. Rich modes need verified current-game signals.

VR presentation and phone scanning remain open. AFM's effective script is a live
sidecar using afm_113b; preserve it. Its map matches the decoder subset, but AFM
integration/gameplay testing follows MM qualification as requested.
