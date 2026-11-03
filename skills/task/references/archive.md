# Archive

Move a terminal task contract out of the active store while preserving it byte-for-byte. Archiving changes visibility and location, not task status or content.

Bind an active task using `core.md`. Only `done` and `abandoned` tasks may be archived. If the task is `open` or `paused`, stop and direct the operator to make any intended status decision through `task sync`; do not combine a status transition with archival.

The target is the same filename in the scope's direct `archived/` child directory. Before proposing the move:

1. Resolve the source and target under the storage boundaries in `core.md`; reject symlinked, nested, or escaped paths.
2. Stop if the target already exists or if any other active or archived file has the same id.
3. For a project task, search repository-owned files for direct path references to the source. Report any reference whose target would break and stop until the owning artifact is updated. Id-based task relationships remain valid because relationship lookup includes archived tasks.
4. Read the local bindings file when available and identify every entry whose exact target is the source. Those entries become stale after the move and are part of the archive proposal.

Show one complete proposal containing:

- source and target paths;
- the task's terminal status;
- confirmation that task bytes and `updatedAt` will not change;
- bindings that will be removed;
- whether the project move will use `git mv` (tracked source) or a filesystem rename (untracked source).

Wait for explicit acceptance. Immediately before writing, re-read the task and verify both its `updatedAt` and complete-file SHA-256 still match the proposal. Re-read the bindings file and recompute affected entries. If either changed, discard the proposal and reconcile before asking again.

After acceptance:

1. Create the direct `archived/` directory if absent.
2. Move a tracked project task with `git mv`; otherwise use one same-filesystem rename. Never copy-and-delete.
3. Verify the source is absent, the target is a valid terminal task, and its complete-file SHA-256 is unchanged.
4. Remove only local binding entries whose exact target was the source. Preserve all other lines and the binding header. If no entries remain, keep the valid header-only registry.

Report the archived locator and removed bindings. Do not bind the current discussion to the archived path. Do not change the task body, frontmatter, `updatedAt`, relationships, or referencing artifacts during archive mode.
