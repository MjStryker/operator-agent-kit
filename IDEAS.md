# Possible OAK features and improvements

This is an idea list, not an implementation plan. OAK's current focus remains
the small set of independent skills described in the [README](README.md).
Frameworks and a harness are possible later directions. Each candidate below
needs a real use case and a check that it improves the work before it becomes
part of OAK.

## Skills and reusable practices

| Candidate | What it could improve |
|---|---|
| **Context reconstruction** | Find relevant earlier discussions and artifacts, record which sources were read, cite consequential decisions, and surface conflicts or missing context before summarizing an objective. This addresses the failure mode where a durable task file starts from an inaccurate account. Inspired by Pstack's `recall`. |
| **Evidence-first verification** | Require proof suited to the claim: a real user path, observable state, test result, trace, screenshot, or other inspectable artifact. Keep unverified claims explicit. Apply this to existing review and fix skills before considering another generic skill. Inspired by Pstack's verification practices. |
| **Project-local control tools** | Help a project provide a small, repeatable way to launch, drive, observe, and clean up its own app. Keep application-specific commands and feature maps in that project. Inspired by Pstack's verification skill and feature maps. |
| **Learning from real runs** | Inspect recurring failures and friction, then improve an existing skill, script, or test only when the lesson is reusable. Evaluate changes against actual cases. Inspired by Pstack's `reflect` and its practice of turning repeated failures into tools. |
| **Skill curation** | Check whether each OAK skill is used, solves a distinct problem, and remains useful on its own. Revise, absorb, or retire skills that do not earn their maintenance cost. `task` and `discover-complex-work` are candidates for this assessment; no disposition is decided. |

## Possible local planning process

| Candidate | What it could improve |
|---|---|
| **Outcome map** | Keep one bounded destination visible across sessions, together with scope, decisions, open questions, and links to plans. Avoid losing the bigger picture when implementation is split into several plans. Inspired by Wayfinder's map. |
| **Fog and frontier** | Record in-scope matters that are still too vague to ask precisely. Turn them into question nodes as they become clear. Show which open, unblocked question can be worked next. Inspired by Wayfinder's fog and frontier. |
| **Question sessions** | Work one question at a time and preserve a short record of sources, answer, remaining uncertainty, and follow-up nodes. Allow another session when the first cannot settle it. A node represents a question or outcome; sessions are attempts to resolve it. |
| **Different routes through uncertainty** | Send a question to discussion, repository investigation, external research, or a small prototype according to what would resolve it. An agent can establish facts; product and preference decisions remain with the human. Inspired by Wayfinder's ticket types. |
| **Visual map** | Render the current route as a readable graph with dependencies and progress. Generate or validate it from the same local records used for work so the picture does not drift from the underlying state. Start with a simple Markdown rendering before considering dedicated UI. |
| **Plan handoff and revision** | Turn settled decisions into the existing local draft plans. Define how new evidence amends an active plan or creates a successor while preserving the original basis and review history. Keep map and session files separate from plan filenames that authorize implementation. |
| **Decision and evidence trail** | Record consequential choices, pivots, and verification results with links to their sources. Prefer a compact append-only record to a transcript dump. Inspired by Pstack's `show-me-your-work`. |
| **Outcome validation** | Compare delivered work with the destination and plan definitions of done. Show what was proven, what remains open, and where unfinished work moved. Closing every map node alone should not imply that the outcome was achieved. |

## Possible tooling after a process proves useful

| Candidate | What it could improve |
|---|---|
| **Local map checks** | Detect broken links, missing source records, dependency cycles, stale status, and inconsistent completion claims; compute the frontier from the records. Use scripts for repeatable checks that prose instructions handle poorly. |
| **Single process entry point** | Open or resume a map, present its current frontier, and route to relevant independent skills. A trigger such as `pathfinder` is one possible interface, not a chosen OAK skill. Pstack's `poteto-mode` demonstrates this routing pattern. |
| **Harness support** | If local files and scripts prove insufficient, provide a way to view or run the process across agent tools. Its role and design are still undefined. |

## OAK assistant

A candidate that would combine several entries above: an assistant specialized
in reasoning and in managing objectives and plans. It keeps the records and
their state; the operator keeps the decisions and chooses when to call the
independent skills (`recon`, `assess`, `pushback`, the review skills).

It comes from a real run of `task` 0.4 on a multi-part UI feature. Defining the
objective worked well. Working the children did not: there was no status view,
the agent asserted a dependency the files did not record, a finished child was
held until its merge request merged, the split was too granular, and the
operator could not see where the current child sat in the whole. `task` 0.7
patches those points; the underlying mismatch is that record-keeping written
as prose instructions depends on the model reading it correctly every time.

| Part | Idea |
|---|---|
| **Dependency rule** | The assistant depends on the skills; no skill depends on the assistant. Every skill stays usable on its own. |
| **Scripts** | Tree, status, dependencies, frontier, progress, broken links, and cycles are computed by code from the records, so the result does not depend on model reading. Starts as a script version of `task status`. |
| **Assistant** | Drafts objectives and criteria, proposes splits and plans, surfaces gaps and contradictions, and recommends which skill fits the current state. Grows from `oak`, which already recommends a next step without running it. |
| **Operator** | Approves every write, owns product and preference decisions, and chooses which tool runs. |

First experiment: a status script over the personal task store, then an `oak`
that runs it before recommending the next step. Try it on a real task tree and
judge whether reasoning over reliable state feels like an assistant.

Undecided:

- Which harness hosts it: Cursor, Claude Code (dedicated agent definitions), or both.
- How much it may do without asking: propose only, or also update status and bookkeeping.
- Whether "planning" includes writing implementation plans or stops at the
  objective and split, handing off to the normal plan step and `review-plan`.

## From the OAK foundation work

Capability gaps left open by the foundation work. Each needs the operator's authorization before work starts.

| Candidate | What it could improve |
|---|---|
| **`refine-prompt` premise support (G7)** | Make `refine-prompt` say where each premise comes from, so a reader can tell a sourced fact from an assumption. |

## Questions that need real use to answer

- Does a map stop when decisions are settled and hand off to plans, or remain
  open through implementation and final validation?
- Which records belong in local plans, and which need their own files?
- When should an active plan be amended, reviewed again, or superseded?
- Which existing skills earn regular standalone or process use?
- How much visual and automated tooling helps before maintenance outweighs it?

A useful first experiment is a case with a known inaccurate objective capture:
reconstruct its source discussions, confirm the destination, map the remaining
questions, and work one question through a session. Assess accuracy, ease of
resumption, visual usefulness, and maintenance cost before adopting a process.

Sources: [Wayfinder video](https://www.youtube.com/watch?v=F3lL98Pj90o),
[Wayfinder guide](https://github.com/mattpocock/skills/blob/main/docs/engineering/wayfinder.md),
[Pstack](https://github.com/cursor/plugins/tree/main/pstack), and its
[`recall`](https://github.com/cursor/plugins/blob/main/pstack/skills/recall/SKILL.md),
[`show-me-your-work`](https://github.com/cursor/plugins/blob/main/pstack/skills/show-me-your-work/SKILL.md),
and [verification](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md)
skills.
