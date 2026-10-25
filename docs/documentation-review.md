# Documentation review — October 25, 2026

This was a maintainer review through three reader perspectives, not an external
Scorbit endorsement or independent usability study. It covered all tracked
first-party Markdown/text guidance, the AI skill, correspondence drafts and
provenance notes. Upstream license texts and generated map data were preserved;
their presentation and claims were checked, not relicensed or rewritten.

## Findings and changes

| Reader | Gap found | Resolution |
|---|---|---|
| Scorbit developer | No precise description of client payloads, claim assumptions or desired review outcome | Added protocol reference tied to source; separated catalog/venue/session identities; highlighted unknown claim and HTTP-200 semantics; specified requested collaboration outcome |
| Scorbit community manager | README assumed technical knowledge and could suggest available tables, hundreds of supported titles or fully validated QR | Added community FAQ/glossary and announcement wording; foregrounded experimental status and separate software/phone/VR evidence |
| Open-source contributor | Setup lacked a concrete first exercise, contribution paths and expected outputs | Added runnable asset-free adapter exercise, full scanner setup, AI/manual workflows, PR template and troubleshooting |
| Table integrator | Generic adapter generation could be mistaken for generic table assembly | Documented MM-specific builder limits, external prerequisites, staged example, required deliverables and reusable qualification record |
| All readers | Historical SDK guidance competed with the selected helper implementation | Labeled SDK notes historical/optional; corrected the skill's default builder and limited native-SDK prerequisites to that route |
| All readers | Support labels, paths and dated observations were inconsistent | Added reading paths and qualification definitions; marked private installation evidence and alternate catalog draft as historical |
| Technical accuracy | JSON limit described as bytes despite VBScript character counting | Corrected to 65,536 UTF-16 code units, with no claim of an HTTP body-byte limit |

## Reader acceptance checks

Each reader can now find the project purpose, current limits and next useful
action from the root README. The [documentation index](README.md) provides the
longer reading paths. The technical brief and protocol reference distinguish
implemented behavior from service guarantees. Community guidance distinguishes
planned player experience from today's developer-only source. Contributors have
commands, expected results, source locations and a change-review checklist.

The offline walkthrough was executed: the generated decoder had the expected
ROM guard and all 9 tests in `test_vbs_runtime.py` passed. Local Markdown targets,
section anchors and encoding were checked; the skill passed its validator.
The new staging example was checked against vpxtool CLI help and builder source;
no table build, gameplay test, Scorbit request or email was performed in this review.
Earlier full-suite/security results remain dated evidence, not newly claimed
hardware validation. Runtime code was not changed by this documentation pass.

## Remaining external validation

- Obtain feedback from actual Scorbit technical/community contacts and a developer
  unfamiliar with the project; internal perspective review cannot substitute for it.
- Hosted CI and private security reporting need verification after publication.
- Catalog provisioning, official protocol guarantees, helper redistribution and
  gameplay/phone/VR qualification remain open. Documentation exposes these gaps;
  it does not resolve them by changing wording.
- Comment coverage has no blanket percentage claim. Interface contracts and
  non-obvious decisions are reviewed manually; test coverage measures execution.
