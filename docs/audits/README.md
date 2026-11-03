# Audits

An audit finding is a known defect in OAK recorded so it cannot be quietly lost. A finding is not an objective. A task commits the project to work; a finding only states that something is wrong and keeps it visible until it is fixed or consciously accepted.

The directory is the index. **Findings still needing work are exactly the files in `docs/audits/`**, and everything in `docs/audits/archived/` has reached a terminal state. There is no list to maintain and nothing to keep in sync.

Findings usually arrive one at a time during ordinary work. A deliberate review pass is several findings opened together, still one file each.

## One file per finding

Each finding is its own file, named `{id}-{slug}.md`. The `id` is the stable handle cited elsewhere, prefixed by type and sequential within that type:

- `CF-` — contract finding: a shipped skill contradicts a committed decision, another skill, or itself. OAK distributes contracts as text, so a contradiction between them is a defect even when nothing executes incorrectly.

Add a prefix when a genuinely different type of finding appears. Do not reuse a prefix for a class it does not describe.

A finding is never deleted. On reaching a terminal state it is moved into `archived/` with `git mv`, kept for history.

## Format

```yaml
---
id: CF-1
type: contract
title: one sentence stating the defect
severity: medium              # critical | high | medium | low
status: open                  # open | resolved | closed | accepted
found_in: charter 0.2 @ 2ed03b6
resolved_in:                  # version that carried the correction; omit while open
verified_by: >
  the named check that keeps it fixed — see below
---
```

Status values:

- `open` — known, not yet addressed.
- `resolved` — the cause has been corrected, but the `verified_by` check has not yet passed.
- `closed` — corrected, with a `verified_by` check that passed so it cannot silently return.
- `accepted` — deliberately tolerated with the reasoning recorded; no fix planned.

`closed` and `accepted` are terminal: move the file to `archived/`. `open` and `resolved` are not, so those files stay in `docs/audits/` where the remaining work is visible.

`resolved` exists because a correction and its proof do not always land together. Without it, a corrected finding would sit at `open`, which says it was never addressed, and only prose would tell the two apart. A `resolved` finding returns to `open` if verification fails or shows the correction was incomplete.

Set `resolved_in` on entering `resolved` — it records the version that carried the correction, not the version that reached a terminal state. For `accepted`, record where the decision was made.

`accepted` is not `abandoned`. Abandoning a task means the objective stopped mattering. Accepting a finding means the defect was examined and judged tolerable, and that judgment is the record a reader needs in order not to re-report it.

`found_in` anchors discovery, not root cause. Name the skill and its version plus the commit when the finding is in a skill, or the commit alone otherwise. This is imprecise while a released `(skill, version)` can still correspond to more than one content state; see [`../tasks/establish-immutable-oak-release-identity.md`](../tasks/establish-immutable-oak-release-identity.md).

## `verified_by`

Every finding carries `verified_by`. While a finding is `open` or `resolved` it may be a plan (`pending — proposed: …`); a finding does not reach a terminal state without a concrete value that has passed.

A check has to satisfy four properties, in order of how much they matter:

1. **Seen red.** A check never demonstrated to fail against the unfixed behavior is not evidence that it protects anything.
2. **Targets the mechanism, with the real adversary.** The fixture must contain what actually caused the failure, not a tidy illustration of it. A check that pins a plausible proxy reads as protection while covering nothing.
3. **States its cadence.** How often it runs is the protection. A check that runs rarely leaves a long window.
4. **May honestly be "no".** Some findings have no clean mechanical check. `not mechanically verifiable — {what would be observed instead}` is a valid value. A requirement that cannot be satisfied honestly gets bypassed, and the field becomes theatre.

OAK does not enforce this field yet. A skill contract is prose interpreted by a harness, so its strongest available check is a behavioral evaluation under [`../evaluations/`](../evaluations/) rather than a unit test. Enforce the field once the tooling can run the checks findings name.

These properties are adopted from the audit practice in Orion-IV, another project, where `verified_by` is enforced by a test and a recurrence established that treating regression coverage as optional was insufficient.

## Why files rather than a tracker

Findings live in the repository so they travel with the code, appear in diffs and review, and can be read offline by an operator or an agent without a tracker API. Unlike a charter, a finding carries no lifecycle authority: anyone may open one, and no activation gate applies.

This is a ledger for the project's own memory, not a workflow tool. Keep it minimal.
