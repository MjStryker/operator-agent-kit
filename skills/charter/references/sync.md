# Sync

Update a bound `draft` or `active` charter with durable decisions and evidence from the current discussion. Do not edit a `complete` or `abandoned` charter.

Classify candidates:

- `no-op`: chatter, implementation progress, plan steps, or facts already represented;
- `additive`: new evidence, scope disposition, decision, task/review reference, or clarified criterion that does not conflict;
- `conflict`: a change to the objective, existing decision, scope boundary, non-goal, or definition of done.

Show one proposed patch. For each conflict, state the charter text, discussion text, recommended resolution, and why. Never silently prefer the conversation over the repository record. Apply only the operator-accepted patch after the write guard, preserve unrelated sections, and update `updatedAt`.

Reconcile the whole charter against each accepted decision. Remove or rewrite unresolved, deferred, baseline, criterion, or decision text that the accepted patch settles, supersedes, or contradicts. “Preserve unrelated sections” does not justify retaining stale statements. Call out every such reconciliation in the proposal; do not silently broaden it beyond the accepted decision.

An active charter may be corrected, but make the operator-visible contract change explicit. If the accepted patch changes Objective, Scope, Key decisions, Definition of done, or Non-goals, include `status: draft` in the proposal: the changed commitment requires another explicit activation decision. Additive Baseline evidence, task references, review pointers, and non-contractual clarifications may remain active when they do not alter the commitment. Do not rewrite an active charter merely to make implementation progress look consistent with the original commitment.
