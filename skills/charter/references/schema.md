# Schema

One Markdown file per charter: `{id}.md` in `CHARTERS_DIR`.

## Header

```yaml
---
id: durable-workflow
title: Durable workflow
status: draft
createdAt: 2026-09-19T10:00:00Z
updatedAt: 2026-09-19T10:00:00Z
---
```

- `id`: kebab-case `[a-z0-9-]+`, at most 64 characters, equal to the filename stem.
- `title`: human title matching the body H1.
- `status`: `draft` | `active` | `complete` | `abandoned`.
- `createdAt`: ISO-8601 UTC, never rewritten.
- `updatedAt`: ISO-8601 UTC of the last charter write.

No additional header fields. Project-specific metadata belongs in the body or a project-owned ledger.

## Body

All headings are required. Use `_None._` only where the section legitimately permits it.

```markdown
# {title}

## Objective
The single project capability this charter commits to. State an observable outcome, not a solution or task list.

## Why now and what it unlocks
Why this capability earns project commitment and what becomes possible after it exists.

## Baseline
Relevant behavior and constraints established from current evidence. Distinguish observation from inference and cite repository paths or external sources for material claims.

## Scope

### In scope
Everything necessary to establish the objective.

### Deferred
Excluded work with a named destination or condition for reconsideration.

### Out of scope
Excluded work with a reason.

### Unresolved
Material decisions required before activation. `_None._` when settled.

## Key decisions
Operator- or policy-owned design decisions with rejected alternatives and reasons when known. Label `D1.`, `D2.`, and never renumber.

## Definition of done
Observable acceptance criteria as plain bullets, without checkboxes or other tick state. Each item must permit a reader to disagree about whether it was met. Completion is recorded only in Outcome, by `close`.

## Non-goals
Load-bearing boundaries that prevent convenient scope expansion.

## Tasks
References to project-owned task records or external tracker items. Do not duplicate their contracts. `_None._` is valid before decomposition.

## Reviews
Pointers and verdicts for persisted optional reviews. `_None._` when no review has been recorded. Do not paste review bodies into the charter.

## Outcome
Filled only by `close`: delivered behavior, verification evidence, missing verification, accepted residuals, and named follow-ups. `_Not closed._` before close.
```

Extra project-required sections are allowed. Do not delete or rewrite them merely to normalize formatting.

## Lifecycle

- `draft`: scope and decisions are still being settled; implementation has not been authorized by the charter.
- `active`: the operator accepted the commitment; downstream tasks and plans may proceed.
- `complete`: closeout established the accepted outcome. The record is frozen.
- `abandoned`: the operator ended the commitment with the reason recorded in Outcome. The record is frozen.

A draft becomes active after the operator explicitly accepts the activation patch. Independent review is optional unless project policy requires it.

A material sync to an active charter returns it to `draft`; see `sync.md`. Historical review pointers remain, and reactivation requires another explicit operator acceptance.
