# Scorbit technical review brief

**Purpose:** agree on a supported VPIN integration/testing route before enabling
production score submission for new ROM-based tables. This is an independent,
experimental project; no Scorbit endorsement is implied.

The default runtime embeds shared VBS in VPX and uses existing sToken/sQRCode
helpers. Python and AI skills are development tools. The native SDK remains an
optional experiment; its feature set must not be assumed for the legacy route.

MM `mm_109b` has an offline pilot and observed attract-state ROM reads. AFM
`afm_113b` is the next target and has only static decoder eligibility. Neither is
qualified end to end. See [compatibility](compatibility.md) and the
[security/quality review](security-review.md).

For exact payload/claim assumptions, read [protocol.md](protocol.md), then
[architecture](architecture.md) for boundaries. The [community overview](community.md)
supplies nontechnical status and announcement wording. Reviewers can reproduce
the [offline exercise](development.md#first-offline-exercise) without VPX, a ROM
or account provisioning.

## Decisions requested from Scorbit

- Correct MM/AFM VPIN catalog entries, machine IDs and helper OPDB values; whether
  Scorbit prefers a different onboarding/identity route for this project.
- Approved staging/test accounts and the evidence required before production use.
- Supported heartbeat/entry response contracts, especially claimed-player seat
  indexing, null/missing players, claim removal and display-name fields.
- Which mode/event semantics the helper protocol accepts, separately from SDK 2.0.4.
- Duplicate/idempotency guarantees for retries of identical session sequences,
  lost responses, final-entry retries and sessions resumed after disconnect.
- Token renewal/reconnect expectations and helper redistribution terms.
- Alignment with the upstream VPX plugin and longer-term supported architecture.

The requested outcome is a technical contact, an agreed test/onboarding route,
corrected protocol assumptions with sanitized examples, and a per-title
qualification checklist. This is a request for collaboration, not recognition
of the current source as a supported MM/AFM release.

Our catalog observations are historical searches, not authoritative proof that
entries do not exist. Physical MM 1389 / `G5pe4-MePZv` and AFM 1056 /
`G4do5-MDlN7` were found; those IDs are not used for virtual submissions.
The observed GOTG VPIN entry was 2108. Scorbit should confirm current values.

We have not submitted synthetic games to those physical entries. Local tests use
fake transports and SDK objects. Private authentication/QR observations used an
already paired existing table identity without game entries; no credentials or
claim QR images are included in this repository.
