---
name: fix-issue
description: Verify and resolve a reported bug, review finding, CI failure, or other engineering issue. Use explicitly when the user wants the claim checked and a justified fix implemented without expanding scope.
license: MIT
metadata:
  author: MjStryker
  category: implementation
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.1"
disable-model-invocation: true
---

# Fix an issue

Treat the report as a claim. Establish whether it is true and whether it should be changed now before editing. A false alarm wastes as much time as a missed bug.

## Verify

1. Locate the implicated behavior and cite the code, configuration, logs, test output, or diff that supports or refutes the report. Do not classify from a matching name alone.
2. Reproduce the problem or run the failing path when practical. If reproduction is unavailable, state what evidence substitutes for it and what remains uncertain.
3. When an MR or branch is relevant, compare the exact change with its known target branch and inspect recent commits when they clarify intent. Determine whether the behavior was introduced by the change, is pre-existing, is already fixed, or lies outside the diff. Do not guess the target branch.
4. Trace affected callers, consumers, contracts, tests, persistence, and runtime paths far enough to establish impact and avoid breaking another use.

## Decide

Record the truth of the claim separately from what should happen next.

Claim status:

- `false positive`: the reported behavior is absent, already fixed, or based on a mistaken reading;
- `confirmed`: evidence establishes the reported behavior;
- `not established`: available evidence cannot yet confirm or refute it.

For a confirmed issue, choose one disposition:

- `fix now`: the issue is in scope and the correct behavior is sufficiently clear;
- `defer`: the issue is real but belongs to a separate change or named owner;
- `accept`: changing it would be disproportionate or the behavior is an accepted limitation.

Do not treat “edge case,” “legacy,” or “outside this MR” as proof that an issue is unimportant. Explain impact and the concrete reason for the disposition.

## Act

- For `false positive`, `not established`, `defer`, or `accept`, do not edit. Report the evidence and the next resolving action, if any.
- For `fix now`, implement the smallest complete fix. Inspect affected call sites and contracts, add or update a regression test when it provides meaningful protection, and run the relevant checks.
- Ask the user only when a missing decision changes observable behavior, scope, risk, ownership, or another material tradeoff. Otherwise make and state the narrowest supported assumption.
- Do not perform adjacent cleanup.

## Report

Include:

- claim status and, when confirmed, disposition;
- evidence and impact;
- changes made, affected surfaces checked, and verification results for `fix now`;
- unresolved information or `none`.
