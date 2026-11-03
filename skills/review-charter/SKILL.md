---
name: review-charter
description: Optionally review a project charter against its intended capability and repository evidence. Use explicitly to find consequential scope, decision, and acceptance gaps without editing the charter.
license: MIT
metadata:
  author: MjStryker
  category: review
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.5"
disable-model-invocation: true
---

# Review a charter

Review only. Do not edit the charter, tasks, plans, source, or implementation files. After the verdict, a review record may be created only through the confirmation flow below.

Review is advisory by default. It does not authorize or block activation unless project policy explicitly makes it a gate.

Use a fresh context when available and authorized. Give the reviewer the objective, repository access, applicable project policy, and charter, but withhold the author's self-review and confidence. If a fresh-context handoff fails or is unavailable, continue the review directly instead of stalling, disclose reduced independence, and mark it `reduced` in the record. A separate discussion that did not author the current charter version qualifies as `fresh`, unless project policy adds a condition such as a different model; see the record's `independence` field.

Prefer accuracy over finding volume. A finding must state a falsifiable concern and cite repository evidence when accessible. Discard unsupported suspicions and style preferences.

Check whether:

- the charter advances one coherent project capability;
- Baseline matches current repository behavior;
- every material concern is in scope, deferred with a destination, out with a reason, or unresolved;
- decisions name consequential alternatives and do not contradict project authority;
- Definition of done can establish the capability rather than merely confirm that listed work occurred;
- non-goals prevent likely scope drift;
- referenced tasks are independently meaningful outcomes rather than implementation steps;
- applicable compatibility, migration, failure, security, operational, and rollback boundaries are dispositioned;
- implementation can begin without making an unrecorded material decision.

For each surviving finding include issue, location, evidence, smallest correction or exact verification, impact (`blocker | high | medium | low`), and status (`confirmed | likely | needs-verification`).

Then provide coverage evidence, remaining unknowns, and one verdict: `ready to activate | ready after named verifications | revise before activation | blocked on a decision or missing evidence`.

Read [references/record.md](references/record.md) before offering to persist the result. Show the complete review record and ask the operator to accept it. Write nothing before acceptance. Immediately before writing, re-read the charter and recompute its complete-file SHA-256; if either it or `updatedAt` differs from the proposed record, discard the record and review the new version. Persisting the review must not modify the charter.
