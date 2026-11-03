# resume

Task lookup, local discussion binding, and the write guard are in `core.md`. Schema and premise derivation are in `schema.md`.

1. Bind the file. If none: `list` and ask.
2. Read the file. Restate it as the working objective and constraints: scope, Objective, Sub-steps, Success, Failure, Constraints, Key decisions still in force, Open questions. Compact prose, not a dump of empty sections. Do not invent a work-in-progress position or expose local binding ids unless the operator needs routing diagnostics.
   - If `## Relationships` exists, resolve its direct Charter, Parent, DependsOn, and Uses references under the storage and locator rules in `core.md`. Load only the referenced charter objective, task objective, required result, premises, or decisions needed to understand this task; do not recursively load an entire relationship tree.
   - Signal missing, invalid, or cyclic references. Do not repair them during `resume`.
   - When the task has a `Parent`, add one line locating it: the parent id and the recorded status of each `DependsOn` target. Point at `task status` for the full tree.
3. Recompute support and validity for each Premise from the clock, revisions, and recorded conditions. **Signal first** premises that are `stale`, `expired`, `contested`, `refuted`, or `unbounded` while time-sensitive, plus any whose validity is unchecked. Do not recite every label when all premises are coherent (`corroborated`/`uncorroborated` + `current`/`unbounded` with no sensitivity). Do not write derived labels into the file.
4. Add or confirm this discussion's local binding when the stable harness id is available. Do not modify the task or its `updatedAt` for binding metadata.
5. Treat the file as source of truth for the rest of the session unless the operator changes it through `define` / `decompose` / `sync`. While working on the task, check each requested change against its Constraints and non-goals and against sibling objectives before acting; when a change belongs to a non-goal or to a sibling, say so and ask.
6. Do not “update from memory.” If the chat disagrees, say so and point at `sync`; do not overwrite objective sections while resuming.
7. End the restatement with one line: `resume` did not change the task file (it only records this discussion's local binding); `list` and `status` only read; `define`, `decompose`, `sync`, and `archive` write, each after operator confirmation.

Stop after restatement unless the same operator message also asked to continue the work.
