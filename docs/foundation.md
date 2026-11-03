# OAK foundation

**Status:** adopted on 2026-09-28, after a cold review on a different model
than the author.

This document states what OAK is for and how its components relate to that
purpose. It is the authority for OAK's principle and obligations. A component
that disagrees with it is a defect to correct, not a second source of
authority.

## Principle

A consequential agent claim, decision, or action must remain bounded by
operator-authorized intent and inspectable evidence, with its provenance
preserved across conversations and tools.

Portable skills are how OAK currently delivers this principle, not what OAK
is. Components are valued by how well they serve operator authority,
evidence discipline, and continuity.

## Obligations

The principle breaks into four obligations. A component identifies the
obligations it serves and need not serve all four.

- **Intent.** Work stays within the operator's objective and scope. A proposed
  solution is not mistaken for the objective, and a change of scope is
  surfaced rather than made silently.
- **Evidence.** A consequential claim identifies what supports it, shows
  whether it was observed, inferred, or is opinion, and does not exceed that
  support. An agent checking its own work is not independent verification.
- **Continuity.** Across conversations and tools, the operator's
  intent, material decisions, constraints, provenance, and unresolved
  questions remain recoverable from their sources.
- **Authorization.** Exploration may broaden the problem and produce evidence,
  options, and open decisions, but it does not authorize implementation.
  Execution begins only from explicit operator authorization or an accepted
  contract that establishes the objective, scope, constraints, observable
  outcome, and expected verification. When those conditions already exist,
  work may begin directly in execution.

## Layers

A capability can be delivered through any of these layers. It uses only the
ones it needs.

| Layer | What it is | Current OAK example |
|---|---|---|
| Principle | Reusable intent that does not depend on an environment | this document |
| Contract | Prose an agent interprets and applies | each `skills/*/SKILL.md`; the task schema in `skills/task/references/schema.md` |
| Deterministic mechanism | A tool that performs a repeatable operation the same way every time | `scripts/install-skills.sh` |
| Adapter | An environment-specific mapping of a contract onto what a harness provides | `disable-model-invocation: true` in skill frontmatter; `agents/openai.yaml` with `allow_implicit_invocation: false` |
| Harness | Observation or enforcement by the environment the agent runs in | a harness honoring the adapter setting above; a read-only sandbox; a denied tool |

An adapter translates; it does not change a contract's meaning. A contract
does not depend on a particular adapter existing.

## Effective guarantees

Where an obligation's strength depends on the environment, a component that
claims it states how strongly it holds in each environment the component
supports:

- **documented** — a contract states it; nothing checks whether it happened.
- **observable** — a departure leaves a record that a person or tool can
  inspect afterward, such as a diff, a transcript, or a committed record.
- **enforced** — the environment prevents the departure.
- **unsupported** — the environment cannot provide it.

The same obligation can hold at different strengths in different
environments. Explicit-only invocation, for example, is enforced where the
harness honors the adapter setting and only documented where it does not.
Audit `verified_by` checks are documented but not yet enforced
([`docs/audits/README.md`](audits/README.md)).

Never describe a guarantee as stronger than the environment provides. When a
capability is missing, say so and continue at the weaker guarantee rather than
changing what the obligation means.

## Ownership

Reusable intent belongs here. Operational behavior belongs to the component
that performs it: the skill, project contract, deterministic tool, adapter, or
harness. Consumers reference the owning definition instead of keeping their
own version of it.

| Definition | Owner |
|---|---|
| Charters, tasks, plans, and how they compose | [`charters/workflow.md`](charters/workflow.md), with [`charters/README.md`](charters/README.md), [`tasks/README.md`](tasks/README.md), [`plans/README.md`](plans/README.md) |
| Task contract fields and premises | `skills/task/references/schema.md` |
| Audit findings and `verified_by` | [`audits/README.md`](audits/README.md) |
| Each skill's behavior | that skill's `SKILL.md` and `references/` |
| Recon versus audit | [`skills/recon/SKILL.md`](../skills/recon/SKILL.md); what an audit finding is, [`audits/README.md`](audits/README.md) |

## Proportional use

OAK is explicitly composed. No request requires a charter, task, plan, review,
or every stage of the work loop; use the smallest step that changes a
decision or reduces a concrete risk. Short paths remain valid; see
[`charters/workflow.md`](charters/workflow.md), Operating model.

## Producers and consumers

A field, classification, or mechanism is added only when something
produces it and something meaningfully consumes or enforces it. Deterministic
tools are introduced for demonstrated repeated, stateful, or error-prone
friction, not to represent the foundation.

## Adopting the foundation

A new or revised component adopts the foundation by stating, in its own
documentation and at the depth its size warrants:

1. **Layers** — which layers it uses.
2. **Obligations** — which obligations it serves, and the effective guarantee
   of each in every environment it supports. An obligation that depends on an
   environment the component cannot check is stated as such, not assumed.
3. **References** — which owned definitions it relies on, linked rather than
   restated.
4. **New mechanisms** — for any field, classification, or mechanism it
   introduces, what produces it and what consumes it.
5. **Authorization** — whether it explores, executes, or both, and what
   authorizes its execution.

A component reports an unsupported or weaker guarantee in two places: in its
documentation, as above, and at the moment it runs, when the environment
turns out not to provide what the component relies on.

A small skill may cover all five in a few lines.
