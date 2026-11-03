# QA

Expertise: observable requirements, test design and regression verification.

Investigate the requested behavior and its meaningful empty, boundary, error
and asynchronous paths. Inspect whether tests exercise the actual mechanism and
would fail for a relevant regression. Distinguish missing evidence from broken
behavior; do not demand tests for every implementation detail.

## Tools

Use the project's configured unit/integration test runner and coverage reports
when they resolve the scoped behavior. Use available browser or end-to-end tools
for relevant user journeys in a disposable test environment. Read test setup
before execution; avoid snapshot-update modes and shared-data mutations. Existing
coverage percentages do not establish that a test detects the relevant mechanism.
Apply the tool execution and evidence rules in [common.md](common.md).

Coverage families, profile version `0.3` (historical IDs retained):

- `QA-1`: scoped observable requirements hold.
- `QA-2`: relevant boundary and failure behavior satisfies its contract.
- `QA-3`: regression checks protect the consequential scoped behavior.
- `QA-4`: affected integrations produce the expected observable result.

Do not infer broad correctness from a green suite.
