# Review record

```text
CHARTERS_DIR: docs/charters
REVIEWS_DIR: docs/charters/reviews
```

Resolve both paths from the project root under the charter storage rules. `REVIEWS_DIR` must remain inside `CHARTERS_DIR`. Create it only after the operator accepts a complete review record.

Name the record `{charter-id}-{reviewedAt}.md`, with `reviewedAt` rendered as compact UTC `YYYYMMDDTHHMMSSZ`. Stop on a collision; never overwrite a review.

Use this frontmatter:

```yaml
---
charter: release-readiness
charterUpdatedAt: 2026-09-20T20:15:21Z
charterSha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
verdict: ready-to-activate
independence: fresh
reviewedAt: 2026-09-20T20:30:00Z
author:
  harness: claude-code 2.1.0
  model: claude-opus-5-5
reviewer:
  harness: codex-cli 0.155.1
  model: gpt-6-sol
  effort: high
---
```

- `charter`: charter id and filename stem.
- `charterUpdatedAt`: exact `updatedAt` of the reviewed charter.
- `charterSha256`: lowercase SHA-256 of the complete reviewed charter file bytes.
- `verdict`: `ready-to-activate` | `ready-after-verification` | `revise-before-activation` | `blocked`.
- `independence`: `fresh` | `reduced`. When project policy requires review on a different model, `fresh` also requires a known `author.model` that differs from `reviewer.model`; otherwise record `reduced`.
- `reviewedAt`: ISO-8601 UTC.
- `reviewer`: the harness (with version), model, and reasoning effort that produced the review, taken from the launch configuration or reported by the environment. Use `unknown` for any value neither source establishes; never infer it. Records written before this field existed remain valid without it.
- `author`: the harness (with version) and model that wrote the reviewed charter version, taken from the operator, the authoring session, or project records. A reviewer cannot establish it from the charter alone. Use `unknown` for any value not established; never infer it. Records written before this field existed remain valid without it.

The body contains the charter title, findings, coverage evidence, and remaining unknowns. Preserve finding impact and status. Use `_None._` for an empty findings or unknowns section. Review records are immutable evidence: corrections require a new record.

Compute the digest from the final re-read immediately before persistence and verify it still matches the proposed record. The timestamp and digest identify the exact charter version reviewed. A later change means the record describes an earlier version; it does not make the historical record invalid. Reviews are advisory unless project policy explicitly uses them as a gate.
