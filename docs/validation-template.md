# Table integration validation record

Copy this template into a new, clearly named document for a proposed integration.
Fill unknown items with **not tested** or **not applicable (reason)**. Keep private
logs and player state outside Git. This is an evidence format, not certification
by Scorbit, a table author, or the upstream map project.

## Identity and scope

| Item | Recorded value |
|---|---|
| Table title, author and version | To be recorded |
| Original table / effective script SHA-256 | To be recorded; note embedded versus sidecar |
| ROM revision / ROM ZIP SHA-256 | To be recorded; do not attach ROM |
| VPX build, OS, PinMAME/backend | To be recorded |
| Map repository commit and map path | To be recorded |
| Integration commit, profile and build manifest | To be recorded |
| Helper versions/hashes | To be recorded; no tokens or device identifiers |
| Approved VPIN catalog ID / OPDB | Unconfirmed; never use a physical ID as a substitute |
| Qualified features | None until evidence below supports them |
| Known limitations | To be recorded |

## Evidence matrix

Record date, tester, configuration and sanitized evidence reference for each row.
Separate software simulation, observed gameplay, camera/headset testing and
service-side acceptance. A successful HTTP response alone is not upload acceptance.

| Scenario | Expected result | Result / evidence |
|---|---|---|
| Exact ROM / invalid map / invalid BCD | Correct data accepted; unexplained layouts rejected | Not tested |
| Boot, attract, fresh player-1/ball-1 start | No synthetic game from boot or late attach | Not tested |
| 1–4 players, turn and ball changes | Every participating score/seat matches the DMD | Not tested |
| Bonus and game end | Stable final scores included with one intended finish | Not tested |
| Extra balls and tilt | Correct lifecycle; rich event only if separately verified | Not tested |
| Reset, exit, lost telemetry, clock gap | Abort locally; no fabricated completed game | Not tested |
| Network timeout, lost response, retries | Behavior matches agreed Scorbit contract; no unintended duplicate session | Not tested |
| Authentication expiry / restart | Known recovery behavior; no identity leakage | Not tested |
| Pairing and all seat claims/unclaims | Correct machine/seat and reliable hide/refresh behavior | Not tested |
| Desktop QR, multiple resolutions | Square, clear quiet zone, no obstruction; software decode AND phone scan | Not tested |
| VR QR in headset | Readable by camera in intended use; no skew/occlusion | Not tested |
| Timeout/manual recall | Pair/claim timeout and recall respect safe display windows | Not tested |
| Fresh helper installation / existing helpers | Approved package, no silent overwrites or copied device state | Not tested |
| Release artifact / rollback | Embedded source matches manifest; specific backups restore prior installation | Not tested |

Add a row for each rich mode/event with its observed signal, encoding, reset
behavior, Scorbit mapping and evidence. Historical audits and score deltas alone
do not establish current-game events.

## Qualification decision

State one level: discovered, decoder eligible, offline tested, gameplay validated,
or service qualified. List supported display modes separately. Explain exactly
which evidence supports promotion and who reviewed it. Update
[compatibility](compatibility.md) only for the features and revisions demonstrated.
Record unresolved requirements instead of checking off the entire table.
