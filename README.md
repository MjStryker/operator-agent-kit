# OAK — Operator-Agent Kit

OAK is a toolkit of small, portable building blocks for more reliable work
between operators and AI agents. It is agnostic by design: usable with any
LLM, in any framework, IDE, or agent harness.

## Why

AI agents are fast, but common failure modes make their output harder to
trust: acting on unclear requests, overstating what was verified, raising
speculative review findings, fixing issues that were never real, and losing
decisions between conversations.

OAK addresses these with explicit, operator-triggered workflows. Each one
covers a single step, such as clarifying a request, reviewing a plan or diff,
verifying an issue before fixing it, or challenging a response. The agent does
the work; the operator decides what gets done and when.

## Quick start

Requires Git and Python 3.

```sh
git clone https://github.com/MjStryker/operator-agent-kit.git
cd operator-agent-kit
scripts/install-skills.sh --list-harnesses   # known harnesses and destinations
scripts/install-skills.sh --harness claude   # or codex, chatgpt, cursor; --all for every one
```

The installer previews every change, backs up the affected skills directories,
and asks for confirmation before copying anything. For other harnesses, pass a
destination directory or copy `skills/` manually; see
[`skills/README.md`](skills/README.md#deployment).

Then, in your agent, invoke a skill by name. Skills never trigger on their own:

```text
oak             # which OAK skill fits what I am doing?
refine-prompt   # turn a draft request into a clear prompt
review-plan     # cold-review a finished implementation plan
```

## Repository

- [`skills/`](skills/) — small, standalone agent skills and how to use them.
- [`agents/`](agents/) — reusable specialist definitions, bundled with the audit skill.
- [`docs/charters/workflow.md`](docs/charters/workflow.md) — the project charter for composing charters, tasks, recon, planning, execution, and verification.
- [`docs/audits/`](docs/audits/) — known defects in OAK, open until fixed or deliberately accepted.
- [`tests/skills/`](tests/skills/) — integrity checks and disposable scenarios for skill behavior and comparative utility.

Invoke `oak` when you want help choosing the smallest suitable OAK skill or
workflow. It recommends what to invoke next without running it for you.

Additional components will be introduced only when their purpose and
implementation are established.

## License

MIT. See [`LICENSE`](LICENSE).
