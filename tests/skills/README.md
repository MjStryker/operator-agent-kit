# Skill testing scope

This is the proposed development test scope, with an executable first corpus.
It does not require a charter, a multi-session project experiment, or a review
cycle for each skill edit. No behavioral or comparative utility result is claimed
by adding these scenarios.

## What each layer establishes

**Integrity, automated.** Validate YAML metadata, explicit-only adapter settings,
local Markdown file links, scenario coverage and byte-preserving installation
for Codex, ChatGPT, Claude and Cursor. Repeat installation to check replacement of obsolete
files and preservation of unrelated skills. This tests the declared settings and
the installer, not whether a harness enforces explicit invocation.

**Behavior, observed in fresh contexts.** Run short disposable scenarios and
assess the answer, tool actions and resulting files against `cases.json`.
Assertions describe outcomes, not exact wording. The corpus covers
all skills, with extra false-positive, missing-evidence, conflict and abstention
cases. Every skill has a smoke scenario; this is not full lifecycle coverage.

**Utility, comparative.** For a representative case, compare the same fixture
and request with and without the skill, keeping the model, harness, capabilities,
effort and operator replies equal. A compliant answer alone does not show added
value. Compare consequential errors avoided, required outcomes reached, unnecessary
edits, clarification count and elapsed time. Keep quality and cost separate;
do not invent a composite score or claim a time saving from one trial.

Read basis: the authority for each scenario is listed in its `contracts` field.
The metadata and installation checks follow [`skills/README.md`](../../skills/README.md).
Contract assessment and observed behavior are kept distinct.
The choice of initial scenarios and the run cadence below are test-design
proposals, not guarantees from those contracts.

## Run the fast checks

```sh
python3 -m pip install -r tests/skills/requirements.txt
python3 scripts/test-skills.py
python3 scripts/test-skills.py --list
python3 -m unittest discover -s tests/install
```

`tests/install/` covers installer safety: collisions, copy and backup failures,
rollback, backup, restore, renamed and retired skills, cancellation and refused
locations. It runs with a temporary `HOME`.

The check uses temporary installation destinations and does not replace real
installed skills. It exits nonzero on failure. Python 3 and Bash are required.

## Prepare a behavioral or utility trial

```sh
python3 scripts/test-skills.py --prepare fix-false-positive --arm skill --destination /tmp/oak-fix-skill
python3 scripts/test-skills.py --prepare fix-false-positive --arm baseline --destination /tmp/oak-fix-baseline
```

Each destination must be new. The runner creates:

- `workspace/`: the fixture, plus unchanged project-local skill files for the
  skill arm in `.agents/skills/` and `.claude/skills/`.
  Audit also includes the unchanged reusable specialist bundle.
- `prompt.txt`: the same request, with explicit invocation and the exact
  project-local skill path prepended only in the skill arm. This pins the copied
  contract instead of relying on same-name discovery. Use the harness's supported
  invocation syntax if it differs.
- `before.json`: SHA-256 inventory for comparing the files after the trial.
- `evaluation.json`: the rubric, exact skill file hashes and an ungraded result
  template. Every criterion starts as `not-run`.

The preparation runner prepares files; it does not launch models, configure isolation,
measure time or grade answers. Cursor installations are tested for byte integrity;
the behavioral setup initially targets Codex and Claude.

1. Open a fresh context rooted in `workspace/`, with no earlier trial history.
   Keep the rubric and before inventory outside the tested agent's context.
   Use an isolated harness configuration with global OAK skills and memory absent
   for both arms. A fresh chat alone does not ensure this. Record discovery of the
   selected skill and other available capabilities; do not call a baseline clean
   if inherited skills or memory were available. These files are not a sandbox;
   access beyond the fixture must be prevented or disclosed by the trial harness.
2. Give only `prompt.txt`. Record the full answer, tool calls, questions and
   replies, along with the model, harness version and collaboration capabilities.
   Use the same capability availability in both arms. For confirmation scenarios,
   end the first turn before accepting a proposed patch: the expected first-turn
   outcome is a proposal or question, with no unauthorized write.
3. Preserve the transcript and file diff. Grade each applicable criterion `pass`, `fail`
   or `not-run`, with a concrete transcript or diff locator. A stopped run or
   unavailable capability is not a pass. Do not infer tool order from the final
   answer. If performing a formal independent review, follow the project's
   different-model, read-only review policy; do not label a self-check independent.
4. For comparative trials, grade each arm before viewing the paired result.
   Criteria with `scope: contract` concern OAK's prescribed process and apply only
   to the skill arm; mark them `not-run` with reason `not applicable` in the
   baseline. Compare shared `scope: outcome` criteria and costs against the case's
   `value` statement. Do not penalize the baseline for not following OAK's internal
   process, and accept semantically equivalent outcomes without requiring OAK labels.
   A tie is evidence of no demonstrated gain on that case, not a reason to change
   the rubric. Retain failures and interruptions; do not rerun until green.

Start with paired `fix-false-positive`, `pushback-overclaim` and
`task-sync-conflict` trials: they test unnecessary edits, overstated evidence and
record authority. Use at least three fresh pairs per case when deciding whether a
revision improves utility; report individual outcomes and variation. Three pairs
are a practical starting sample, not a statistical guarantee. For a skill revision,
use the previous skill snapshot as an additional comparison when distinguishing
regression from the value of using any skill.

## Audit contract 0.4: targeted decision exercises

Contract 0.4 removes the numerical mode and its scoring reference. All audits
use `references/obligations.md` for qualitative states, inspected paths and unknowns.
Scenario contract lists identify current owners for evaluator traceability; they
are not required-reading lists supplied to the tested agent.

Some live prompts deliberately retain legacy score requests to exercise the
transition: explain the removed mechanism and return useful qualitative evidence,
without silently restoring scores or blocking on a numerical threshold. The seven
`trial_kind: decision-exercise` cases cover bounded contract decisions for:
family-only grids and legacy scoring requests, partial-path evidence, unavailable browser, quota/resumption,
impossible provider policy, stable historical IDs and qualitative delivery.
They read exported runtime fixtures; they do not call the actual runtime or launch
another audit. The quota case stages completion and unconfirmable resumption in
separate follow-ups; do not expose later events in the first context.

`python3 -m unittest discover -s tests/skills` additionally checks that preparation
copies the complete audit/profile bundle, keeps evaluator records outside the
workspace, and does not leak future quota events. Those are deterministic fixture
and packaging checks. They do not establish agent compliance, provider selection
or real quota recovery. Grade decisions from the recorded responses; grade actual
orchestration only from live runtime traces. The old runner's exact-session tests
verify its CLI transport, not the audit agent's mission lifecycle.

The scenario expectations were updated for audit 0.4, which removed audit
scoring. The revised behavioral scenarios have not yet been rerun.

A stopped decision exercise is not a completed live audit scenario. No test that
matches contract wording or parses the corpus proves behavior. Formal review rules
are unchanged.

## Development and release cadence

- Every edit: fast integrity checks.
- A changed skill or reference: scenarios for the affected skill, plus consumers
  when a shared workflow boundary changes. Record the exact source hashes.
- A corrected defect: add a scenario and demonstrate it fails on the old behavior
  before claiming regression protection. Existing scenarios are hypotheses until
  observed against the relevant good and bad behavior.
- Before release: the behavioral corpus on Codex and Claude with recorded versions
  and conditions. List every missing or interrupted run instead of treating it as
  green. Run comparative trials for skills whose utility changed materially.

A failed blocking criterion (scope, authority, false factual claims or a required
outcome) blocks claiming the tested behavior supported. Nonblocking criteria
track evidence quality and usefulness; record their failures too. Do not weaken
a criterion to hide a failure. Revise a scenario when an explicitly accepted
contract change makes its expectation obsolete, keeping the reason in Git.

## Deliberate gaps in this first corpus

- Task define, decomposition, archive, relationships and premise validity.
- Charter sync, close and material-change transitions.
- Successful MR review against an exact target and regression diff.
- Live interrupted delegations, disagreement and resumption paths (0.3 decision
  fixtures exercise policy choices, not real runtime recovery).
- Wider post-acceptance coverage: partial approvals, unaffected concurrent changes,
  relationship updates and recovery after a declined replacement. The additive
  write and conflicting stale-file cases are covered by the two-turn trials below.
- Harness enforcement of invocation settings, global/project skill discovery,
  model variability and behavior under unavailable tools.

Expand the corpus around real
defects and changed behavior rather than adding every mode before development
can continue.

## Optional live Codex runner

`scripts/run-skill-trials.py` runs the three starter cases, three pairs each,
under Linux `bwrap`. It uses file-based Codex authentication already present in
the local account. It consumes model usage; it does not grade responses or retry
failed trials. Supply the native runtime directory from your installed Codex CLI:

```sh
python3 scripts/run-skill-trials.py --vendor /path/to/vendor/x86_64-unknown-linux-musl --output /tmp/oak-live-trials
```

Use `--cases`, `--pairs`, `--jobs`, `--model` and `--timeout` to limit a campaign.
Cases may declare `followups` with a scripted reply and optional `before_files`
replacements, kept outside the tested agent's workspace. For the accepted-write
and stale-write cases, the runner ends the first turn, checks that the workspace
was not modified, applies any declared external replacement, then resumes the
exact UUID returned by `thread.started`. It verifies that the second turn keeps
that same session; it never selects the newest session. A failed first turn or an
early write stops the trial before the scripted acceptance. `--timeout` applies
to each turn. These are fixture-only replies, not approval to modify real records.

```sh
python3 scripts/run-skill-trials.py --vendor /path/to/vendor/x86_64-unknown-linux-musl --output /tmp/oak-resumed-trials --cases task-sync-accepted-write task-sync-stale-write
python3 -m unittest discover -s tests/skills -p test_live_runner.py
```

Per-turn prompts, events and before/after inventories are retained. In each
observation, `turns[].external_changes` identifies the runner's replacement,
while `turns[].agent_changes` identifies changes during that agent turn. The
aggregate `changes` includes both, so it must not be used alone to attribute
writes to the agent. The fake-CLI unit checks test runner behavior and credential
cleanup; they do not grade a model's behavior.

Every trial has its own home and Git worktree root. The original home, OAK source,
rubric and other trials are not mounted into the namespace. User configuration,
memory, browser and apps are disabled; collaboration is available in both arms.
The selected contract is path-pinned in the skill arm. The runner retains JSONL
events, session traces, before/after hashes and elapsed times. Check its recorded
skill-read evidence before treating a skill trial as applicable; missing discovery
or a correct answer by itself is not a successful skill invocation.

System runtime and networking for authentication/inference remain available.
Authentication is copied into the temporary home and removed after normal exit,
failure or timeout; if the runner itself is forcibly terminated, remove the
temporary `private-home/.codex/auth.json` copies before retaining the evidence.
No model answer, credential or full transcript belongs in Git by default.

Past campaign results are not kept in the repository; record new ones outside Git.

The isolated-environment approach follows the separation of agent-visible inputs from evaluator answers in
OpenAI's [harness-aware evaluation example](https://developers.openai.com/cookbook/examples/partners/harness_aware_plugin_evals/harness_aware_plugin_evals).
