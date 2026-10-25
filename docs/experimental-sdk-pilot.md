# Historical optional SDK pilot

**Not the default integration path.** These notes describe the earlier Python
companion experiment. Use [developer setup](development.md) for maintained offline
tools and [architecture](architecture.md) for the embedded helper route. Native
SDK authentication/callback behavior remains unqualified; installed-artifact
observations below are historical, not a current upstream release inventory.

The prototype explored adapting ROM-driven VPX tables through SDK 2.0.4.
Its target was Medieval Madness, `mm_109b`, on Windows VPX
`10.8.1.5436.af26b2d93`. It is retained for feature-driven experiments.

**Status: staged offline pilot, not a finished Scorbit-enabled table.** Live
Controller.NVRAM access is proven on this PC. SDK authentication, full game
lifecycle, actual player claiming/upload, and headset presentation are not yet
validated. See [research and evidence](research.md).

The reusable [skill](../skills/vpx-scorbit/SKILL.md) works as repository guidance
for Codex, Claude, or another agent that can read Markdown and run these tools.
Its current deterministic builder targets one pinned Medieval Madness script;
other tables require explicit ROM mapping and lifecycle integration work.

## Components

- `maps/mm_109.map.json`: upstream map for mm_109/mm_109b/mm_109c, with ODbL/DbCL licenses.
- `vpx_scorbit/memory.py`: strict WPC snapshot and five-byte BCD decoder.
- `vpx_scorbit/lifecycle.py`: offline session tracking and reset safeguards.
- `vpx_scorbit/sdk.py`: experimental SDK 2.0.4 adapter, provider/device-key callbacks and QR links.
- `assets/telemetry.vbs`: 500 ms telemetry and native Windows QR flasher rendering.
- `tools/stage_mm.py`: hash-guarded builder that adds a panel and hooks to a separate extraction.
- `profiles/medieval-madness.json`: pinned input hashes and source commits.

The table reads its existing Controller instance and publishes a complete hex
snapshot by file rename. The Python bridge decodes memory and calls the SDK
outside VPX. Basic session events derive from the map. Castle/multiball and
other rich modes need further mapping and validation.

## Historical workflow (advanced, offline by default)

First install the full environment from [developer setup](development.md),
including test dependencies. The following is not a player installation guide.

```powershell
.venv/Scripts/python -m unittest discover -s tests -v
```

The Python SDK wheel is only a wrapper. A matching `scorbit_sdk.dll` and its
dependencies must be provided on Windows; set `SCORBIT_SDK_PATH` to its folder.
During the recorded pilot, the installed wheel failed to import because that
native library is absent. Public 2.0.4 release assets inspected so far provide
Linux native builds and Python wrappers, not a ready-to-install Windows DLL.

Extract the user's table with vpxtool into an external staging folder, then:

```powershell
.venv/Scripts/python tools/stage_mm.py --extraction <extracted-table-folder> --output <new-pilot-folder> --runtime <runtime-folder> --vpxtool <vpxtool.exe>
```

The builder writes `<new-pilot-folder>.vpx`; copy the original table-specific
INI alongside that new VPX. Use an isolated desktop global INI for capture.
The runtime path is embedded in the staged script and must exist. Start the
offline bridge before the table; wait through attract before starting a game:

```powershell
.venv/Scripts/python -m vpx_scorbit.bridge --runtime <runtime-folder>
```

For an offline QR display test, call `vpx_scorbit.qr.write_qr()` with a clearly
marked test URI and `<runtime-folder>/pair.png`. This is not a pairing code.
Remove the test PNG before authenticating. Synthetic/replayed input must never
be passed to a production SDK configuration.

Pairing QR display expires after 30 seconds; player-claim display after 15.
Pairing confirmation removes the pairing image; claiming removes that seat's
claim image. The panel hides while a ball is in play. A claim can be shown
before launching ball one (MM shooter-lane switch 18, launch switch 11).
Use the table's **Scorbit QR** option, switching **Auto → Show again**, to
reopen an available code. It still obeys the playfield visibility guard.
These callbacks require real SDK validation; the timeout works locally.

## SDK configuration (pending integration validation)

Keep a private JSON file outside the repository with these fields:
`provider`, `machine_id`, `hostname`, `encrypted_provider_key`,
`device_key_path`. Obtain the identity and provider key through Scorbit; do not
reuse another table's helper token. `hostname` selects the SDK environment.
Use staging while validating the adapter and the target's lifecycle.

`--sdk-config <private-json>` explicitly enables SDK calls. Without it the
bridge is offline. The SDK writes generated `pair.png` and seat-specific
`claim-1.png` through `claim-4.png` to runtime. Key material is never printed.
The SDK adapter has not been exercised against a native library yet.

## Known pilot limits

The bridge must observe attract before starting a session. It does not resume
an in-progress session after restart, infer finish on disconnect, support score
rollover, or implement rich modes. It rejects invalid BCD and unknown map
semantics. The telemetry transport is a local polling prototype, with no
automatic service/launcher installation. QR placement and refresh need further
VR/phone testing. No live installation or launcher config is modified by the
builder. This repository contains no tables, ROMs, helper executables or keys.
