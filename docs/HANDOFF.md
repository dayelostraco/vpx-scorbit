# Development checkpoint - October 25, 2026

This is a dated maintainer handoff, not contributor setup instructions. Paths,
captures, patches and table backups below refer to the private development
installation and are not included in the checkout. Start with the
[documentation guide](README.md) for reproducible public workflows. BM means
Blood Machines; Cyber means CyberRace; Sponge means SpongeBob.

## Current deliverables

- Shared embedded VBScript runtime, no Python/native SDK player dependency.
- Hash-guarded offline MM builder and hash-pinned local helper bundle.
- Automated security/quality checks and native VBScript tests pass; see
  [security review](security-review.md) for current counts, scope and limitations.
- Existing helper authentication/claim QR tested against the SAME existing BM
  device, preserving identity; zero game entries sent.
- MM common pilot clean desktop startup; square QR decodes at 5120x2160 and
  1920x1080, outside playfield/DMD. Embedded-only run and timeout verified.
- Seven installed tables: all gain lazy log allocation (~229 MiB isolated-class
  saving). BM/Cyber/Sponge also have corrected name indices, and BM/Sponge have
  separate token files. Seven startup/paired-heartbeat checks pass.
- Public-facing author notes and patches are in Downloads/Scorbit-author-fixes-2026-10-25.zip.
- Public source is now at https://github.com/dayelostraco/vpx-scorbit; the initial
  hosted checks passed. No email/outreach messages have been sent. See sharing-readiness.md.

## Main remaining work

1. Get proper MM/AFM VPIN catalog identities. Searches found physical/remake
   entries only. Never substitute those IDs. Draft request is in
   docs/scorbit-catalog-request.txt and Downloads/Scorbit-VPIN-catalog-request.txt.
2. Resume normal-play validation when the Windows computer-use native pipe is
   available. It failed all recovery attempts; no direct UI automation fallback
   was used. Scoped paused diagnostic was stopped; test NVRAM restored.
3. Validate score changes, 1-4 seats, bonus/finish, tilt, extra balls and resets.
   Attract samples and synthetic tests do not qualify this. No live score upload.
4. Validate actual legacy entry/claim response schema and retry semantics.
   Current parser's players-array handling is tested with fixtures, not real
   claimed-game responses. Auth rejection currently disables the client; token
   refresh/reconnect needs further work before production release.
5. Implement and test a VR QR surface. Current common pilot hides its desktop
   backdrop in VR; physical phone/headset scanning remains open.
6. Map and qualify rich MM events. Do not substitute cumulative audits or infer
   modes from score deltas. See mm-capabilities.md.
7. Only after MM qualification, integrate/test AFM using its effective live VBS
   sidecar, afm_113b. Its map is eligible for the current generator, but AFM has
   not been modified or gameplay-tested by this project.
8. Verify helper redistribution terms before publishing a player package.

## Local evidence and safety

Repo: the current checkout.
MM staging: <VPX install>/Staging/2026-10-24-scorbit-rom.
Current artifact: mm-common-v1.vpx; it predates the security-review changes.
Rebuild and requalify the staged pilot before testing the updated runtime in VPX.
Networking is disabled and catalog ID zero. Its QR is an offline test URI.
Do not distribute this diagnostic VPX as a working Scorbit integration.
The older mm-pilot is diagnostic history; its sidecar remains in staging only.

Seven-table fixes: Staging/2026-10-24-scorbit-common-fixes and
Staging/2026-10-25-scorbit-log-buffer, with separate original-VPX backup sets.
The latter backup preserves the earlier three-table corrections. Restore only
specific files when rolling back. Staging includes asset junctions into live
Tables: never recursively delete their targets.

Live MM, ROM ZIP, VPX binary, global VR/frontend configuration preserved.
All game-input tests were offline. User-supplied prior research is archived
locally under docs/prior-research and excluded from Git.
