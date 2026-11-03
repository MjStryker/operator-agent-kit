---
id: workflow
title: Coherent operator workflow
status: complete
createdAt: 2026-09-19T21:12:06Z
updatedAt: 2026-09-21T13:43:07Z
---

# Coherent operator workflow

## Objective

OAK provides independently useful, explicitly composed contracts for project capabilities, durable objectives, investigation, execution strategy, implementation, and verification without forcing the full workflow onto small work.

## Why now and what it unlocks

OAK already had task, recon, and review skills, but their relationship to project commitments and durable plans was implicit. A shared artifact model lets personal and professional projects choose proportionate ceremony while preserving scope, decisions, and evidence across agents and conversations.

This charter unlocks a repository-owned charter lifecycle, personal and project task scopes, optional durable plans, and future completion verification without conflating those responsibilities.

## Baseline

- Observed: `skills/task/` defines durable objective contracts and explicitly excludes plans and implementation logs.
- Observed: `skills/recon/` investigates repository-backed engineering objectives without planning or implementation.
- Observed: `skills/review-plan/` reviews completed implementation plans, but OAK has no planning skill.
- Observed: before this charter, OAK had no reusable charter lifecycle and task files stored harness discussion identifiers alongside shareable objective content.

## Scope

### In scope

- A repository-owned charter contract and lifecycle.
- Optional independent charter review, persisted when the result needs to survive the discussion.
- Personal and project task scopes.
- Local discussion bindings separated from task contracts.
- Plans that are ephemeral by default and repository-owned only when handoff, review, or multi-session execution requires persistence.
- Explicit integration boundaries among charters, tasks, recon, plans, execution, and verification.

### Deferred

- A dedicated planning skill → reconsider after observing repeated durable-plan use.
- Task completion or verification mode → a separate task-design objective after the charter lifecycle settles.
- External task-tracker adapters → add when a concrete GitHub, Linear, Jira, or equivalent integration is selected.

### Out of scope

- A general-purpose project-management system.
- Requiring a charter, task decomposition, or plan for every change.
- Universal milestone numbering, roadmap structure, active-charter limits, or model-review policy.
- Implementation progress tracking inside charters or tasks.

### Unresolved

_None._

## Key decisions

D1. Charters, tasks, and plans are distinct artifacts: charters own project capability commitments, tasks own independently verifiable objectives, and plans own execution steps.

D2. A task may exist without a charter or plan. A charter normally references project tasks, while planning does not silently create them.

D3. Recon supplies evidence and possible directions without silently editing downstream artifacts; explicit sync records accepted findings.

D4. Charters and project tasks are repository-owned by default. Personal tasks remain in an operator-owned store.

D5. The stable harness discussion identity is the default key for local task routing. Bindings remain local state and never become part of a shareable task contract; manual identity entry is only a fallback when the harness cannot resolve it automatically.

D6. Plans are ephemeral by default. Persist an accepted plan under `docs/plans/` only when it must survive handoff, review, or multiple sessions.

D7. Project policy may strengthen or adapt naming, review, lifecycle, concurrency, and storage rules without changing the core artifact responsibilities.

D8. Charter activation requires explicit operator approval. Independent review is optional evidence and never a default activation gate; project policy may require it when a project needs a stronger gate.

D9. A material change to an active charter's objective, scope, decisions, definition of done, or non-goals returns it to draft and requires explicit operator approval before reactivation.

## Definition of done

- [ ] `charter` can define, synchronize, activate, resume, close, and list repository-owned capability charters.
- [ ] `review-charter` can independently assess a draft charter before activation.
- [ ] `task` supports personal and project scopes without storing new harness discussion ids in task contracts.
- [ ] Existing personal task files with legacy Sessions remain readable.
- [ ] Project documentation explains when each artifact is optional, where durable artifacts live, and how they compose.
- [ ] Installation includes the new and revised skills for supported harnesses.
- [ ] Codex and at least one other supported harness distinguish a small standalone task from a charter-worthy multi-task capability without inventing missing evidence or decisions.

## Non-goals

- Proving every charter lifecycle mode in the initial release.
- Shipping planning or task-verification skills as part of this charter.
- Migrating or deleting existing personal tasks automatically.
- Storing local conversation identifiers in Git.

## Tasks

- `validate-workflow-lifecycle` — completed cross-harness lifecycle validation.

## Outcome

**Complete.** Closed 2026-09-21.

Delivered: `charter` 0.4 (define, sync, activate, resume, close, list; project-declared stores; activation by explicit operator approval), `review-charter` 0.3 (independent, advisory, persisted, version-anchored reviews), `task` 0.6 (personal and project scopes, local discussion bindings, legacy Sessions compatibility), and documentation for charters, tasks, plans, and their composition.

Verified: all seven criteria met. Evidence: routing evaluations on Codex and Claude, real lifecycle writes and store resolution on both harnesses, and an installation check placing all skills for Codex and Claude. The evaluation records are not kept in the public repository.

Not verified: `charter` 0.4 activation and its already-active stop were not re-run under a harness evaluation; the only observed use is this charter's own activation. Evaluations were isolated but not clean-room.

Deviations: D8 moved from a mandatory review gate to optional review. The deferred full lifecycle evaluation was dropped by operator decision.

Residuals: planning skill, task verification mode, and tracker adapters remain deferred as recorded in Scope. Install-time mutation of `task/references/core.md` → `establish-immutable-oak-release-identity`. Codex same-name global/project-local skill discovery is a harness constraint on evaluation setup, not an OAK defect.

## Operating model

```text
charter define → recon → charter sync → optional review-charter → charter activate
                                                              └─ project tasks

personal or project task → optional plan → execute → verify

verified project tasks → charter close
```

Common short paths remain valid:

- Clear, small objective: `task define → execute → verify`.
- Uncertain standalone objective: `recon → task define → execute → verify`.
- Shared project objective: `task define project → optional plan → execute → verify`.

## Storage ownership

- Charters: `docs/charters/` by default.
- Project task contracts: `docs/tasks/` by default.
- Personal task contracts: the operator's configured personal task store.
- Local discussion bindings: the operator's configured bindings file.
- Durable plans: `docs/plans/` by default; otherwise remain ephemeral.

Projects may replace these paths or use an external task tracker. Artifact responsibilities do not depend on the storage backend.
