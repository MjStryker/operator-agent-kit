# Close

Evaluate an `active` charter against its Definition of done. Do not close a `draft` charter or rewrite plan-time sections.

For every criterion, report `met`, `not met`, or `unverified` with independent evidence. Inspect referenced task outcomes and repository behavior, but do not treat task status, merged code, or completed plan steps as sufficient by themselves.

Then report:

- what was delivered;
- what was verified and how;
- what was not verified;
- deviations from the charter;
- residuals with named destinations;
- whether project-required closeout review exists and blocking findings are dispositioned.

Recommend `complete`, `abandoned`, or remain `active`. A `complete` recommendation requires every criterion to be met or an explicit operator acceptance of each named exception. Ask the operator to decide. After acceptance and the write guard, fill Outcome, set the accepted terminal status, and update `updatedAt`. Do not rewrite earlier sections to match the outcome.
