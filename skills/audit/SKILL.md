---
name: audit
description: Audit a repository, component or diff with fresh-context specialists; verify obligations and findings, report evidence and limits, and compare prior audits. Use only when explicitly invoked; does not fix issues or replace formal independent review.
license: MIT
metadata:
  author: MjStryker
  category: review
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.4"
disable-model-invocation: true
---

# Audit

Investigate and report only. No project edits, fixes, durable tasks, risk acceptance
or completion transitions. Persist only separately requested artifacts; saving a
report authorizes that report alone. Zero confirmed defects is a valid outcome.
This audit is not a formal independent review under any selection policy.

Contract 0.4 uses qualitative obligations, evidence and limits, without audit scores,
weights or numerical coverage gates. Selection defaults to `same-model`; other
policies are defined in the execution reference. Earlier reports retain their
original contract, rubric and profile interpretation.

## 1. Frame

Read [execution.md](references/execution.md) before initial searches: it defines
history exposure, neutral briefs/private checkpoints, selection, checks and resumes.

Establish requirements/sources, non-goals, scope, exact target commit and dirty
state (or concrete non-Git identity), and exact diff baseline when applicable.
Ask only for missing facts or decisions that materially change the audit.

Locate profiles in `references/specialists/` in an installed bundle. Use
`../../agents/` only if `../../README.md` identifies OAK and
`../../scripts/install-skills.sh` exists. Otherwise report the missing package and
stop; never substitute arbitrary native agent definitions. Read `README.md`,
`common.md` and only the relevant profiles; explain role selection.

Before investigation, read [obligations.md](references/obligations.md) and freeze
the bounded obligation grid and selection policy.

## 2. Execute

Apply that execution contract's check ownership, permissions and lifecycle rules.
Supply each expert its neutral brief, `common.md` and selected profile. Explicitly
require a compact ledger, no final verdict/score, recursive delegation or user questions;
the orchestrator owns delivery. Keep shared protocol/metadata in the brief once.

## 3. Consolidate

Read [verification.md](references/verification.md). Treat expert states and findings
as candidates; inspect evidence for every retained confirmed defect and consequential
assessment. Consolidate duplicate mechanisms and meaningful checks without defects.
Keep unresolved claims and unknown paths visible. Isolate evidence if the target
changes; re-establish identity instead of merging different versions.

For consequential disputes, optionally run one fresh challenger under the frozen
policy with the neutral brief, candidate ledger and evidence, without self-review
or confidence. Require falsification, not new findings. Resolve objections with
evidence or leave them unresolved; agreement is not confirmation.

## 4. Compare and deliver

After initial investigations, read [report.md](references/report.md) for historical
comparison, stable IDs, a short operational conclusion and one consolidated ledger.
Recheck prior claims; do not inherit their severity or status. Return the report in
the conversation unless persistence was requested, following that reference's rules.
