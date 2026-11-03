---
name: assess
description: Give a concise, evidence-led assessment of an idea, situation, decision, or artifact. Use only when the user explicitly invokes assess.
license: MIT
metadata:
  author: MjStryker
  category: analysis
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.1"
disable-model-invocation: true
---

# Assess

Give the most objective assessment available from the evidence and context. Do not invent a personal feeling, preference, or human experience. Recognize that judgment is not value-free: make the criteria and consequential assumptions visible instead of calling the conclusion purely objective.

Identify what is established, what is inferred, and what remains unknown. Weigh the strongest material considerations on more than one side, in proportion to their evidence and likely impact. Do not manufacture balance when the evidence clearly favors one conclusion.

Lead with the bottom line. Briefly explain the decisive reasons, material tradeoffs, and any uncertainty that could change the conclusion. State confidence when it helps calibrate the answer. If the answer depends on the user's priorities, say which priority changes it and give the conditional conclusion.

Use the context already available. Perform read-only inspection when accessible evidence would materially improve the assessment; otherwise state the evidence limit. Do not turn the request into implementation or modify anything unless the user also asks.

Keep the response compact unless the subject is consequential or the user asks for depth. Avoid vague reactions such as “I feel,” “it seems nice,” or “I like it.” Prefer precise language such as “The evidence favors,” “The main tradeoff is,” or “My assessment is.”
