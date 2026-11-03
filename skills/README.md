# Agent skills

Each skill is a directory containing a `SKILL.md` file (Markdown with YAML
frontmatter) and, optionally, supporting references. Skills are written to be
independent of any particular model, framework, IDE, or agent harness.

## Skills

| Skill | Use |
|---|---|
| [`oak`](oak/SKILL.md) | Find the smallest suitable OAK skill or workflow and what to invoke next. |
| [`charter`](charter/SKILL.md) | Manage repository-owned capability commitments and their lifecycle. |
| [`recon`](recon/SKILL.md) | Scout a repository-backed engineering objective through scout and challenger subagents before choosing what to do next. |
| [`think`](think/SKILL.md) | Answer a search or planning question through a subagent, keeping exploration out of the conversation. |
| [`fix-issue`](fix-issue/SKILL.md) | Verify a reported issue and fix it only when warranted. |
| [`pushback`](pushback/SKILL.md) | Challenge unsupported or overstated claims in an agent response. |
| [`refine-prompt`](refine-prompt/SKILL.md) | Turn a draft request into a clear prompt without executing it. |
| [`review-charter`](review-charter/SKILL.md) | Optionally cold-review a charter and persist accepted review evidence. |
| [`review-plan`](review-plan/SKILL.md) | Cold-review a completed implementation plan. |
| [`review-mr`](review-mr/SKILL.md) | Cold-review a merge request, branch, or diff. |
| [`audit`](audit/SKILL.md) | Verify specialist findings and bounded obligations, report qualitative evidence and limits, and compare previous audits. |
| [`assess`](assess/SKILL.md) | Give a concise, evidence-led assessment instead of a subjective reaction. |
| [`task`](task/SKILL.md) | Define, decompose, synchronize, resume, and list durable task objectives. |

Each skill's `SKILL.md` is the authority for what it does and which modes it
accepts. These skills are explicit-only: the operator invokes them by name, and
the agent should not trigger them on its own. Invocation syntax depends on the
harness, for example:

```text
oak
review-plan
charter define
task define
```

## Workflow

Use only the stages that fit the work. How charters, recon, tasks, and plans
compose, including the short paths, is defined in
[`docs/charters/workflow.md`](../docs/charters/workflow.md), Operating model.
Each review skill's `SKILL.md` says when it applies, and `oak` recommends a
route for a given objective.

## Metadata and versioning

Each `SKILL.md` declares:

- `license`: the skill's SPDX license identifier.
- `metadata.author`: the skill's author.
- `metadata.category`: its primary workflow category.
- `metadata.repository`: the canonical source repository.
- `metadata.status`: its lifecycle status (`experimental`, `active`, or
  `deprecated`).
- `metadata.version`: its `major.minor` version.

The version covers the whole skill directory, including its references,
scripts, and assets.

The rules for incrementing versions and publishing releases are not defined yet.

## Deployment

Copy each skill directory into the skills location your harness reads. For a
manual audit installation, also copy the repository's `agents/` contents into
the installed `audit/references/specialists/` directory. Then adapt
harness-specific details:

- **Explicit-only invocation.** Each skill carries its adapter settings in its
  `SKILL.md` frontmatter and `agents/openai.yaml`. If your harness uses a
  different mechanism to prevent automatic invocation, use that instead.
- **`task` configuration.** Optionally set the personal store, project store, and local bindings path in `task/references/core.md`. Leave `HARNESS` empty to use the harness name from system context, or set it to override that name.

[`scripts/install-skills.sh`](../scripts/install-skills.sh) copies the skill
directories unchanged into one or more harness skill directories. It requires
Python 3. Its usage is in `scripts/install-skills.sh --help`, and its known
harnesses, destinations and the other directories each harness reads are in
`scripts/install-skills.sh --list-harnesses`. Any other harness-specific step is
still up to you.

The installer only replaces skills whose `SKILL.md` declares this repository in
`metadata.repository` and the directory's name. Any other entry with an OAK
skill name blocks that skill and is left intact. Former OAK skills are listed
and their removal is offered, never automatic. It asks for a backup root
(default `~/.oak/install/backups/`), previews operations, alerts, detected
harness versions and backup paths, and changes nothing without confirmation.
Before any change, it backs up and verifies every affected skills directory in
full, third-party skills included; restore with
`scripts/install-skills.sh --restore RUN_DIR` and list runs with
`--list-backups`. Verified harness versions and the level reached for each
(copy, discovery, explicit invocation) are in
[`skill-installation-0.1.md`](../docs/evaluations/skill-installation-0.1.md).

Reusable [specialist definitions](../agents/README.md) live outside the skills.
The installer also bundles their unchanged files into
`audit/references/specialists/`, so an installed audit does not need the OAK
checkout. They are reusable mission profiles, not native agent registrations.
