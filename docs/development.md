# Developer guide

This checkout is developer tooling and experimental embedded runtime source.
Players do not install Python, this skill, or a native SDK for the default route.

## Clean setup

Use Git, Windows with Python 3.12, and the Windows `cscript` VBScript host. Obtain
a source checkout (fork/clone the public repository, or unpack the
review source archive), open PowerShell there, and confirm the root contains
`pyproject.toml` and `README.md`. All commands below run from that root. Linux-only
test runs skip the native tests and cannot qualify the runtime. No VPX install,
ROM, helper binary, Scorbit account or SDK native library is needed for unit tests.

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install --upgrade pip==26.2.2
.venv/Scripts/python -m pip install --require-hashes -r requirements.txt
.venv/Scripts/python -m pip install coverage==7.14.1 hypothesis==6.170.9
New-Item -ItemType Directory -Force local/security
Get-Command cscript.exe -ErrorAction Stop
.venv/Scripts/python -m coverage run -m unittest discover -s tests -v
.venv/Scripts/python -m coverage json -o local/security/coverage.json
.venv/Scripts/python scripts/check_coverage.py local/security/coverage.json
```

The optional SDK wrapper is installed by this developer lock for offline adapter
tests; it does not install or exercise a native SDK. Run from the checkout root;
this project is not currently a general pip-installable application.

If the Python launcher (`py`) is unavailable, use your explicit Python 3.12
executable for the first command. Do not run tests with an unrelated system
Python after creating the environment. Expected result: all tests pass with no
native-host skips, then the per-file coverage gate passes. The recorded suite
currently contains 36 tests; counts may grow as contributions are added.

For the complete quality workflow:

```powershell
py -3.12 -m venv local/security/venv
local/security/venv/Scripts/python -m pip install -r packaging/security-tools.txt
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install-scanners.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality.ps1
```

The scanner install writes only under ignored `local/security/`. These commands
download developer packages and public rule/advisory data. See [security review](security-review.md) for tool
versions, network use, exclusions and the documented Semgrep disposition.

## First offline exercise

Compile the included MM map without a table, ROM, network token or helper:

```powershell
New-Item -ItemType Directory -Force local/walkthrough
.venv/Scripts/python tools/generate_rom_adapter.py --map maps/mm_109.map.json --rom mm_109b --output local/walkthrough/mm-adapter.vbs
Get-Content local/walkthrough/mm-adapter.vbs -TotalCount 8
.venv/Scripts/python -m unittest discover -s tests -p test_vbs_runtime.py -v
```

Expected output is a generated `SBDecode` function with an `mm_109b` ROM guard,
followed by passing native runtime tests. The generated file is **not** a complete
table script and does not submit scores. Its dependencies come from the common
VBS modules. The tool refuses to overwrite output; choose a new filename when
rerunning. Unsupported ROM names or mapping semantics must fail, not silently
produce a guessed adapter.

For your first change, add an offline regression for a decoder boundary, improve
a protocol assumption's documentation, or improve an existing error explanation.
Use `tests/test_security.py` for hostile inputs and `tests/test_vbs_runtime.py`
for actual VBS execution. Avoid selecting a full new table as a trivial first issue.

## Using AI assistance

AI is optional. From either assistant, ask it to read `AGENTS.md` and
`skills/vpx-scorbit/SKILL.md` in this checkout, then describe the exact task and
allowed staging location. For example: "Review this ROM map for decoder eligibility
and produce an offline validation plan; do not modify my live tables."
The skill is repository guidance, not a player plugin or a self-contained one-file
skill download: it references this repo's tools and docs. Keep the checkout intact.
Separate native skill installation/discovery for each assistant has not been
qualified here, so the documented baseline is explicit file-based invocation.

## From offline exercise to table work

The [integration guide](table-integration.md) adds separate requirements: a trusted
vpxtool executable, the exact authorized table/script revision, a compatible ROM
and VPX/PinMAME installation, isolated INIs, then an approved Scorbit identity/test
route. The development test suite needs none of those external player assets.
The [MM profile](../profiles/medieval-madness.json) deliberately rejects unreviewed
script revisions. Removing its hash guard is not a supported way to add a table.

## Where changes belong

For a full staged MM build, follow the [concrete staging example](table-integration.md#staged-mm-build-example).
That example needs external assets and is separate from the asset-free exercise.

| Change | Location | Main validation |
|---|---|---|
| ROM decoding / lifecycle | `vbs/rom-core.vbs`, `tools/generate_rom_adapter.py` | Boundary/BCD tests, native snapshots, real DMD comparison |
| Session transport | `vbs/entry-queue.vbs`, `vbs/http-transport.vbs`, `vbs/helpers.vbs` | Fake HTTP failures/retries, identity and claim protocol review |
| QR presentation / table wiring | `vbs/qr-desktop.vbs`, `vbs/host.vbs`, builder | Native host tests, staged screenshots, actual phone/headset |
| Optional reference/SDK tooling | `vpx_scorbit/` | Python tests; fake SDK contracts do not qualify native SDK behavior |
| Shared integration procedure | `skills/vpx-scorbit/SKILL.md` | Follow against a staged table; keep evidence and limits accurate |

Changes to shared VBS do not update existing tables automatically. Regenerate an
isolated pilot, retain its manifest/module hashes, then run capture and gameplay
validation. Never overwrite the author's table or live INIs while developing.

The Windows CI workflow mirrors local checks and fails if cscript is missing.
The [initial hosted run](https://github.com/dayelostraco/vpx-scorbit/actions/runs/40205322892)
passed on Windows. Check the repository Actions tab for the current commit's
result. Scanners need internet access for rules/advisory databases.

## Review and comments

For every changed interface, record input types, units, allowed ranges, object
ownership, output/error behavior, and side effects. Comments should explain why
score regression aborts, why final entries remain queued, or why a QR is hidden.
Avoid comments that simply repeat assignments. Do not claim full comment coverage:
we review contracts manually, while automated coverage measures executed Python.

Keep generated artifacts and scanner reports under ignored `local/`. Treat
diagnostic response bodies and helper output as private. Provide sanitized
summaries rather than raw authentication logs in reviews.

## Common setup failures

| Symptom | Action |
|---|---|
| Native tests skipped | Check `cscript.exe` availability; a Python-only pass is incomplete |
| `curses` import failure on Windows | Install the locked dependencies into the same `.venv` used to run tests |
| Native Scorbit DLL error | Do not invoke the experimental live SDK adapter for offline tests; tests use fakes |
| Existing generated output | Choose a new file/directory; generators intentionally avoid replacement |
| Scanner download or rule fetch fails | Check network access; report the scan as incomplete, not clean |
| Tests pass but the table has old behavior | Rebuild the embedded runtime; existing VPX files do not auto-update |
