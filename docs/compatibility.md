# Compatibility and qualification

| Target | ROM/map status | Table integration | Scorbit and display status |
|---|---|---|---|
| Medieval Madness `mm_109b` | Mapped; decoder and attract samples tested | Offline common pilot on VPX 10.8.1.5436; rebuild required after hardening | VPIN identity unresolved; no end-to-end uploads; desktop QR software-decoded; phone and VR unqualified |
| Attack from Mars `afm_113b` | Matches the static decoder subset | Not integrated or gameplay tested | VPIN identity unresolved; no QR/upload qualification |
| Other mapped ROMs | 1,589 indexed revisions at pinned upstream commit; 258 revisions / 63 map files match the current subset | No qualification implied | Separate adapter, table and service validation required |

The seven existing helper-integrated tables were used as protocol references and
received separately staged fixes. They are not seven ROM adapters implemented by
this repository. Their startup/heartbeat tests do not qualify MM or AFM gameplay.

## Qualification levels

| Level | Minimum evidence | Does not establish |
|---|---|---|
| Discovered | Exact ROM appears in pinned map index | Decoder or table compatibility |
| Decoder eligible | Compiler accepts mapped semantics | Correct live reads or gameplay |
| Offline tested | Boundary/synthetic decoding and lifecycle tests; record live attract observations separately | Real game accuracy or service acceptance |
| Gameplay validated | Complete games compared with scores/states in the specified setup | Pairing, uploads or all display modes |
| Service qualified | Approved identity/test process and confirmed claims/uploads/retries for scoped features | Other revisions, rich events or untested display modes |

These levels are project evidence labels, not official Scorbit certification.
Desktop software decode, physical phone scan and VR scan have separate evidence.
Use the [validation record](validation-template.md) for new claims.
Every new compatibility claim needs the
table/script hashes, ROM revision, VPX build, date, evidence and known limitations.
Never promote a table based only on an entry in the map catalog.

See [map coverage](map-coverage-notes.md), [MM capabilities](mm-capabilities.md),
and [handoff](HANDOFF.md) for evidence and remaining work.
