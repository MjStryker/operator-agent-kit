# Delivery and historical comparison

## Delivery

Use the user's language. Start with a short operational conclusion: principal
material defects (critical/high first), decisive unknowns and next decisions/checks.
Zero confirmed defects within inspected scope is valid. For suspended work, give
an explicitly incomplete provisional handoff under [execution.md](execution.md).

Link one consolidated ledger and necessary evidence, not parallel expert reports,
adjudication narratives or rejected suspicions presented as defects. The ledger
contains the records in [verification.md](verification.md) and references:

- report ID/time, contract/profile versions, target/dirty state,
  exact baseline if applicable, requirements, scope/non-goals and frozen grid;
- role rationale, selection/context guarantees versus exposed identities, exposure
  limits, mission lifecycle/IDs, check ownership, prerequisites, completed/failed/
  skipped checks, and temporary resource disposition from the execution checkpoint;
- obligation/finding/evidence records, unknowns and resolving actions, separating
  severity, certainty, disposition and history. Optional improvements are not defects.

Describe inspected and unverified paths with evidence and resolving checks.
Do not calculate audit scores or numerical coverage, or wait for a percentage
threshold to deliver. Keep tool scores separately attributed.

Default is conversation. Save Markdown only when requested, at the specified or
project-declared location; otherwise propose a path before writing. Keep previous
reports intact. Never store a whole report in OAK's `docs/audits/` individual-defect
ledger, or automatically create tasks/finding records.

## Compare after initial investigation

Use a supplied/project-declared baseline, otherwise the latest dated report in the
project audit location for the same scope. State selection; ask about materially
ambiguous alternatives. Do not search unrelated personal stores. If none is
available, say no baseline compared. Previous reports are evidence, not authority.
Recheck old claims on the current target, personally or through a narrow follow-up.

Assign IDs such as `AUD-001` initially. Reuse an old ID for the same requirement,
mechanism and trigger despite changed title, line or specialty. Continue the baseline
sequence for new IDs; preserve duplicate aliases and disclose ambiguous matches.
Highlight persistent defects, then other changes. For each old finding record:

- `persistent`: same defect currently confirmed;
- `aggravated`: persistent with demonstrated increased reach/impact;
- `corrected`: current behavior satisfies the requirement and a change since the
  prior target explains it; disappearance alone is insufficient;
- `refuted`: evidence about the prior target establishes the old claim was mistaken;
- `not reproduced`: relevant current check succeeds, historical cause unknown;
  distinguish neither correction nor false alarm without evidence;
- `not reevaluated`: outside scope, missing evidence or no current check.

Current claim status is separate: a current false positive can coexist with
historical correction/non-reproduction. `newly reported` does not mean newly
introduced. Cite decisions removing requirements or accepting limitations; neither
silently means corrected. A passing check does not establish regression protection.
Keep original report versions and any historical scores attributed to their old
methodology; calculate no current score or numerical delta. Compare established
mechanisms, inspected scope and evidence limits instead.
