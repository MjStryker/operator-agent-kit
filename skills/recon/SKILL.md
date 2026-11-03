---
name: recon
description: Scout a repository-backed engineering objective to establish current behavior, affected boundaries, constraints, risks, and unresolved decisions before the operator chooses what to do next.
license: MIT
metadata:
  author: MjStryker
  category: discovery
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.2"
disable-model-invocation: true
---

# Recon

Investigate and report only. Do not edit project files, implement the objective, or produce an implementation plan. Return with enough evidence for the operator to choose the next action.

Recon separates three roles so exploration does not flood the conversation and unverified claims do not reach the operator as facts:

- a **scout** subagent explores and returns an evidence ledger;
- the **root** agent reasons over the ledger and drafts the report;
- a **challenger** subagent tries to falsify the draft.

The root agent owns every operator-facing answer and every question to the operator. Subagents never address the operator.

## Mission

Establish:

- the objective and what a successful outcome would mean;
- facts and decisions already established;
- explicit non-goals and accepted limitations;
- unknowns that could materially change the available directions.

Resolve repository-answerable questions before asking the operator. Ask only for decisions or unavailable facts that would materially change the findings.

## Delegation

First inspect the available collaboration capabilities. A wait or polling capability alone does not mean that subagents are available. When an explicit create or spawn capability exists, delegation is required: create the scout before exploring the repository yourself, and create the challenger as a separate subagent that has not seen the scout's work in progress. Never call a wait or polling tool unless the creation call succeeded and returned a live subagent identifier.

If no create or spawn capability exists, stop before exploring. Warn the operator that subagents are unavailable, so exploration would run in the main conversation and fill its context, and the challenger would share the author's context, which weakens the challenge. Ask whether to continue without them and wait for the answer. Only on explicit confirmation, perform each role in sequence in the current context, keep the same outputs and boundaries, and repeat the warning at the top of the report. Do not simulate or announce separation that did not happen.

When the operator follows up on an earlier recon in the same conversation and a capability exists to continue its scout, continue that scout and send only what changed. Otherwise create new subagents.

Instruct every subagent to explore without modifying project files or external state.

## 1. Scout the terrain

Give the scout a packet with two separate parts:

- **Request**: the operator's objective exactly as written. Do not rephrase, narrow, expand, or answer it.
- **Context**: what the scout needs to avoid a wrong investigation: referents the request depends on, decisions, constraints, non-goals, and accepted limitations established in the conversation, target files or artifacts, and prior findings with their provenance. Omit the root agent's hypotheses, preferred direction, and conclusions.

Instruct the scout to:

1. Trace the relevant behavior end to end: entry points, ownership, reads, writes, transport, persistence, asynchronous work, consumers, and observable results.
2. Follow affected boundaries outward until ownership, contracts, and side effects are understood. Inspect direct readers and writers, duplicated representations, lifecycle behavior, compatibility, failure paths, performance-sensitive paths, and analogous implementations that constrain the objective.
3. Inspect tests and operational tooling that establish current behavior. Run read-only checks when they can resolve a material uncertainty.
4. Check any assumptions or directions stated in the request against the evidence. Check for diverging state, multiple clients or machines, stale asynchronous completion, discarded runtime data, payload amplification, and restart or migration failures when applicable.
5. Stay within the objective. Do not expand into adjacent cleanup.

The scout returns only a compact evidence ledger, not a report or recommendation:

- **Observations**: each material fact with a precise location (path and line, symbol, command and its output, or a short quoted excerpt) sufficient to check it with one targeted read.
- **Inferences**: conclusions drawn from observations, each naming the observations it rests on.
- **Contradicted assumptions**: assumptions in the request that the evidence does not support, with the evidence.
- **Open questions**: material unknowns, and the evidence or operator decision that would resolve each.

## 2. Reason over the ledger

Treat the ledger as candidate claims, not verified facts. Do not re-run the exploration. Check that each inference follows from the observations it cites and covers the scope it claims; narrow or drop those that do not.

When the ledger leaves a gap that would materially change the report, ask the scout one narrow follow-up. Do not start a second exploration.

Then draft the report (see *Recon report*). Classify each material finding as one of:

- blocks the objective;
- required migration or compatibility concern;
- constraint or tradeoff;
- accepted temporary limitation;
- possible follow-up;
- unrelated or out of scope.

Where no direction has been proposed, identify constraints that any viable direction must satisfy.

## 3. Challenge the draft

Give the challenger an immutable packet containing the operator's request exactly as written, the established context, the draft report, the scout's ledger, and repository access. Omit the root agent's confidence and any self-assessment.

Instruct the challenger to try to falsify the draft, not improve its prose. It checks consequential claims against the cited evidence and the repository, and looks for missed boundaries, unsupported classifications, directions that violate an observed constraint, and inferences presented as observations. It returns a compact ledger of candidate objections, each with the challenged claim, the evidence inspected, its material effect, and a status of `candidate` or `unresolved`.

The challenger's work is part of recon, not a formal independent review. Do not describe it as independent verification.

## 4. Settle and verify

Perform one falsification pass over the objections: check each against the draft and its evidence, and reject those resting only on speculation, preference, or a merely possible alternative. Where the challenger and root disagree about a consequential claim and one concrete evidence check can settle it, inspect that evidence once or ask the challenger one narrow follow-up. If the disagreement still stands, mark the claim unresolved and stop. Do not create another subagent.

Before replying, personally inspect the cited evidence for the claims that most determine the operator's choice: every finding classified as blocking, every contradicted assumption, and the basis of any recommendation. Label every other material claim as reported by the scout and unverified.

## Recon report

Return:

1. The objective, success conditions, and non-goals.
2. Confirmed architecture and behavior.
3. Incorrect or unsupported assumptions.
4. Findings by classification.
5. Viable directions and their material tradeoffs, without turning them into implementation plans.
6. Decisions or unavailable facts still required from the operator.
7. A recommended next action when the evidence supports one.

Cite paths and symbols for material claims. Mark each material claim as checked by the root agent, reported by the scout and unverified, or inferred, and mark unresolved challenges. State which roles ran as subagents. Do not include the scout's ledger or the challenger's objections unless the operator asks for them.

Stop and wait for the operator to choose the route forward.
