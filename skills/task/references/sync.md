# sync

Pull durable information from **this conversation** into the bound/named file. The **file is source of truth**. Task lookup, local discussion binding, and the write guard are in `core.md`. Schema and premises are in `schema.md`.

If the file is missing: say so and offer `define` or `list`. Do not create a file from `sync`.

Harvest only what belongs in the schema: objective refinements, new or changed sub-steps, relationships, constraints, operator-made key decisions, success/failure, open questions about those, and **premises** when the conversation brings a durable fact, new evidence, a contradiction, or a new invalidation condition. Ignore implementation progress, plans, “next we should…”, chatter, failed attempts that did not become decisions, tool logs, and code that already lives in the repo.

Agent-produced factual claims go in Premises with `Authority: agent`. Do not promote them.

## Classify each candidate

- **no-op** — omit
- **additive** — new key decision, new/changed sub-step, new non-conflicting relationship, new premise, new `supports:`, `supports (independent):` or `contradicts:` evidence pointer on an existing premise, or open question that does not contradict the main objective, an existing decision, or an existing premise. **Evidence against a premise is additive**: append a `contradicts:` pointer; the derived support becomes `contested`/`refuted` at read time. Do not rewrite the Claim.
- **conflict** — chat disagrees with a file statement, including rewriting the main Objective, bars, constraints, or an existing decision, or changing a stored premise's Claim, Basis, Authority, or an existing pointer's independence marker (including replacing it via `SupersededBy`). A wording refinement of the main Objective that keeps the same goal is still a conflict (prefer file unless the operator is clearly tightening it).

## Conflict question

Required, per conflicting item. Do not write that item until the operator answers. End the proposal by explicitly asking which conflicting replacements the operator accepts. A confirmed conversation decision does not by itself accept the proposed file edits; ask about recording the change rather than reopening the decision.

```
Section: {heading} / {item}
File: {verbatim or close paraphrase of the file}
Chat: {what the conversation now says}
Recommendation: keep-file | take-chat | merge: {one-line merge}
Why: {one sentence; heuristic below}
```

Recommendation heuristic (still ask):

- Prefer **file** for the main Objective, Success, Failure, Constraints (operator-locked; rare to move)
- Prefer **chat** for a new Key decision the operator clearly made later
- Prefer **chat** for additive Sub-steps that refine the goal without contradicting the main Objective
- Prefer **chat** for a new Relationship explicitly established by the operator; ask on replacement, removal, or a cycle
- Prefer **chat** for a new Premise or new evidence the operator (or an inspection they asked for) clearly established; keep `Authority: agent` if only the agent asserted it
- Prefer **file** when the chat drifted without operator confirmation, or when a “sub-step” is actually an implementation task
- Status changes (`open` → `done`, etc.) are always conflicts
- Changing a premise's Claim, Basis, or Authority, or superseding it, is a conflict; adding `contradicts:` evidence is not

## Write

**Additives:** show as one proposed patch. Do not apply until the operator confirms the patch (one confirmation, not per bullet).

Write only the accepted items, after the write guard re-read. Set `updatedAt`, then add or confirm the local discussion binding without modifying the task contract. Do not reorder or rewrite unaffected sections for style. Do not renumber `P{n}` / `D{n}`.
