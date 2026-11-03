# Schema

One Markdown file per task: `{id}.md` in its personal or project store. Required headings are always present; use `_None._` when empty.

## Naming

- `id` = kebab-case slug, `[a-z0-9-]+`, max 64 characters, unique across the active and archived directories of its store, **equals the filename stem**
- On `define`, slugify the title (lowercase, hyphens, strip other characters, trim hyphens, truncate to 64). If the operator supplies a name, slugify that instead.
- On collision: ask for a distinct id. Do not silently suffix.

`decompose` / `list` / `resume` / `sync` / `archive` identify active tasks by scoped locator, id, title, or local discussion binding as defined in `core.md`. Archived tasks are listed or read as relationship evidence, not rebound. Title is display only.

## Header

```yaml
id: shared-session-state
title: Session state remains consistent across clients
scope: project
status: open
createdAt: 2026-09-10T14:58:00Z
updatedAt: 2026-09-10T16:20:00Z
```

| Field | Required | Values / notes |
|---|---|---|
| `id` | yes | Filename stem |
| `title` | yes | Human title; body H1 matches |
| `scope` | yes for new files | `personal` \| `project`. A pre-0.4 file without it is a legacy personal task. |
| `status` | yes | `open` \| `paused` \| `done` \| `abandoned` |
| `createdAt` | yes | ISO-8601 UTC, set on `define`, never rewritten |
| `updatedAt` | yes | ISO-8601 UTC, set on every successful write. Last write, **not** claim validity. |

No other header fields. Optional project/repo context belongs under **Constraints and non-goals** if it constrains the objective.

## Body

```markdown
# {title}

## Objective
The main goal. What done looks like. Not a solution, not a plan. Stable after define; rewrite only as a rare refinement (conflict in sync).

## Sub-steps
Optional decomposition of the objective. Still the goal (parts of “what done means”), not implementation tasks. Add or modify freely via sync when they do not contradict the main objective. A child task created by `decompose` is referenced here by id; its own file defines its contract.

## Success
Observable signs the objective is met. Operator-owned.

## Failure
Observable signs this is the wrong outcome, or that work should stop.

## Constraints and non-goals
Hard constraints, then non-goals. Do not silently add scope. A constraint that rests on an external fact needs a **Premise**; the constraint itself is authority, not a scored claim.

## Premises
Durable factual claims on which the objective, constraints, or decisions depend. Labeled `P1.`, `P2.`, … in order of addition; never deleted or renumbered, only superseded. Record basis, authority, evidence, assessment time, and any known revalidation condition. Support and validity are **derived when the task is read**, never stored. `_None._` when empty.

## Key decisions
Labeled `D1.`, `D2.`, … in order of addition; never renumbered. Each: the decision, and why if known. Authority is the operator or a policy; justification may rest on Premises. Not a changelog of the chat, not a list of commits.

## Open questions
Unresolved material questions about the objective, bars, or trade-offs. Remove when answered (answer goes to Key decisions, Constraints, Premises, or a sub-step). Not “what should we code next.” Already unresolved: do not apply the four axes here.

```

Task contracts do not store harness discussion ids. Pre-0.4 files may contain a legacy `## Sessions` section; preserve it without adding entries. New files omit it.

### Optional relationships

Add `## Relationships` only when the task consumes context or a verified result owned by another task. Do not duplicate the referenced task's objective, status, decisions, premises, or criteria.

```markdown
## Relationships
- Charter: `docs/charters/durable-workflow.md`
- Parent: `parent-task-id`
- DependsOn: `other-task-id` — result this task builds on
- Uses: `parent-task-id#P2`, `parent-task-id#D1`
```

- `Charter` identifies the project capability this task contributes to. It is valid only on a project task and uses a project-relative charter path.
- `Parent` identifies the objective this child contributes to.
- `DependsOn` identifies another task whose result this task builds on. The consumer owns this dependency declaration. The dependency is satisfied once that result is available to build on, for example on a branch the consumer can stack on; it does not require the dependency's merge request to be merged or its status to be `done`. When a merge or a `done` status really is required, say so in the line's description.
- Tasks are objective boundaries, not delivery units. How many branches or merge requests carry the work is a plan decision: several tasks may ship in one merge request, and one task may span several.
- `Uses` references premises or decisions at their owning task. Do not copy them into the consumer.
- Bare task ids resolve within the current task's store, checking the active directory first and then its `archived/` directory. Cross-store references use `personal:{id}` or `project:{id}` and follow the same order. Signal duplicate active/archive ids, missing or invalid references; do not silently discard them.
- Parent and dependency relations must not form cycles.

In a parent's `## Sub-steps`, reference a materialized child without repeating its contract:

```markdown
- `child-task-id` — contribution to the parent objective
```

## Premises

Apply the four axes only to **factual premises**. Do not mark the rest of the file.

| Content | Treatment |
|---|---|
| Objective, success, failure | Operator contract. Not a claim to score. |
| Decision | Operator or policy authority. Justification may rest on premises. |
| Constraint | Explicit authority. If it rests on an external fact, that fact is a Premise. |
| Factual premise | All four axes. |
| Open question | Already unresolved. |
| Status, scope, `createdAt` / `updatedAt` | Management metadata, not epistemic. |

**Store what lets support and validity be computed. Do not store `current` or `corroborated`.**

```markdown
P1. **Claim:** The session state is shared between all clients.
   - Basis: observed
   - Authority: import
   - Evidence:
     - supports (independent): `https://example.invalid/example/example-app.git` `src/session/state.ts` @ `a1b2c3d`
   - AssessedAt: 2026-09-11T08:00:00Z
   - RevalidateWhen: `src/session/` changes (same repo)
```

Labels `P1`, `P2`, … and `D1`, `D2`, … are written literally. Premises are never deleted or renumbered; retire one by setting `SupersededBy`.

### Stored (producer writes)

| Field | Required | Role |
|---|---|---|
| Claim | yes | The factual statement |
| Basis | yes | Declared by whoever produces the claim (`observed`, or another short declared token) |
| Authority | yes | Who may establish or promote it: `operator` \| `policy` \| `import` \| `agent` |
| Evidence | no | List of pointers, each marked `supports:`, `supports (independent):`, or `contradicts:`. Needed for corroboration and contestation. |
| AssessedAt | yes | ISO-8601 UTC when this record was last assessed |
| EffectiveFrom | no | Applies only after this instant |
| RevalidateAfter | no | After this instant → `stale` |
| ExpiresAt | no | After this instant → `expired` |
| RevalidateWhen | no | File, schema, dependency, or event whose change invalidates the observation |
| SupersededBy | no | `P{n}` or `D{n}` that replaces this one |

`Authority` values: `operator` — the operator stated it; `policy` — a written rule the operator has adopted; `import` — taken from an external authoritative source (spec, vendor doc, upstream repo) named in Evidence; `agent` — asserted by an agent from its own inspection. An agent-produced claim stays `Authority: agent` until the operator or a policy promotes it.

### Evidence pointers

Mark a supporting pointer `supports (independent):` only when the referenced artifact was produced independently of the claim's producer: by the operator, by an external source, or by a different model in a separate context. Evidence the producer created or wrote down itself, including a record of another model's output written by the producing session, stays a plain `supports:`. When independence is unknown, use plain `supports:`. An agent never upgrades its own pointer to independent; the operator may.

Evidence in a personal task must be resolvable from any workspace: name the repository remote URL, or an absolute path when no remote exists, plus path and revision. Evidence in a project task may use a project-relative path plus revision. A citation names the document and locator.

### Derived at read time (never written)

Support — from the stored Evidence list only (the skill does not go looking for new evidence; that is `sync`'s job):

- `uncorroborated` — no supporting pointer is marked `supports (independent):`
- `corroborated` — at least one `supports (independent):` pointer
- `contested` — both supporting and `contradicts:` pointers present
- `refuted` — `contradicts:` pointers present and no supporting pointer

A supporting pointer is either form of `supports`. Pointers written before the independence marker existed are plain `supports:`, so their premises read as `uncorroborated` until the operator marks an independent pointer.

Validity — from dates, revisions, and invalidation events, **not from elapsed time alone**. Check in this order; first match wins:

- `not_yet_valid` — `EffectiveFrom` is in the future
- `superseded` — `SupersededBy` is set
- `expired` — `ExpiresAt` has passed
- `stale` — `RevalidateAfter` has passed, or a `RevalidateWhen` event has occurred, or a supporting evidence pointer's referenced path differs between its recorded revision and the current checkout of that repo (`git diff --quiet {revision} -- {path}` is non-zero). **HEAD having moved past the revision is not by itself stale.**
- `current` — recorded validity conditions still hold
- `unbounded` — no validity condition was defined

`unbounded` means “cannot be aged automatically,” not “true forever.”

If `RevalidateWhen` or an evidence revision cannot be inspected (repository not present, path or revision not resolvable), do not call the premise `current`. Say validity is **unchecked** (resume signal only, not a stored field).

Display tuple when a premise must be shown:

```text
[observed · uncorroborated · current · import]
```

Order: basis · support · validity · authority.

## Legacy Sessions

A pre-0.4 task may retain `## Sessions` for backward-compatible lookup. Treat it as frozen legacy metadata. New and updated bindings belong in the local `BINDINGS_FILE` defined by `core.md`; never copy local discussion ids into a shareable task.
