# UI/UX React

Expertise: React behavior, interaction design and accessible interface states.

Trace user journeys through state, effects and rendering. Inspect relevant
loading, empty, error and success states, keyboard/focus behavior, semantics and
responsive layouts. Separate observable usability failures from aesthetic taste.
Use an available browser for runtime or visual claims; a source inspection alone
does not establish a rendered layout, contrast measurement or completed journey.

## Tools

For a React target, use React Doctor for scoped static diagnostics when available
and permitted. Prefer the project's installed executable or configured command;
check its version/help and supported flags. Example for a compatible local CLI:

```sh
./node_modules/.bin/react-doctor . --json --no-score --no-supply-chain
```

Read the [official CLI reference](https://www.react.doctor/docs/reference/cli-reference)
when choosing flags. These options request structured diagnostics without the
score API/crash reporting or dependency supply-chain checks. Match the scan to
the audit target; for partial scopes provide the established baseline explicitly.
An introduced-only scan cannot prove an old finding is corrected.

Do not run `install`, CI setup, rule-changing commands or auto-fixes. If the CLI
is absent or incompatible, report that limit and use available checks; do not
download `@latest` implicitly. Verify each diagnostic against the code and
requirements. Attribute any React Doctor score to that tool, not to an OAK audit score.

Use available browser tooling for rendered journeys and accessibility evidence,
and the project's React lint/type checks when relevant. Static diagnostics alone
cannot establish visual quality or a completed interaction. Apply the shared
tool execution and evidence rules in [common.md](common.md).

Coverage families, profile version `0.3` (historical IDs retained):

- `UI-1`: scoped user journeys achieve their intended outcome.
- `UI-2`: React state and effects preserve that outcome across relevant transitions.
- `UI-3`: relevant accessibility requirements hold for the interaction.
- `UI-4`: required UI states and target viewports remain usable.

Without rendered evidence, leave affected obligations unverified.
