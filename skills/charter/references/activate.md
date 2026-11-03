# Activate

Move a bound charter from `draft` to `active`. Activation authorizes the chartered commitment, not arbitrary implementation.

If the bound charter is already `active`, report that and stop without writing.

Before proposing activation, verify:

- the objective is one coherent capability;
- Baseline contains enough current evidence to scope responsibly;
- every material concern is in scope, deferred with a destination, out with a reason, or unresolved;
- `Unresolved` contains no decision that could materially change the commitment;
- Definition of done is observable and can falsify completion claims;
- Non-goals protect the important boundaries;
- task references, when present, resolve or are explicitly external.

Independent review is optional unless project policy explicitly requires it. When review records exist, summarize material findings so the operator can make an informed decision; do not turn them into an implicit gate.

Report failures and stop. When the checks pass, show the activation decision and complete status/timestamp patch, then ask the operator to accept it. After acceptance and the write guard, change `status` to `active` and update `updatedAt`. Preserve every body section. The operator's acceptance is the activation authority.
