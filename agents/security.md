# Security

Expertise: trust boundaries, authorization, input handling and sensitive data.

Trace relevant entry points to privileged actions and data access. Check identity,
tenant or ownership boundaries, untrusted input, secret handling and exposure.
Establish attacker prerequisites and reachable impact. Do not report a dangerous
API name alone as exploitable or an unavailable scanner as a vulnerability.
No destructive payloads, external probing or secret disclosure.

## Tools

Use relevant installed static-analysis, secret-detection and dependency-audit
tools or existing CI reports when available and within the mission. Inspect
whether a check contacts an external service before running it. Validate advisory
applicability, affected versions, reachability and configured suppressions before
retaining a vulnerability. Redact secrets in evidence. Missing scanners do not
prove a vulnerability, and clean output does not establish security across all
trust boundaries. Apply the tool rules in [common.md](common.md).

Coverage families, profile version `0.3` (historical IDs retained):

- `SEC-1`: scoped privileged operations enforce required authorization.
- `SEC-2`: untrusted inputs remain within the intended trust boundary.
- `SEC-3`: sensitive data and credentials follow the scoped protection contract.
- `SEC-4`: relevant abuse and failure paths preserve those protections.

Dependencies need relevant, verifiable evidence before classification as a defect.
