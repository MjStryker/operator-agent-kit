# Core

```text
CHARTERS_DIR: docs/charters
REVIEWS_DIR: docs/charters/reviews
```

Resolve the project root as the nearest enclosing Git worktree root. If there is no Git worktree, use a workspace root explicitly provided by the harness. If neither is unique, ask; never guess among projects.

Resolve `CHARTERS_DIR` relative to that root unless configured as an absolute path or relocated by project policy. Resolve `..` and symlinks. The resulting directory must remain inside the project root unless project policy declares a store outside it; every charter path must then resolve inside that declared store. Scan it as a flat directory for `*.md`; ignore `README.md`, `TEMPLATE.md`, review subdirectories, and files that do not validate against `schema.md`.

Resolve `REVIEWS_DIR` under the same store as `CHARTERS_DIR`. It must remain inside `CHARTERS_DIR`. Review records are auxiliary evidence, not charters; do not include them in charter listing or binding.

Before acting, read applicable project instructions and any existing working-method or charter-convention document they name. Project rules override OAK defaults when they are stricter, merely choose local vocabulary, or declare where charters are stored. Stop on a direct conflict that would weaken an operator-approved boundary such as the lifecycle freeze.

## Binding

For `sync`, `activate`, `resume`, and `close`, bind in this order:

1. Operator-supplied path, confined to `CHARTERS_DIR`.
2. Operator-supplied id matching the filename stem.
3. Unique case-insensitive frontmatter title.
4. Otherwise run `list` and ask.

Never pick by modification time or apparent activity. Apply the schema and storage boundary before binding.

## Write guard

Immediately before changing an existing charter, re-read it. If `updatedAt` changed since binding, discard the pending patch, reconcile against the new record, and re-ask only about affected decisions. Never write from a stale read.

Use ISO-8601 UTC timestamps. Do not create or modify plans, tasks, roadmap entries, reviews, or source files unless the operator separately accepts those changes.
