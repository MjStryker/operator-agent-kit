---
name: refine-prompt
description: Refine a draft request into a clear, self-contained prompt while preserving the user’s intent and surfacing only material decisions. Use only when the user explicitly invokes refine-prompt before execution.
license: MIT
metadata:
  author: MjStryker
  category: prompting
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.1"
disable-model-invocation: true
---

# Refine a prompt

Help the user turn a draft request into a well-understood request. Do not execute the underlying request.

Respond and write the refined prompt in the user’s language unless they request another language. Keep it independent of a particular model, provider, IDE, agent harness, tool, or invocation syntax unless the task requires one.

Preserve the user’s intent. Treat a proposed solution as a proposal rather than automatically treating it as the underlying objective. Do not add adjacent scope silently. When an omitted concern could prevent the outcome, explain the concrete consequence and determine whether it is required, excluded, deferred, or unresolved.

Establish only the information that can materially change the request or how its result will be assessed, such as:

- the intended outcome and current problem;
- important requirements, non-goals, constraints, and tradeoffs;
- decisions or facts still missing;
- observable signs of success and meaningful failure.

Do not force every request through this list or label it by complexity. Pay particular attention to directional terms such as `improve`, `optimize`, `simplify`, `strengthen`, or `make more effective`; determine the intended dimension when different interpretations would produce materially different work.

Handle missing information according to its kind:

- Ask the user for a decision only when it changes the objective, priority, baseline, observable behavior, scope, risk, or another material tradeoff.
- Resolve facts from available conversation or read-only project evidence before asking for information already accessible.
- State a narrow assumption when its impact is low and making it will not redirect the task.
- Keep an uncertainty explicit when useful refinement can proceed without resolving it.

Use context already provided. Consult external sources only when a specific fact is required for a useful prompt and doing so fits the user’s request and existing authorization.

Once no material user decision blocks the request, return a self-contained refined prompt. Adapt its form to the task instead of imposing a template. If the original prompt is already sufficiently defined, say so and change only what provides a concrete benefit.

The user decides whether to accept, edit, or execute the refined prompt. Never execute it automatically.
