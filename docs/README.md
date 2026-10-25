# Documentation guide

Read the [project overview](../README.md) first. The project is experimental:
developer tools can be used now, but there is no qualified MM/AFM player package.

## Choose a reading path

- **Scorbit developer:** [technical brief](scorbit-review.md) →
  [architecture](architecture.md) → [implemented protocol and assumptions](protocol.md)
  → [MM evidence](mm-capabilities.md) → [security review](security-review.md).
- **Community manager/player:** [community overview](community.md) →
  [compatibility](compatibility.md). These explain what exists, what is planned
  and how to describe progress without implying supported table releases.
- **Contributor:** [development setup and first exercise](development.md) →
  [contributing](../CONTRIBUTING.md) → [architecture](architecture.md).
- **Table author:** [integration guide](table-integration.md) →
  [validation record template](validation-template.md) →
  [map discovery coverage](map-coverage-notes.md). AI assistance is optional;
  [the shared skill](../skills/vpx-scorbit/SKILL.md) follows the same boundaries.

## Current references

| Document | Purpose |
|---|---|
| [Compatibility](compatibility.md) | Canonical table/ROM qualification status; map eligibility is not support |
| [Common runtime](common-runtime.md) | Intended component responsibilities and packaging design |
| [Protocol](protocol.md) | What this client sends/accepts, and what Scorbit still needs to confirm |
| [Security reporting](../SECURITY.md) | Handling vulnerability and credential reports |
| [Licensing and provenance](../THIRD_PARTY_NOTICES.md) | Original MIT code versus separately licensed upstream material |
| [Sharing readiness](sharing-readiness.md) | Public source-review checklist; separate from player release readiness |
| [Roadmap](../ROADMAP.md) / [changelog](../CHANGELOG.md) | Milestone acceptance criteria and unreleased changes |
| [Comment review](comment-review.md) | Interface documentation scan scope, results and manual contract review |

## Historical evidence and correspondence

[Research](research.md), [MM capabilities](mm-capabilities.md) and the
[development handoff](HANDOFF.md) record the October 2026 development installation.
Local captures, table backups and private research mentioned there are not
repository prerequisites or downloadable artifacts. Contributors can reproduce
offline tests; reproducing hardware/gameplay observations requires their own setup.

[SDK pilot notes](experimental-sdk-pilot.md) describe an optional older prototype,
not the default runtime. [Email draft](scorbit-email-draft.txt) is the current
unsent introduction; [catalog-only draft](scorbit-catalog-request.txt) is retained
as a shorter historical alternative, not an additional request to send.

When status changes, update compatibility first, then the README/community
summary and affected capability rows. Keep dated evidence factual; do not turn
old desktop captures into claims about a newly rebuilt runtime or VR.
