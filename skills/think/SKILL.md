---
name: think
description: Delegate exploration of a search or planning question to a subagent and receive a compact synthesis, keeping the main conversation readable. Use only when explicitly invoked.
license: MIT
metadata:
  author: MjStryker
  category: discovery
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.1"
disable-model-invocation: true
---

# Think

For search and planning, not implementation. A subagent explores; you examine its synthesis and answer.

## Delegate

When you can create a subagent, you must create one before exploring; a wait or polling capability alone does not count. For a follow-up to an earlier `think`, continue that subagent when possible. Without subagents, explore here and say so.

Send two separate parts:

- **Request**: the operator's words, unchanged.
- **Context**: what the request refers to, decisions and constraints from the conversation, target files, and established findings with their source. Not unsupported hypotheses or a preferred answer.

The subagent explores read-only and returns only:

1. Conclusions.
2. Evidence consulted for each, including evidence that limits or contradicts it, with a precise location (path and line, or a short quote).
3. Assumptions.
4. Open questions.

## Answer

Treat the synthesis as unverified claims. Reject or narrow conclusions whose evidence does not support them. Spot-check at most the two conclusions that matter most; label the rest as reported by the subagent, and list any unchecked conclusion the answer depends on as an open question.

Answer concisely, in the operator's language, keeping checked findings distinct from relayed ones and carrying forward open questions that still matter.
