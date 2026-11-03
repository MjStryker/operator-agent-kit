# Frozen obligations — contract 0.4

Assess obligations qualitatively: states, evidence, inspected paths and unknowns.
This contract provides no audit scores, weights, S/F/U totals, numerical coverage
or completion thresholds. If a request expects the removed scoring mechanism,
explain the contract change and provide the qualitative assessment; a separately
requested numerical methodology is outside this contract. Attribute external-tool
scores to their own rubric, never to the audit.

## Grid before investigation

Profile 0.3 keeps historical IDs as coverage families, not binary tests. Derive
bounded observable obligations from the relevant families, each with:

- stable ID and contributing specialties/families;
- expected property and source, labelled read, inferred or proposed;
- target paths/actors/conditions, applicability and reason;
- importance (`ordinary` or `consequential`) and expected evidence type/scope.

For example, SEC-3 can yield `USR-01`: member responses from GET /users and
GET /users/:id exclude passwordHash, sourced to the API privacy contract and
checked through serialization and response evidence. “All contracts agree” is too
broad. Merge equivalent obligations; duplicating checks must not inflate coverage.

Freeze selection policy, obligations and applicability before investigation.
Record necessary scope/applicability corrections with reason and effect. Never
split failures, remove failed/unknown obligations or rebuild the grid because
results displease. Material new scope needs a separately frozen investigation; it does not retroactively make old results comparable.

## States

- `satisfied`: evidence establishes the property within its declared scope.
- `not satisfied`: a confirmed violation, linked to a finding ID.
- `unverified`: neither result established, including unclear requirements,
  unavailable evidence/tooling or terminal delegation failure.
- `not applicable`: outside the target, with a reason.

A violation on one path can establish `not satisfied` while sibling paths remain
unknown. Passing a subset cannot establish the whole property. Keep unknowns
without retroactively splitting the obligation; “assessed” never means every path
was checked. Record evidence and actual root verification separately as specified
in [verification.md](verification.md). Temporary suspension keeps the audit pending;
it is not a terminal coverage result.
