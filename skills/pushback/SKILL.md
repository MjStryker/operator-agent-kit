---
name: pushback
description: Challenge an agent response for unsupported claims, missing consequential work, scope errors, or overstated verification. Use only when the user explicitly invokes pushback.
license: MIT
metadata:
  author: MjStryker
  category: review
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.4"
disable-model-invocation: true
---

# Pushback

Critically examine the target response without opposing it for the sake of disagreement. The operator may invoke pushback at any time. By default, examine the agent's most recent substantive response. If the operator supplies another response, document, or focus, use that target instead. Treat unfinished work as an interim snapshot: challenge claims already made, but do not call work missing merely because it is still in progress.

Review only. Do not execute the underlying task or modify project files unless the user explicitly asks after the assessment. Read-only inspection needed to assess the response is allowed within the existing authorization.

## Review process

Use one fresh subagent or isolated context when available and authorized. Give it an immutable review packet containing:

- the operator's request and material constraints;
- the exact response or artifact being challenged;
- relevant existing evidence and repository access;
- this review-only boundary.

First inspect the available collaboration capabilities. A wait or polling capability alone does not mean that subagents are available. When an explicit create or spawn capability exists, delegation is required: create exactly one reviewer before analyzing the target, announcing independent review, or waiting. Never call a wait or polling tool unless that creation call succeeded and returned a live reviewer identifier. If no create or spawn capability exists, skip delegation and perform discovery and falsification once in the current context; do not simulate or announce independent review.

Keep the original target fixed throughout the review. The reviewer produces a compact candidate ledger containing the challenged claim, claim type, evidence inspected, material effect, confidence, and status (`candidate` or `unresolved`). It does not produce the operator-facing answer.

After receiving the ledger, the root agent performs one falsification pass: check every candidate against the original target and evidence, narrow overbroad conclusions, and reject findings based only on speculation, preference, or a merely possible alternative. Do not defer this judgment to the reviewer or copy its response directly.

A third and final pass is allowed only when reviewer and root reach different conclusions about a consequential finding and a concrete evidence check or contradiction can resolve the difference. Ask the same reviewer one narrow follow-up or inspect that evidence once. If the disagreement cannot be resolved from available evidence, mark it unresolved and stop. Do not spawn another reviewer.

Stop after root falsification when there is no such material disagreement. Rephrasing, confidence adjustments without new evidence, unsupported alternative explanations, and stylistic objections do not justify another pass. A pass is a completed review of the target or ledger, not a wait, poll, tool call, or restatement.

Return one consolidated assessment. Do not expose intermediate debate or include rejected, duplicate, stylistic, or otherwise non-material ledger entries.

Focus on claims or omissions that could materially affect the user’s understanding, decision, or belief that the task is complete. Check whether the response addressed the requested outcome and important constraints as well as whether its stated conclusions are supported.

For an interim response, unfinished work is not an omission, but observations already asserted still require support when they materially affect the direction of the work.

Distinguish facts, deductions, proposals, opinions, and unresolved uncertainty. Do not demand evidence for preferences or proposals, but ensure they are not presented as established facts.

For each consequential claim, determine:

- what evidence supports it and whether that evidence was actually inspected;
- whether the evidence covers the full scope of the claim;
- what remains assumed, inferred, or unverified;
- what observation could contradict the conclusion.

Inspect accessible source code, documentation, or tool behavior when it can resolve the question. Before retaining a claim that evidence is absent, locate and read relevant existing records in the authorized context; an uninspected record is not an absent record. Give the reviewer access to those records, and check any evidence-absence candidate during root falsification. If no record is found, state what was checked and distinguish a reported result from an inspected record rather than implying the event did not occur. Do not rerun the underlying task to replace this read-only check.

Repository evidence that a code path exists does not establish that it caused a runtime event. An earlier live observation is not current state unless its freshness was checked. Treat an operator report as evidence while distinguishing it from an agent-observed result. Rank supported explanations instead of giving every logically possible alternative equal weight.

Interpret evidence according to the capability that produced it. A successful check proves only the properties that check covers. Terms such as `valid`, `passed`, `verified`, and `successful` do not establish broader correctness. If the check’s scope is unclear, inspect its documentation or implementation when available.

Match verification to the claim type. Use source or diff evidence for structural claims and runtime evidence for behavioral claims. Do not propose runtime execution to establish structural additivity or repository scope, and do not treat missing runtime tests as consequential when the target claims only repository or staging state.

Do not rerun a product scenario, stateful end-to-end flow, deployment, or the underlying task merely to manufacture evidence for the review. When re-execution is the only way to resolve a claim, name the smallest exact check as follow-up work. Do not perform it during pushback unless the operator explicitly asks for it after the assessment.

Use the project’s epistemic vocabulary when one exists. Do not call a self-review independent verification. If no material issue survives examination, state what was checked and the remaining limits rather than declaring the whole response validated.

If the operator combines pushback with another question, the operator-facing response must use two separate sections: `Pushback assessment`, containing findings without advice, followed by `Requested follow-up`, containing the answer to the additional request. Do not put proposals or “I would” statements in the assessment. Label recommendations as proposals and do not implement them unless explicitly requested.

If review is interrupted, resume from evidence already inspected when possible. Never leave a planning sentence as the apparent result. If completion is impossible, state that the assessment is incomplete and identify what remains unchecked.

Present meaningful findings with their evidence, correct unsupported or overstated conclusions, identify consequential omissions, and name the smallest verification needed for unresolved claims. Adapt the response to the findings instead of forcing a report template. Use the operator's language unless quoted evidence or established project terminology requires otherwise.
