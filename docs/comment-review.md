# Interface comments and docstring review

The publication pass reviewed first-party Python, shared VBS, the historical
telemetry asset and PowerShell entrypoints. Added contracts explain ranges and
units, caller ownership, side effects, failure behavior and known limitations.
No player runtime behavior was intentionally changed in this pass.

`scripts/audit_comments.py` produces a reproducible presence report and is part
of the quality workflow. It checks public Python functions/classes/methods and
non-private VBS procedures/properties for docstrings or adjacent comments.
Run it with an output path under `local/security/` to retain the exact inventory.

The initial publication scan found **24/24 Python interfaces** with docstrings
and **40/40 VBS procedures/properties** with adjacent comments. Positive/negative
fixture checks confirmed missing documentation fails the gate. An AST comparison
excluding docstrings and a VBS comparison excluding comment lines confirmed that
the existing executable statements did not change during this pass.

This narrow gate must not be described as "all code is fully commented" or
equated with test coverage. It excludes constructors/private/nested callables,
tests, generated output and upstream source. PowerShell and generated-adapter
contracts are reviewed manually. Presence does not prove accuracy or usefulness.

## Manual contract review

| Boundary | Information checked |
|---|---|
| ROM decode/snapshot | Byte offsets, BCD/integer validity, complete snapshots, immutable/copy ownership |
| Lifecycle and queue | Attract prerequisite, millisecond clocks, final-score ordering, local versus transmitted IDs, abort behavior |
| HTTP/helpers | Token secrecy, trusted executable/state paths, asynchronous polling, provisional response semantics and absent automatic renewal |
| QR | Quiet zone, provenance of links, bounded pixel expansion versus WIA decode, desktop-only scope, timer and manual recall behavior |
| Builders/packager | Hash guards, new-output-only semantics, partial staging on failure, identity versus redistribution rights |
| Optional SDK/bridge | Native configuration requirement, copied callbacks, ordered final scores, file side effects, no finish on interrupted input |
| Quality tooling | Scan/coverage scope and failure behavior; no claim of semantic or hardware certification |

Comments remain candid about risks: the helper host does not itself verify
executable hashes; packaging does. Caller-selected state paths are trusted.
The SDK QR writer is single-writer per output path. Transport Connect is not a
complete identity-switch or recovery API. These statements help reviewers see
the boundaries; they do not turn an unimplemented feature into a completed one.
