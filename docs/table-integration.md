# Integrating a ROM-based VPX table

This is a developer procedure, not a promise of automatic integration. The
current builder is MM-specific and offline. Do not rename its ROM constant to
produce an apparently supported table. The [shared skill](../skills/vpx-scorbit/SKILL.md)
guides the same investigation for AI-assisted work.

## Before starting

Complete the [offline exercise](development.md#first-offline-exercise) first.
Actual table work adds your authorized table/ROM, exact build information,
trusted vpxtool and isolated staging. Only the MM map and platform metadata are
included; obtain other maps from the pinned upstream checkout. Service testing
adds an approved identity/test route. Start a [validation record](validation-template.md)
and mark unknown results as not tested. This is an engineering workflow, not an
automated all-table installer.

## Integration procedure

1. **Inventory and preserve.** Record exact VPX build, table hash, effective
   embedded/sidecar script, ROM ZIP/revision and PinMAME backend. Read installation
   notes. Back up the specific files and work in isolated staging with separate
   INIs. A matching `.vbs` can override the embedded script.
2. **Inspect the upstream map.** Pin its commit and licenses. Confirm RAM versus
   serialized file offsets, byte order, BCD validity, player/ball semantics and
   score slots. Do not mistake cumulative audits for current-game events.
3. **Compile or implement an adapter.** `tools/generate_rom_adapter.py` accepts
   only its narrow WPC-12K subset. Unsupported mappings must fail explicitly.
   Add offline boundary and malformed-input tests before extending encodings.
4. **Prove live reads offline.** Sample `Controller.NVRAM` and compare all player
   scores and states to the actual DMD. Files on disk may lag gameplay. Keep raw
   captures private and use synthetic values for committed regression tests.
5. **Wire the host.** Create table-specific init/timer/exit/option hooks, a safe
   shooter-window predicate and QR render objects. Start only after the controller
   is ready. Guard exact source hashes and refuse duplicate integration.
6. **Qualify lifecycle.** Test fresh start, 1–4 players, turn/ball changes, bonus
   settlement, tilt, extra balls, restart, reset, exit, telemetry loss and late
   attach. Final scores must precede finish. Abort is not a completed game.
7. **Establish service identity.** Obtain the proper VPIN machine ID, OPDB value
   and approved test process from Scorbit. Never substitute a physical title ID.
   Confirm the legacy player-claim schema, retry behavior and accepted events.
8. **Validate QR presentation.** Verify payload with a decoder, then scan with an
   actual phone in desktop and VR. Check square geometry, quiet zone, contrast,
   occlusion, safe location, timeout, hide-on-pair/claim and manual recall. The
   current renderer intentionally hides in VR; implementing that surface is open.
9. **Validate the approved service route.** Keep synthetic tests offline. Under
   Scorbit's agreed process verify authentication, seats/claims, final upload,
   outages, retries and duplicate handling. Do not infer acceptance from HTTP 200
   alone without checking the resulting session/account state.
10. **Package and document.** Embed the common runtime, pin helper hashes, retain
    provenance, and exclude ROMs, device state and private QR images. Verify
    redistribution permissions and table-author consent. Record the qualification
    matrix and restore procedure before a release.

Rich events need their own verified memory/switch/lamp evidence and a confirmed
Scorbit semantic mapping. A score delta or mode-looking text is insufficient.
Mode/event support across the upstream catalog is future work, not a current
capability of the MM core-score adapter.

## Concrete outputs for a new table

| Layer | Deliverable |
|---|---|
| Source identification | Profile with exact script/table hashes and ROM/map provenance |
| ROM adapter | Generated `SBDecode` or reviewed compiler extension, with regression fixtures |
| Table wiring | Reviewed init/timer/exit/option hooks and a table-specific safe display predicate |
| Build tooling | New or generalized hash-guarded builder/profile; no broad game-logic rewrites |
| Qualification | Evidence record, feature/display limitations and compatibility update |
| Release | Manifest, authorized contents, setup instructions and scoped rollback |

For an eligible additional map, use the generator command from the offline
exercise with that map and exact ROM. This produces decoder source only.
`build_common_pilot.py` hardcodes the MM profile, ROM and switches; there is no
`--rom` flag on that builder. Another table needs reviewed builder/profile work.
A successful map lookup alone cannot create a working Scorbit integration.

Review [protocol assumptions](protocol.md) before adding client features and
follow [contribution instructions](../CONTRIBUTING.md). Fix shared modules once,
then rebuild and revalidate affected staged tables.

## Staged MM build example

This advanced example uses the current MM-only builder and a full vpxtool
extraction. The CLI shape was checked against the locally available vpxtool
0.34.5. Verify your trusted tool's version/help before use. Replace the two
quoted input placeholders with your own paths; run from the repository root.
Do not use an existing extraction directory or omit media needed for assembly.

```powershell
$tableSource = '<absolute path to your authorized original MM VPX>'
$vpxtoolPath = '<absolute path to your trusted vpxtool.exe>'
if (Test-Path local/mm-stage) { throw 'Choose a new staging folder' }
New-Item -ItemType Directory local/mm-stage
Copy-Item -LiteralPath $tableSource -Destination local/mm-stage/source.vpx
& $vpxtoolPath extract local/mm-stage/source.vpx --output-dir local/mm-stage/extracted
if ($LASTEXITCODE -ne 0) { throw 'Extraction failed' }
.venv/Scripts/python -c "from vpx_scorbit.qr import write_qr; write_qr('urn:vpx-scorbit:offline-display-test:not-a-pairing-code', 'local/mm-stage/offline-qr.png')"
.venv/Scripts/python tools/build_common_pilot.py --extraction local/mm-stage/extracted --output local/mm-stage/pilot --vpxtool $vpxtoolPath --test-qr local/mm-stage/offline-qr.png
if ($LASTEXITCODE -ne 0) { throw 'Pilot build failed; inspect staging output' }
```

Expected outputs are `local/mm-stage/pilot.vpx`, the extracted `pilot/` folder
and `pilot.build.json`. The source script must match the MM profile or the builder
stops. The resulting pilot embeds the VBS modules, has networking disabled and
catalog ID zero, and displays only the offline QR asset. Its absolute diagnostic
image path is local to this staging setup; this is not a portable player package.

Before opening it, prepare the required table assets/ROM and a separately copied
table INI plus isolated desktop configuration. Check for a matching `.vbs`
sidecar that could override the embedded script. Opening the pilot is a separate
local gameplay test; this documentation review did not rebuild or run a VPX.
Retain logs/captures privately, then complete the validation record.

## Troubleshooting and rollback

- ROM mismatch or invalid BCD: verify effective ROM, byte layout and snapshot
  length; reject the sample rather than coerce it to zero.
- No game start: establish attract observation and fresh player-1/ball-1 start;
  inspect timer gaps. Do not bypass the late-attach guard to make a test pass.
- No QR: inspect offline/network configuration, pairing/claim state, timeout,
  safe-window predicate and rendering mode. Current VR hiding is intentional.
- 401/403: stop uploads and investigate the helper identity/token privately.
  Current runtime has no automatic token refresh. Never copy a working table's
  identity into another title to bypass catalog provisioning.
- Missing final upload: distinguish in-memory queue loss from rejected/duplicate
  entries; server retry semantics remain a qualification gate.

Roll back only the exact staged/deployed table/script/INI files identified in the
backup manifest. Preserve original downloads and ROM state unless restoration is
explicitly intended. Never recursively delete asset junctions into live folders.
