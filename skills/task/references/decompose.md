# decompose

Turn one bound task objective into a minimal set of independently verifiable child objectives. This is operator-triggered only. Do not score task complexity, auto-invoke this mode, or recursively decompose children.

`decompose` creates objective contracts, not an implementation checklist. Do not perform the underlying work unless the same operator message also asks to continue after the files are accepted.

## Entry

The operator names mode `decompose` and may identify the parent by path, id, or title. Bind it using `core.md`. If no task binds uniquely, run `list` and ask.

Read the parent Objective, Sub-steps, Success, Failure, Constraints and non-goals, Premises, Key decisions, Open questions, and Relationships when present.

If the parent objective or its success/failure bars do not establish what the child objectives must contribute to, ask focused questions before proposing files. Do not choose those bars for the operator.

## Propose one level

Propose only child objectives that make part of the parent outcome separately executable and verifiable. There is no required number of children.

A proposed child is ready when it has:

- one coherent outcome;
- its own observable Success and Failure;
- an identifiable verification method or evidence;
- enough constraints and context to execute without an implicit material decision;
- an explicit contribution to the parent objective.

For a user-visible change, the child's Success names what it must look like: a mockup, an existing component to match, or the specific properties that must match (for example color, opacity, typography, motion). "Uses the X style" alone leaves an implicit decision; ask the operator which properties matter. State visual treatments the child must not add when a sibling owns them.

The default is one task and a plan. Split further only when doing so would reduce a concrete ambiguity, isolate a risk or dependency, or make failure independently diagnosable. Do not split merely by file, module, architectural layer, estimated size, or generic phases such as “analyse / implement / test.” Do not aim for the smallest possible action. Do not propose a child whose only observable result is a container or scaffold that a sibling fills; fold it into that sibling.

Children are objectives, not merge requests. Do not assign a child to its own merge request or make one child wait for another's merge unless the operator requires it. If delivery grouping matters, mention it once as a suggestion for the plan; do not write it into task files.

If the parent already forms one coherent, independently verifiable unit and further splitting would only create procedural steps, say so and propose no files.

For every proposed child, show a complete task record conforming to `schema.md`, plus:

```markdown
## Relationships
- Charter: `docs/charters/charter-id.md`
- Parent: `parent-task-id`
- DependsOn: `sibling-task-id` — result this child builds on
- Uses: `parent-task-id#P1`, `parent-task-id#D2`
```

Include only applicable relationship lines. Children inherit the parent's scope and Charter relationship. Reference parent-owned premises and decisions with `Uses`; do not copy their definitions. Put a dependency on its consumer. Dependency relations among proposed children must be acyclic.

Before the full records, show the proposal as a tree in the shape `status.md` uses: each proposed child, its `DependsOn` targets, and which children can start immediately. Say explicitly which children are independent of each other. This picture and the records must agree.

Show the proposed parent `## Sub-steps` patch. Preserve unrelated existing sub-steps. Do not repeat child objectives, criteria, or status in the parent; reference each accepted child id with a short statement of its contribution.

Wait for the operator to accept or edit the complete proposal. Do not write drafts incrementally.

## Write

Before writing:

1. Validate every proposed id and confirm none collides with an active or archived task.
2. Validate every relationship target against an existing task or an accepted child in this batch, and reject cycles.
3. Re-read the parent and apply the write guard from `core.md`.

After acceptance, create the child files with the parent's `scope`, `status: open`, and the same `createdAt` and `updatedAt` write timestamp. Then patch only the parent's accepted `## Sub-steps` and bump the parent's `updatedAt`. Add or confirm the parent discussion binding in the local bindings file; child files remain unbound until a discussion resumes them.

Create children before adding their parent references. If any write fails, stop and report exactly which files exist and which parent references were or were not written. Do not claim the decomposition was completed and do not retry blindly.

Child success does not prove parent success. Keep the parent's Success and Failure unchanged; they remain the final integration contract.

Stop after the files are written unless the same operator message also asked to continue the underlying work. A child may be decomposed later only through a new explicit `task decompose <child-id>` invocation.
