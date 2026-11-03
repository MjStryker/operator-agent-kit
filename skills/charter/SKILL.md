---
name: charter
description: Define, update, activate, resume, close, or list shared, project-owned capability charters. Use explicitly when a project commitment needs durable scope, decisions, acceptance criteria, and an outcome record beyond an individual task.
license: MIT
metadata:
  author: MjStryker
  category: project-management
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.6"
disable-model-invocation: true
---

# Charter

Operator-triggered only. A charter is the shared, project-owned contract for a project capability: why it matters, what is committed, what is excluded, which decisions govern it, and what evidence will establish its outcome.

A charter is not required for ordinary tasks. Do not turn implementation steps into charters, write an implementation plan, create downstream tasks silently, or perform the underlying work unless the operator also asks to continue it.

## Mode

The operator names the mode: `define` | `sync` | `activate` | `resume` | `close` | `list`.

```text
charter define
charter sync
charter activate
charter resume
charter close
charter list
```

If invoked without a mode, describe the modes briefly and wait. Do not choose one.

After the mode is known, read [references/core.md](references/core.md), [references/schema.md](references/schema.md), and only the matching mode file:

- [references/define.md](references/define.md)
- [references/sync.md](references/sync.md)
- [references/activate.md](references/activate.md)
- [references/resume.md](references/resume.md)
- [references/close.md](references/close.md)
- [references/list.md](references/list.md)

## Invariants

- Charters are shared project records. Their store is project policy; the repository is the default.
- A charter owns a capability commitment; tasks own independently verifiable objectives; plans own execution steps.
- Project policy may strengthen or adapt review, naming, lifecycle, concurrency, and storage rules. Do not invent missing policy or weaken existing policy.
- Draft and active charters may change only through explicit operator decisions. Complete and abandoned charters are frozen.
- Completing tasks or plan steps does not prove a charter outcome; close against its definition of done.
- Persist task references, not duplicated task contracts or implementation logs.
