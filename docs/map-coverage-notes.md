# ROM discovery coverage

Static audit of pinball-memory-maps at commit
f0c422099f0b50b69bfdf6d071a6653a8b25a6fd: 1,589 indexed ROM revisions.
The earlier count of 1,590 included the index's `_note` metadata entry.
258 revisions across 63 distinct map files match the generator's current
WPC-12K field subset. A map file is not necessarily a distinct game title.
This is compile eligibility, not live-game or Scorbit compatibility.

See map-coverage.json for rejection reasons and mapped field names. The
remaining layouts/encodings need explicit adapter support rather than guesses.
AFM afm_113b matches the subset, but its table has not been integrated or tested
with the common runtime; MM qualification comes first.

Source: https://github.com/tomlogic/pinball-memory-maps/tree/f0c422099f0b50b69bfdf6d071a6653a8b25a6fd
Data copyright Tom Collins and upstream contributors; ODbL/DbCL licenses are
retained under maps/. Regenerate using tools/audit_maps.py against that pinned
checkout, with a new output path. Never describe this audit as hundreds of
working table integrations.
