# Status

Show where a task sits in its tree, what each related task's recorded status is, and what can start next. Read-only: never write a task, the bindings file, or anything else.

## Entry

Bind a task using `core.md`, except that a failed binding is not an error: with no uniquely bound task, show every active root task (a task with no `Parent`) in the eligible stores and stop.

From the bound task, follow `Parent` upward to the root. Stop and signal a missing, invalid, or cyclic parent instead of guessing.

## Read

For the root and each descendant, read only the header and the `## Sub-steps` and `## Relationships` sections. Descendants are the ids referenced in a parent's `## Sub-steps` plus any task in the same stores whose `Parent` names it. Resolve ids with the locator and archive rules in `core.md` and `schema.md`. Do not read other body sections, assess premises, or inspect repositories, branches, or merge requests.

## Show

A tree in a code block, one task per line: status, id, title. Mark the bound task with `← you are here`. Under a task that declares `DependsOn`, list each target with its recorded status.

```text
open   checkout-redesign — Checkout redesign ready to ship        1/4 done
├─ done   payment-form — Payment form matches the mockup          ← you are here
├─ open   error-message — Reusable error message component
├─ open   order-summary — Order summary shows every order state
│         depends on: payment-form (done), error-message (open)
└─ open   receipt-email — Receipt email sent on success
```

Then, briefly:

- **Progress:** for each parent, done children out of non-abandoned children, plus the number of paused children when there are any (for example `1/4 done, 1 paused`). Paused children count as not done. Say that this counts recorded status only; it does not measure implementation, and child success does not prove parent success.
- **Ready now:** open tasks with no `DependsOn`, or whose `DependsOn` targets are all `done`.
- **Can build on open work:** open tasks whose remaining `DependsOn` targets are `open` and whose dependency lines do not require a merge or `done`. Per `schema.md`, they may start once the target's result is available to build on; `status` does not check whether it is.
- **Blocked:** open tasks with a `DependsOn` target that is `paused`, or that is `open` while the dependency line requires a merge or `done`. Name the blocking target.
- **Paused:** paused tasks in the tree, listed once. They are neither ready nor blocked.
- **Inconsistencies:** sub-step ids without a file, children whose `Parent` is not listed in the parent's `## Sub-steps`, missing or cyclic relationships, a `DependsOn` target that is `abandoned`, a `done` parent with open or paused children, a binding that points at an archived task. Report; do not repair.
- **Next:** at most two operator commands, labeled read-only or writes, for example `task resume {id}` (read-only) or `task sync` to record a child as done (writes after confirmation).

Do not infer status from the conversation, the repository, or elapsed time. A task is done only when its file says `done`.
