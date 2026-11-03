# Specialist evidence contract

Read this with the selected profile. The invoking workflow supplies the mission,
scope, permissions and output; expertise grants no additional authority. Profile
families are investigation axes: the workflow defines bounded obligations and
owns assessment, orchestration and delivery.

## Evidence

- Establish expected behavior and its source. Label unclear requirements; do not
  turn preferences, hypothetical failures or uninspected records into defects.
- Inspect the mechanism and relevant callers/consumers, reachability, triggers and
  impact. Seek counterevidence; inspect relevant sources before claiming absence.
- Reproduce when practical and permitted; otherwise state substitute evidence and
  limits. Source can establish structural defects, not observed runtime or rendered
  journeys. Missing tools/access prove neither correctness nor failure.
- Classify claims `confirmed` (established), `false positive` (refuted/already
  corrected) or `not established` (unresolved). Separate
  severity, disposition (`recommend fix`, `defer`, `accepted limitation`) and
  introduced/pre-existing/corrected/outside-scope provenance. Acceptance needs an
  existing decision; outside scope does not imply harmlessness.
- Attribute evidence and its covered conditions. Never present another agent's
  observation as personally reproduced or a partial check as exhaustive assurance.
  Preserve unknown paths after a confirmed violation. Zero findings is valid.

## Checks

Discover relevant configured checks, installed tools and browser/connectors; prefer
project commands and pinned versions. Inspect scope, side effects and prerequisites
before execution. Follow mission limits for external calls, disposable resources
and fixture writes; report unmet permissions/setup and continue with other evidence.
For audits, no implicit installation, migrations, restart, project/service changes,
auto-fix, setup or upload; package runners must not silently download missing tools.
Coordinate shared checks with their owner; account for temporary resources as
required by the workflow.

Tool diagnostics remain candidates: verify reachability, suppressions and
counterevidence. Failed/partial scans limit coverage. Attribute tool scores to
their own rubric. Record version, command/interaction, target/configuration,
completion/exit status, evidence locator and actual scope; name useful skipped
checks and reasons. Redact credentials and unrelated sensitive output.

When a ledger is requested, return obligation IDs/proposed states and evidence
references, candidates with expected/source, trigger/mechanism/location, impact,
support/counterevidence and smallest resolving action, plus unknowns and limits.
Reference shared framing instead of repeating its protocol/metadata.
