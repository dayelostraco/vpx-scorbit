# Security reporting

This is an experimental integration, not a qualified player release. The common
MM builder disables networking. Do not enable uploads using a physical-machine
catalog entry or submit synthetic games to production.

For a suspected vulnerability or credential exposure, do not open a public issue
containing exploit details, tokens, QR codes, player data or private logs. Once
private vulnerability reporting is enabled on the public GitHub repository, use
its Security tab. Until then, arrange a private channel with the repository
owner without posting the sensitive material. No response-time SLA is offered.

Describe the affected revision, component, prerequisites and impact. Prefer an
offline reproducer using fabricated values. Do not test against another player's
device or a production Scorbit account. If credentials were exposed, revoke or
rotate them with their provider; deleting a file from Git is insufficient.

Scans and their limitations are in [the security review](docs/security-review.md).
Third-party advisories and helper redistribution terms need separate tracking.
