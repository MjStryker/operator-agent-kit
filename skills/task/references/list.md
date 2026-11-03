# List

Read frontmatter from eligible tasks in the personal store and current project store using the boundaries and validation rules in `core.md` and `schema.md`.

Selectors may be combined when unambiguous:

- scope: `personal` or `project` (default: both);
- visibility: `active`, `archived`, or `all` (default: `active`).

`active` means nonterminal tasks (`open` or `paused`) in the store root. A terminal task left in the root is pending archival: hide it from the default view but include it in `list all` with location `active (terminal)`. `archived` means terminal tasks in the store's direct `archived/` child. `all` includes both locations and every valid status.

Treat a pre-0.4 task with no `scope` field as `personal`. Skip invalid files. Do not read task bodies, assess premises, or inspect local discussion bindings.

Sort by `updatedAt` descending. For the default active view, show:

| scope | id | title | status | updatedAt | createdAt |
|---|---|---|---|---|---|

For `archived` or `all`, add a final `location` column with `active`, `active (terminal)`, or `archived`.

Use scoped locators when the same id exists in both stores. If the selected view is empty, say so. Offer `task define personal` or `task define project` only when there are no active tasks and the operator did not specifically request archived tasks.

`list` shows no relationships; point at `task status` when the operator needs the tree, dependencies, or progress.

Never write.
