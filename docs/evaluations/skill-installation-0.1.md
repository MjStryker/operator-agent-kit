# Skill installation 0.1 compatibility evaluation

**Date:** 2026-10-13
**Revision under test:** working tree on `9432553` with the rewritten installer (`scripts/install-skills.sh` → `scripts/install_skills.py`)
**Task:** [`harden-oak-skill-installation`](../tasks/harden-oak-skill-installation.md)

## Question

On the harness versions installed on the evaluation machine, does a skill copied by the installer reach the harness, at three distinct levels?

- **Copy:** the installed files are byte-identical to the package.
- **Discovery:** the harness registers the installed skill.
- **Explicit invocation:** naming the skill puts the installed `SKILL.md` content into the model context.

## Harnesses

| Harness | Detected version | Install target | Directories read (source) |
|---|---|---|---|
| Codex CLI | `codex-cli 0.162.1` | `~/.agents/skills` | `$HOME/.agents/skills` (OpenAI Codex skills documentation); `$CODEX_HOME/skills` (string in the installed binary) |
| ChatGPT desktop (Linux) | `26.1007.21434`, bundled `codex-cli 0.162.0-alpha.17.2` | `~/.agents/skills` | `$HOME/.agents/skills` (string in `/usr/lib/chatgpt/resources/app.asar`); the package metadata declares `"codexAppBrand": "chatgpt"` and ships a Codex binary |
| Claude Code | `2.1.296` | `~/.claude/skills` | `~/.claude/skills`, project `.claude/skills` |
| Cursor | `3.24.12` | `~/.cursor/skills` | `~/.cursor/skills`, `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills` (Cursor skills documentation) |

ChatGPT on the web stores skills server-side through its own upload flow. A local copy does not reach it, and this evaluation does not cover it.

## Method

Each copy was made by the installer itself, answering its prompts, into a disposable location. Probes ask the model to reply, without any tool, with content that only the installed copy holds, or `NOT_LOADED`. A missing-skill control (`oak-missing-skill`) was run with the same probe.

- **Codex and ChatGPT engine:** `HOME` pointed to a disposable directory where the installer had written `~/.agents/skills`; `CODEX_HOME` stayed on the operator's configuration for authentication, so sessions were recorded there. `audit` existed only in the disposable copy. `codex exec --json -s read-only '$audit …'`, then the same with `/usr/lib/chatgpt/resources/codex`.
- **Claude Code:** credentials cannot be isolated without copying them, so the installer wrote to a disposable project's `.claude/skills` (`DEST` override) and `claude -p --output-format stream-json` ran there with the operator's real home. `audit` existed only in that project. Claude Code strips the frontmatter before injection, so the probe asks for the first sentence of the body.
- **Cursor:** `cursor agent status` reported `Not logged in`. No agent run was possible.

## Results

| Harness | Copy | Discovery | Explicit invocation |
|---|---|---|---|
| Codex 0.162.1 | verified | verified through the explicit mention | verified: `audit 0.2`, no command run; control `NOT_LOADED` |
| ChatGPT 26.1007.21434 | verified | partial: bundled engine only | partial: bundled engine replied `audit 0.2`, no command run; app interface not observed |
| Claude Code 2.1.296 | verified | verified in a project directory: `audit` listed in the `init` skills | verified in a project directory: replied `Investigate and report only.`; control `NOT_LOADED` |
| Cursor 3.24.12 | verified | not verified | not verified |

Copy was verified for every target by the installer's own byte comparison and by `tests/install/` and `scripts/test-skills.py`.

## Observations

- Codex does not list explicit-only skills (`allow_implicit_invocation: false`) to the model. A request to list available skills returned only system skills. Discovery is therefore observable only through invocation.
- Claude Code's `init` event also listed user-level OAK skills from `~/.claude/skills`, including `discover-complex-work`, which exists only there. The directory is read by 2.1.296. The installer's own user-level copy was not probed.
- Cursor reads four user-level directories. Installing for Cursor together with Codex or Claude Code makes the same OAK skills visible to Cursor several times. The installer reports this; whether Cursor deduplicates them is not verified.
- Running `cursor agent status` installed the Cursor agent CLI (`2026.10.01-e373342`) into `~/.local/share/cursor-agent` as a side effect.

## Not verified

- Cursor discovery and invocation, on any version.
- ChatGPT desktop discovery and invocation through its interface; ChatGPT web skills.
- Claude Code invocation from the user-level `~/.claude/skills` written by this installer.
- Any harness version other than those listed. The installer reports a different detected version as not verified.
