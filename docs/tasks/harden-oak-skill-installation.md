---
id: harden-oak-skill-installation
title: Harden OAK skill installation
scope: project
status: open
createdAt: 2026-10-13T20:39:26Z
updatedAt: 2026-10-13T20:41:15Z
---

# Harden OAK skill installation

## Objective
Install and update OAK skills without losing existing skills,
with simple interaction, a way to roll back, and compatibility
verified on the installed harness versions.

## Sub-steps
_None._

## Success
- Only skills identified as belonging to OAK are modified.
- Third-party skills or skills of unknown provenance remain untouched.
  A collision blocks installation of the OAK skill concerned.
- Old OAK skills that were renamed or removed are reported;
  their cleanup is offered, never silent.
- A complete backup of the skill directories concerned,
  including third-party skills, succeeds before any modification.
- A restore brings back the backed-up state,
  including after accidental corruption of third-party skills.
- The script asks for the backup root, with a default
  usable by pressing Enter.
- A preview shows the operations, warnings, detected versions
  and backup paths.
- The script always asks for confirmation before any modification
  of the installation; a refusal or no answer cancels the operation.
- Dangerous destinations, notably those overlapping the
  sources or placing backups inside the skills, are refused.
- Compatibility is verified for Cursor, Codex, Claude Code
  and ChatGPT on the installed versions.
- Results distinguish copy, discovery and explicit invocation;
  any impossible or incomplete validation is stated.
- Tests cover collisions, copy failures, backup,
  restore, renames, removals and cancellation.

## Failure
- A third-party skill or a skill of unknown provenance is modified or deleted.
- A modification starts without a successful complete backup.
- The confirmation can be bypassed.
- A cleanup removes a skill that is not identified as OAK.
- A backup is discovered as a skill.
- Compatibility is claimed without sufficient evidence.

## Constraints and non-goals
- Keep the current names, without an `oak-` prefix.
- Limit the actions asked of the user to selecting the harnesses,
  choosing the backup root and confirming
  the operations presented.
- Initially target the installed versions;
  support for older versions is not required.
- Take into account the directories the harnesses actually read.
- Check how ChatGPT currently manages skills;
  do not assume a local copy is enough.
- The appropriate installation method for each product remains to be determined
  based on the checks.
- The implementation and its execution order belong to the plan.

## Premises
P1. **Claim:** The current script deletes every directory bearing
    the name of a source skill before copying it, without checking
    its provenance.
   - Basis: observed
   - Authority: agent
   - Evidence:
     - supports: `scripts/install-skills.sh`, lines 113–123,
       @ `a9cf602177d7b020a2f99f198fc90f868aeb1198`
   - AssessedAt: 2026-10-13T20:09:43Z
   - RevalidateWhen: `scripts/install-skills.sh` changes

## Key decisions
D1. No `oak-` prefix; keep the current names.
D2. Never modify third-party skills.
D3. Offer cleanup only for old OAK skills that were
    renamed or removed.
D4. Back up the directories concerned in full so that
    third-party skills are also protected against a script error.
D5. Always present the warnings and ask for confirmation.
D6. Target the installed harness versions.
D7. Ask for a configurable backup root.
    Proposed default: `$HOME/.oak/install/backups/`,
    with a unique subfolder per installation and per harness.
D8. Task contract explicitly approved in this discussion
    on 2026-10-13T20:41:15Z. The status remains `open` until
    the objective is verified; approval does not mean completion.

## Open questions
_None._
