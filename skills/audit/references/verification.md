# Verification and evidence ledger

Apply the specialist common evidence contract during consolidation. For each
candidate, inspect expected behavior/source and accepted constraints, mechanism,
reachability, trigger, consumers, support and counterevidence. Reproduce when
permitted and useful; otherwise name substitute evidence and uncertainty. Establish
provenance against the exact target/baseline. Keep concrete, falsifiable, material
claims; an unknown is consequential only for a named scoped path/requirement.

Claim status concerns the current target: `confirmed` requires evidence;
`false positive` means refuted/already corrected; `not established` means unresolved.
Keep it separate from historical status ([report.md](report.md)) and disposition.
Recommend the smallest complete fix/resolving check, defer, or cite an existing
acceptance decision; the audit grants no correction or acceptance authority.
Consolidate symptoms of one mechanism, retaining contributing specialties.

Severity follows demonstrated impact and prerequisites: `critical` catastrophic
compromise/loss; `high` major security/correctness/availability impact; `medium`
material bounded failure; `low` minor demonstrated impact. An unresolved risk may
carry a labelled conditional impact estimate; it is not a confirmed finding and
does not fail an obligation. Do not add a numerical confidence score.

## Consolidated records

Reference frozen framing instead of repeating it:

- **Obligation:** ID, final state and finding links; evidence references and covered
  conditions; remaining paths/conditions and smallest resolving check.
- **Evidence:** ID/locator, producer (expert/tool/orchestrator), type (source, test,
  runtime response, browser, log), target and actual scope. Tool execution records
  follow `common.md`.
- **Root verification:** action/result/locator: inspected evidence, rerun command,
  reproduced journey, or not personally checked. Reading an expert's output does
  not become personal reproduction; keep attribution.
- **Finding:** stable ID, specialties, title, expected/source, trigger/mechanism/
  location, impact, support/counterevidence, claim status, severity, provenance,
  disposition and smallest recommendation/resolving check.

Source can establish a structural defect, not a rendered layout or completed
journey. Without a browser, infer neither visual success nor failure. A violation
on one path does not erase sibling unknowns, even when the obligation fails.
Narrow or discard conclusions beyond evidence; exclude false positives from the
final defect list, retain material unresolved claims as unknowns, and record
meaningful checks that found no defect without claiming blanket assurance.
