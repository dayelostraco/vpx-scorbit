# Security and quality review — October 25, 2026

This is a local source review, not a player-release or hardware certification.
No table, ROM, helper identity, live configuration or service-side score was
changed during this pass. The staged MM VPX still contains the earlier runtime;
it must be rebuilt and tested before these source changes reach a table.

## Review rounds

1. Public-release and trust-boundary review: history/working-tree secret scans,
   dependency inventory, generator inputs, filesystem boundaries, provenance.
2. Runtime correctness: snapshot isolation, numeric validation, JSON resource
   bounds, atomic response updates, delayed attachment, queue/locale behavior.
3. Regression and repeatability: native VBScript tests, differential/property
   fuzzing, packaging/CLI/optional SDK tests, per-file coverage and final scans.

## Fixes

- ROM identifiers must be safe literal names, even when included in supplied
  map metadata. Field lengths/offsets reject booleans and fractional values.
- Map-index paths cannot escape the supplied root, including resolved links.
- Python decoder resets sparse memory between complete snapshots; an old
  PinMAME trailer cannot survive a later RAM-only snapshot.
- VBScript validates numeric types, integer values, four score slots and bounds.
  Lifecycle state copies snapshots so caller mutation cannot bypass regressions.
- Optional Python lifecycle also refuses delayed starts beyond player 1/ball 1.
- Parsed JSON text is capped at 65,536 UTF-16 code units (VBScript `Len`, not an
  HTTP byte limit). Pairing and player claims update only
  after the entire response validates; malformed rows cannot partially pair.
- QR pixel expansion rejects nonsquare or oversized images (maximum 1024 square).
  This bounds our pixel-copy allocation after WIA loads the image, not the WIA
  decoder's own allocation; helper-produced local files remain the trust boundary.
- Common builder checks for duplicate panels before producing output.
- Updated the isolated project environment's vulnerable pip 25.0.1 to 26.2.2.
  Pip is development tooling and is not shipped to players.
- Consistent Python formatting/linting and a hash-pinned optional Python runtime
  inventory. Developer dependencies are not VPX player requirements.

## Results and scope

| Check | Result |
|---|---|
| Windows unit/integration tests | 36 passed, including real cscript execution |
| Property-based fuzzing | 500 ROM identifiers + 500 byte strings; deterministic Hypothesis runs |
| Native differential tests | 811 JSON inputs, all 256 single-byte BCD values, oversized JSON rejection |
| Coverage | Every first-party file in `tools/` and `vpx_scorbit/` passes 80% lines and 80% branches separately |
| Ruff 0.17.2 | Lint and format checks pass |
| Semgrep CE 1.182.1 | No unsuppressed findings with `p/python` and `p/security-audit` |
| Trivy 0.76.1 | No known vulnerabilities or detected secrets; scans `requirements.txt` |
| pip-audit 2.10.1 | No known vulnerabilities in pinned optional runtime dependencies |
| Gitleaks 8.30.1 | No recognized secrets in local Git history |

Semgrep initially flagged the legacy diagnostic builder's `subprocess.run`.
Reviewed disposition: intentional execution of a developer-selected local
vpxtool executable using an argument vector and no shell. The exact rule is
suppressed inline with the rationale; do not generalize that suppression.
Registry rules and vulnerability databases evolve; retain local JSON reports
when comparing runs. Downloaded Trivy/Gitleaks release archives were checked
against their official release SHA-256 manifests before execution.

VBScript is not semantically covered by the Python Semgrep rules. Its protection
comes from manual review, generic secret scans and real-engine behavioral/fuzz
tests. No VBScript line/branch instrumentation is available in this workflow;
the 80% coverage claim is **Python only**. Tests and review-runner scripts are
outside that coverage denominator. Vendored parser code and map data are also
excluded from our first-party coverage gate; their files remain scan targets.
Trivy found no applicable infrastructure configuration, and skipped license
detection without site-packages: neither is a license-compliance pass.

## Reproduce on Windows

The tested environment uses Windows Python 3.12. The [developer guide](development.md)
provides the canonical setup without uv; the equivalent uv workflow below assumes
uv is already installed. Run from the repository root:

```powershell
uv venv .venv --python 3.12
uv pip sync --python .venv/Scripts/python.exe requirements.txt
uv pip install --python .venv/Scripts/python.exe coverage==7.14.1 hypothesis==6.170.9
uv venv local/security/venv
uv pip install --python local/security/venv/Scripts/python.exe -r packaging/security-tools.txt
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install-scanners.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality.ps1
```

The runner stops on failed checks and keeps reports in ignored `local/security/`.
It downloads public Semgrep rules with metrics/version checks disabled. Trivy
updates its public advisory database; pip-audit queries public package advisories.
No Scorbit credentials or service calls are needed. Python tools do not need to
be installed on player machines. Tests have hard time limits for cscript.

The runtime lock was resolved on Windows with the optional SDK extra. Regenerate
using `uv pip compile pyproject.toml --extra sdk --generate-hashes -o requirements.txt`.
Do not interpret this inventory as a player installer or cross-platform lock.

## Remaining release gates

- Real MM gameplay, score uploads/claims, reconnect/token refresh and retry
  semantics remain unqualified; only offline tests were added here.
- No VR QR surface is implemented; desktop QR phone/headset tests remain open.
- MM/AFM VPIN catalog identities remain unresolved; AFM is not integrated yet.
- Upstream map ODbL/DbCL and parser LGPL notices are retained. Helpers, ROMs and
  VPX binaries are absent from Git. Confirm helper redistribution terms before
  any player bundle. Original project code/documentation are now MIT licensed;
  see the root license and third-party notices.
- Working-tree documentation now uses portable paths. Earlier local commits
  contain workstation usernames/paths as historical notes, but no scanner-
  recognized credentials. A separate sanitized initial-commit candidate has since
  been prepared; preserve private history locally and refresh that candidate
  after later source changes. See [sharing readiness](sharing-readiness.md).
- Source was subsequently published with private vulnerability reporting and
  protected main enabled. The initial hosted Windows workflow passed; see
  [sharing readiness](sharing-readiness.md) for the run and protection details.
