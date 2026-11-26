# OAK — Rules for agents working on this repository

These rules apply to any agent editing or explaining OAK itself. They do not
apply to projects that install OAK skills; those follow their own rules.

## Read before explaining

- Before explaining an OAK concept (charter, task, plan, recon, review,
  workflow), read its owning definition first: `docs/charters/workflow.md`,
  `docs/charters/README.md`, `docs/tasks/README.md`, `docs/plans/README.md`,
  and the relevant `skills/*/SKILL.md` and `references/`.
- Label consequential claims as read (with the path), inferred, or opinion.
  Leave a gap open rather than filling it with plausible content that has no
  source.

## Terminology

- "Operator" means only the generic role: whoever is directing the agent.
  Never use it for a specific person. When describing a specific event, name
  the project, session, commit, or artifact instead.

## Reviews

- A formal independent review (`review-charter`, `review-plan`, `review-mr`,
  and similar) must run on a different model than the one that authored the
  work, in a read-only context, without the author's self-review or
  confidence. When that is not possible, say so and record the reduced
  independence rather than presenting the review as independent.

## Skill trials

- After changing a skill's behavior, propose paired live trials on Codex and
  Claude Code ([`tests/skills/README.md`](tests/skills/README.md)) before
  claiming an improvement. Passing fast checks are not behavioral evidence.

## Commits

- Commit only when the operator explicitly asks for that specific commit.
  Approval to perform a change is not approval to commit it.
- Commit messages are a short imperative subject line with no body and no AI
  attribution trailer (for example `Harden charter activation`).

## Public repository

- OAK is public. Files, examples, test fixtures, commit messages, and pull
  request or issue text must not contain private data: personal names other
  than the declared author, email addresses, home directory paths, internal
  hosts or repositories, company or client names, credentials, or material
  taken from private projects.
- Build examples and fixtures from invented, generic cases.
- Before proposing a commit, review the diff for such data and report what
  was checked.
- `scripts/check-private-data.py` runs with the fast checks and catches
  common patterns only; it does not replace that review.
