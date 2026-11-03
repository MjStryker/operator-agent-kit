# Define

Refine-prompt style. Do not perform the underlying request. Both ways of creating a task are this mode. `sync` is only for an **existing** task file.

Resolve and state the task scope using `core.md`. A project task is a shareable repository contract; a personal task may span projects and remains operator-owned. Do not put local harness discussion ids in either task file.

How the operator starts it: name mode `define` (`task define`). If they invoked the skill with no mode and then chose `define`, same path.

## Entry paths

**#1 New discussion** (little or no prior content). Guide the operator. Ask focused questions until the objective, success, and failure are clear enough to lock. Do not dump a blank template and wait. Grow the draft in the conversation after each answer.

**#2 Existing discussion** (content already in this chat, no task file). Convert that chat into the schema: render into the headings, drop implementation chatter. Propose the draft from what was said. Do not invent bars or trade-offs the chat did not make. Then the same gap questions as #1. If the chat mixed several objectives, ask which one this file is for — do not merge them silently.

**Incremental feeding.** The draft grows in the conversation. The disk file is written **once**, after acceptance, to the resolved personal or project store. Do not create a stub and patch it every turn. Exception: if the operator says to save now while gaps remain, write with Open questions listing what is still unlocked; `status` stays `open`.

## Shared steps

1. Use what the operator already said. Do not ask for facts the context contains.
2. Check only material gaps: intended outcome; success and failure; constraints / non-goals; omitted concerns that could prevent the outcome. Ask focused questions. Do not force a checklist. Do not silently widen scope. Surface omitted concerns as questions with the concrete reason. Record **only** factual premises that materially affect the objective, constraints, or criteria. If none are needed, do not ask for epistemic metadata.
3. Do not choose the objective, priority, baseline, trade-off, or success/failure bar. Wait. Continue across turns. Keep showing the updated draft.
4. Target: **new file** unless the operator explicitly names an existing active `id` and confirms re-lock. A new id must be absent from both the active and archived directories; archived ids are never reused or re-locked. Re-lock rewrites Objective / Success / Failure / Constraints; ask before wiping Sub-steps, Premises, Key decisions, or Open questions. Preserve any legacy `## Sessions` section unchanged. Keep `id`, `scope`, and `createdAt`; bump `updatedAt`. Apply the write guard in `core.md`.
5. Show the full proposed record, including `scope`. Write only after the operator accepts (or edits), except the “save now” exception. New files start `status: open` and omit `## Sessions`. After a successful write, add the local discussion binding when available (see `core.md`).
6. Stop, unless the same message also asked to start the work.
