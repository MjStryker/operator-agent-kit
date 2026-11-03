---
name: task
description: >-
  Create, decompose, update, resume, list, show status of, or archive durable personal or project task
  objectives. Use only when the operator explicitly invokes this skill with a
  mode (define, decompose, sync, resume, list, status, archive). Do not auto-invoke from ambient
  coding work.
license: MIT
metadata:
  author: MjStryker
  category: task-management
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.11"
disable-model-invocation: true
---

# Task

Operator-triggered only. One public skill with named modes. A task file is the source of truth for an objective and its decisions — not a plan, implementation log, charter, or general knowledge base.

Do not infer this skill from ambient work. Do not infer the mode. Do not choose the objective, success bar, failure bar, or trade-offs. Do not execute the underlying work unless the same operator message also asks to continue that work.

## Mode

The operator names the mode: `define` | `decompose` | `sync` | `resume` | `list` | `status` | `archive`.

```text
task define
task define project
task decompose
task sync
task resume
task list
task status
task archive
```

Prefix with the harness's skill invocation syntax. `define` accepts an optional `personal` or `project` scope. Existing modes may use a `personal:{id}` or `project:{id}` locator when the scope is otherwise ambiguous.

If invoked with no mode, propose the available modes (one line each: when to use) and wait. Do not pick.

| Mode | When to use | Writes |
|---|---|---|
| `define` | Lock a new task file (new chat or extract from this chat). | yes, after confirmation |
| `decompose` | Propose and create independently verifiable child objectives for a named task. | yes, after confirmation |
| `sync` | Pull durable facts/decisions from this chat into an existing file. | yes, after confirmation |
| `resume` | Reload a file as the working objective and constraints. | no (local binding only) |
| `list` | Show active tasks by default; optionally show archived tasks or all tasks. | no |
| `status` | Show the task tree, dependencies, progress, and what can start next. | no |
| `archive` | Move a terminal task out of the active store without changing its contract. | yes, after confirmation |

After the mode is known, read [references/core.md](references/core.md), [references/schema.md](references/schema.md), and only the matching mode file:

- [references/define.md](references/define.md)
- [references/decompose.md](references/decompose.md)
- [references/sync.md](references/sync.md)
- [references/resume.md](references/resume.md)
- [references/list.md](references/list.md)
- [references/status.md](references/status.md)
- [references/archive.md](references/archive.md)

## Invariants

- File is source of truth. Conversation memory is not.
- Premises are a cross-cutting rule in `schema.md`, not an additional mode. Support and validity are derived at read time; never store `current` or `corroborated`.
- `updatedAt` is last file write, not claim validity.
- Task contracts never store harness discussion ids. Local bindings live outside shareable task files.
- Terminal tasks may be moved to the store's `archived/` directory; archived contracts are retained and read-only.
- Do not ship independent skills for the modes or alias skills (invoking `task` with a mode already passes the mode).
