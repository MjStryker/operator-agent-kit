# Core

```text
PERSONAL_TASKS_DIR: $HOME/tasks
PROJECT_TASKS_DIR: docs/tasks
BINDINGS_FILE: $HOME/tasks/.bindings.md
HARNESS:
```

`PERSONAL_TASKS_DIR` contains operator-owned tasks that may span or outlive projects. Resolve `$HOME`; do not hardcode a username.

`PROJECT_TASKS_DIR` is relative to the current project root unless configured as an absolute path. Resolve the project root as the nearest enclosing Git worktree root, or a unique workspace root explicitly supplied by the harness when no Git worktree exists. Project task storage must remain inside that root unless project policy declares a store outside it; every project task path must then resolve inside that declared store.

Each store has an `archived/` child directory: `PERSONAL_TASKS_DIR/archived` and `PROJECT_TASKS_DIR/archived`. It is a terminal record store, not a third scope. Do not create it until an accepted archive operation needs it.

`BINDINGS_FILE` is local routing state. It maps harness discussions to exact task paths and is never part of a project task contract. Its parent must resolve inside `PERSONAL_TASKS_DIR`.

`HARNESS` is an optional open lowercase token `[a-z0-9-]+`. If empty, use the harness name stated in system context, lowercased and hyphenated. Do not infer it from the model name.

Timestamps are ISO-8601 UTC. Status vocabulary is in `schema.md`.

## Scope

New tasks have one explicit scope:

- `personal`: stored in `PERSONAL_TASKS_DIR`;
- `project`: stored in the current project's `PROJECT_TASKS_DIR` and suitable for repository sharing.

`task define personal` and `task define project` select it explicitly. Without a qualifier, use `project` only when the operator explicitly asked for a shared/project task or the task contributes to a named charter; otherwise preserve the historical `personal` default. State the selected scope in the proposal.

Charter-derived tasks are project-scoped by default. Child tasks inherit the parent scope.

## Storage boundary

Resolve candidate paths, including `..` and symlinks. Active tasks are `*.md` files whose resolved parent is exactly the resolved personal or current-project task directory. Archived tasks are `*.md` files whose resolved parent is exactly that store's resolved `archived/` directory and whose status is `done` or `abandoned`. Scan both locations as flat directories; do not recurse. Ignore the bindings file and files with invalid naming or frontmatter.

Normal mode binding (`decompose`, `sync`, `resume`, `status`, and `archive`) selects active tasks only. Archived tasks are immutable through the task skill and never become the current discussion binding. A relationship read may resolve an archived terminal task when its active-store id is absent. `list archived` and `list all` may read archived frontmatter as defined in `list.md`.

For a task path obtained from the local binding registry, accept a personal task only when its parent is exactly `PERSONAL_TASKS_DIR`, and accept a project task only when its parent is exactly that project's `PROJECT_TASKS_DIR`. If it instead names a valid archived task, report that the binding is stale and offer to remove or replace it; do not resume the archived task or fall back silently. Stop on missing, invalid, nested, or escaped paths.

## Task locators

Use `personal:{id}` and `project:{id}` when a bare id could be ambiguous. A bare id searches the current project store and personal store; if both match, ask. Titles must match uniquely across the same search set.

Binding for `decompose`, `sync`, `resume`, `status`, and `archive` uses the first unique match:

1. Operator-supplied path passing the storage boundary.
2. Operator-supplied scoped locator.
3. Operator-supplied bare id.
4. Unique case-insensitive title.
5. Current `HARNESS` + discussion id in `BINDINGS_FILE`.
6. Legacy `## Sessions` lookup for pre-0.4 task files.
7. Otherwise run `list` and ask.

Never pick by newest modification time. The bound file is source of truth.

## Local discussion bindings

By default, automatically bind through the harness's stable top-level discussion, thread, or chat identifier. Resolve that canonical identifier from harness-provided system or app context, environment, or API; for example, Codex exposes `CODEX_THREAD_ID`. These are discovery sources for the same identity, not alternate binding strategies.

The identifier must remain stable across turns and resumptions of the same discussion. Never use or store a run, turn, request, process, tool-call, or child/subagent identifier. Never infer identity from newest modification time or invent an identifier.

The bindings file is local and has this body:

```markdown
# Task bindings

- codex `discussion-id` — `/absolute/path/to/task.md` — 2026-09-19T10:00:00Z
```

The tuple `(harness, discussion-id)` may point to only one task. On every successful `define`, `decompose`, `resume`, or `sync`, automatically resolve the stable harness discussion identity and add the tuple when absent. This is the default routing behavior, not an optional fallback. If it points elsewhere, ask whether to move it, keep the existing binding and abort, or allow replacement; never create multiple active mappings. Re-read the bindings file immediately before writing it.

Binding metadata does not modify the task or its `updatedAt`. If automatic resolution yields no candidate or several candidates, the identity is unavailable: skip the binding, say so, and offer the exceptional manual fallback. The operator may supply `harness` + id; a bare id uses the configured harness.

Legacy task `## Sessions` entries remain valid for lookup but are not appended, migrated, or removed implicitly.

## Write guard

Sibling discussions may share a task. Immediately before changing a task, re-read it. If `updatedAt` differs from the value read at bind time, discard the pending patch, re-run classification, and re-ask only for affected items. Never write from a stale read.

## Common rules

- Do not execute underlying work unless the operator also asks to continue it.
- Do not treat a task as a plan, todo list, implementation tracker, charter, or knowledge base.
- State relationships and dependencies only as the files record them. If one seems missing or wrong, say so and point at `sync`; do not assert it as established.
- Do not delete task files or legacy Sessions entries.
- Do not store derived epistemic labels in the file.
- No mode sets the `status` field directly. `define` sets `open`; `sync` may propose a status change as a conflict requiring operator acceptance; the `status` mode only displays it.
