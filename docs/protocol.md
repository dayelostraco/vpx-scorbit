# Legacy protocol implementation under review

This describes **the current repository code**, not an official Scorbit API
specification. Read it alongside [http-transport.vbs](../vbs/http-transport.vbs),
[entry-queue.vbs](../vbs/entry-queue.vbs) and [helpers.vbs](../vbs/helpers.vbs).
The generated MM pilot is offline. Do not use these notes to submit fabricated
entries or bypass catalog provisioning.

## Identity and data flow

The table's catalog machine ID and OPDB identifier are inputs to helper
provisioning. The returned `venuemachine_id` represents the provisioned venue
machine used by claim QR generation; it is not the catalog machine ID. A
`session_uuid` identifies a game. These identities must not be interchanged or
borrowed from another table. The exact identity/provisioning contract needs
Scorbit confirmation for the new titles.

sToken produces private authentication output and pairing material. The common
client passes the token as `Authorization: SToken …` over HTTPS; the token must
never appear in committed fixtures or logs. sQRCode generates claim imagery from
the helper inputs. The host reads local images for display, not from an AI service.

| Request implemented | When | Current evidence |
|---|---|---|
| `GET /api/heartbeat/?session_active=true|false` | No entry is ready to send, or pairing is needed | Existing paired reference device returned HTTP 200; not an MM/AFM claim test |
| `POST /api/entry/` with form-encoded fields | Paired client with queued entries | Fake HTTP tests only; no new-table production game submitted |

Only `api.scorbit.io` and `staging.scorbit.io` are accepted by the transport. The
current host's enabled path selects production; there is no supported command-line
switch that makes the MM builder a staging/network client. Agree on the test route
with Scorbit before implementing an authenticated pilot.

## Entry fields currently emitted

| Field | Client behavior | Confirmation needed |
|---|---|---|
| `session_uuid` | Generated per observed fresh game | Required format and lifetime |
| `session_time` | Elapsed table milliseconds since queue Begin, plus 1 | Server units, meaning of offset and reset behavior |
| `session_sequence` | Starts at 0; increments on appended entries | Gaps from coalescing and duplicate/retry semantics |
| `active` | `true` for start/update; `false` for finish | Accepted finish semantics |
| `current_p1_score` … `current_p4_score` | Integer scores for participating seats only | Seat changes and final-score acceptance |
| `current_ball`, `current_player` | Active snapshot values; both `-1` for finish | Sentinel values and special cases |

Final scores and `active=false` share one queued message. Ordinary tail updates
can be coalesced; the queued head and final entries are preserved. Queue head IDs
are local acknowledgment handles, distinct from `session_sequence`. State is not
persisted across VPX exit. A reset/gap aborts the open local game without submitting
a synthetic finish. No modes, credits, achievements or extra-ball events are
currently emitted by this queue; an inspected donor's `game_modes` field is not
proof of supported rich events in this client or the service.

## Response assumptions

The client requires a JSON object and commits pairing/claim changes only after
validating the whole object. JSON size and depth are bounded. The following is
implemented behavior to review, **not a verified service schema**:

| Field | Implemented interpretation |
|---|---|
| `unpaired` | Optional Boolean; true clears venue identity and claims |
| `venuemachine_id` | Optional positive integer literal (1–15 digits); marks paired; null leaves prior value unchanged; a positive ID with `unpaired=true` is rejected |
| `players` | Optional array of up to four objects, position treated as seat order; presence clears then replaces claim names |
| `cached_display_name` | Optional string/null in a player object; nonempty name is treated by the host as a claimed seat |

An absent `players` field retains prior claims; `players: []` clears them;
`players: null` is rejected. Empty display names are currently indistinguishable
from unclaimed seats. Scorbit should confirm indexing, sparse seats, claim removal
and the reliable claim-identity field before this controls live display behavior.

HTTP 200 with valid object JSON acknowledges the in-flight head, including `{}`.
This may be insufficient if the API reports application-level errors in a 200
body; that is a review question, not a claimed guarantee. A malformed response
does not acknowledge the entry. 401/403 disables the client; other HTTP failures
or timeouts retain the head and retry after about 5 seconds. Successful responses
schedule the next request after about 2 seconds. Automatic token renewal and
cross-restart recovery are not implemented.

## Requested review outcome

Scorbit's technical contact should confirm/correct the fields above, specify the
approved test environment and catalog identities, and define duplicate/final-entry
behavior and rate limits. Add sanitized fixtures and regression cases for the
agreed contract, then validate it under that approved process before updating
[compatibility](compatibility.md) to service-qualified.
