---
name: review-plan
description: Independently review a completed engineering plan against its intended outcome and repository evidence. Use explicitly before implementation to find consequential gaps without generating speculative findings.
license: MIT
metadata:
  author: MjStryker
  category: review
  repository: "https://github.com/MjStryker/operator-agent-kit"
  status: experimental
  version: "0.1"
disable-model-invocation: true
---

# Review an implementation plan

Review only. Do not edit the plan or project files unless the user asks for revisions after the review.

Use a fresh subagent or context when available and authorized. Give the reviewer only the requested outcome, approved requirements and non-goals, accepted limitations, the proposed plan, and repository access or directly relevant references. If fresh-context review is unavailable, disclose that the review is less independent.

Review for correctness rather than finding volume. Ignore style preferences. A finding must state a falsifiable claim and have direct repository evidence when that evidence is accessible. When runtime or external evidence is unavailable, raise a named verification only if a concrete plan gap or repository fact makes the risk consequential. Discard unsupported suspicions.

## Checks

- The plan achieves the requested outcome.
- Every material scope item is covered by a concrete plan step, explicitly excluded, deferred to a named destination, or unresolved.
- Material readers, writers, consumers, contracts, persisted data, runtime paths, and operational work are covered.
- Instructions have one reasonable interpretation and are internally consistent.
- Types, runtime validation, serialization, persistence, and domain behavior agree.
- Sequencing handles applicable compatibility, migration, rollback, partial failure, retry, concurrency, authorization, lifecycle, multi-client behavior, and stale asynchronous completion.
- Frequent paths avoid payload amplification, unnecessary serialization, fan-out, and unbounded work.
- Verification can falsify the implementation rather than reproduce the plan’s assumptions, and completion conditions are observable.

Recommend the smallest correction or exact verification that resolves each surviving finding.

## Output

Prioritize findings by impact. For each include:

1. Issue and challenged claim.
2. Plan location.
3. Repository evidence or the concrete evidence gap.
4. Smallest correction or resolving verification.
5. Impact: `blocker | high | medium | low`.
6. Status:
   - `confirmed`: available evidence establishes the problem;
   - `likely`: evidence supports the problem but one material runtime or external fact is unavailable;
   - `needs-verification`: the plan relies on an unverified claim whose failure would materially affect the outcome.

Then provide:

- `Checked and looks sound`: coverage evidence for important checks that passed.
- `Remaining unknowns`: material unavailable information, or `none`.
- `Verdict`: `ready for implementation | ready after named verifications | revise before implementation | blocked on a decision or missing evidence`.

State directly when there are no blockers.
