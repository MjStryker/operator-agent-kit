---
name: oak
description: Guide the operator to the smallest suitable OAK capability based on the current project and available skills. Use only when explicitly invoked.
license: MIT
metadata:
  author: MjStryker
  category: workflow
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.1"
disable-model-invocation: true
---

# OAK

Guide the operator toward the smallest useful next step in OAK. Do not perform the underlying work or invoke another skill.

Use the current project and available installed skills as needed. Do not rely on a fixed catalog or assume every OAK capability is installed.

Recommend one next skill and its mode when established, or ordinary agent work when no skill adds value. Briefly explain why it fits and what it will not do. If a longer route may help, keep it optional and make the immediate next invocation clear.

Ask only when missing context would materially change the recommendation. If no objective was supplied, ask what the operator wants to accomplish. Then stop and let the operator choose.
