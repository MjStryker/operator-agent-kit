---
name: review-mr
description: Independently review a merge request, branch, or diff for correctness, regressions, missing affected surfaces, and readiness to merge. Use explicitly when the user wants an evidence-backed code review without speculative findings or edits.
license: MIT
metadata:
  author: MjStryker
  category: review
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.1"
disable-model-invocation: true
---

# Review a merge request

Review only. Do not modify project files, format code, update dependencies, or commit changes unless the user asks for fixes after the review.

Use a fresh subagent or context when available and authorized. Provide the requested outcome, approved requirements and non-goals, accepted limitations, MR or branch identity, and repository access. If fresh-context review is unavailable, disclose that the review is less independent.

Resolve the exact target branch and review diff from repository or MR metadata. Do not guess. Treat the title, description, commits, tests, and inline rationale as useful context and claims to verify rather than proof of correctness.

Review for correctness rather than finding volume. A finding must be concrete and falsifiable, with direct repository evidence when accessible. When runtime or external evidence is unavailable, request a named verification only if a repository fact or untested path makes the risk consequential. Discard unsupported suspicions and style preferences.

## Checks

- The change achieves the intended outcome, including requirements not restated in the title.
- Changed behavior is correct across meaningful null, empty, error, boundary, and asynchronous paths.
- Affected callers, consumers, contracts, persisted data, configuration, generated artifacts, and runtime paths remain compatible.
- Types, runtime validation, serialization, persistence, and domain behavior agree.
- Applicable migration, rollback, partial failure, retry, concurrency, authorization, observability, lifecycle, and multi-client concerns are handled.
- Frequent paths avoid payload amplification, unnecessary serialization, fan-out, and unbounded work.
- Tests exercise the changed behavior and would fail for the relevant regression rather than mirror the implementation.
- Every material scope item is implemented, explicitly excluded, deferred to a named destination, or unresolved.
- Repository-specific architecture and dependency rules are applied only when local documentation or established code makes them applicable.

Run relevant read-only checks when feasible. Record what each check actually establishes. Separate problems introduced by the change from pre-existing behavior.

## Output

Prioritize findings by impact. For each include:

1. Issue and challenged claim.
2. File and hunk or symbol.
3. Repository evidence.
4. Smallest fix or resolving verification.
5. Impact: `blocker | high | medium | low`.
6. Status:
   - `confirmed`: available evidence establishes the problem;
   - `likely`: evidence supports the problem but one material runtime or external fact is unavailable;
   - `needs-verification`: merge safety depends on an unverified claim whose failure would materially affect the outcome.

Then provide:

- `Checked and looks sound`: coverage evidence for important checks that passed.
- `Remaining unknowns`: material unavailable information, or `none`.
- `Verdict`: `ready to merge | ready after named verifications | revise before merge | blocked on a decision or missing evidence`.

State directly when there are no blockers.
