# Contributing

OAK is public. Keep private data out of files, examples, test fixtures,
commit messages, and pull request or issue text: use invented, generic cases.

## Issues

Anyone can open an issue to report a defect or propose a change. Describe
what you observed or need, with a minimal invented example when useful.

Pull requests are limited to the maintainer. A proposal accepted in an issue
is implemented by the maintainer.

## AI-assisted proposals

Proposals written with an AI agent are welcome. Say so in the issue and name
the model used. When you can, also give the harness and its version, and the
reasoning effort level. This helps reproduce the observed behavior and weigh
the proposal.

## Maintainer checks

- Run the fast checks listed in [`tests/skills/README.md`](tests/skills/README.md#run-the-fast-checks).
  They include `scripts/check-private-data.py`, which flags email addresses,
  home directory paths, and credential formats, plus any terms listed in a
  local file kept outside the repository (`~/.config/oak/private-terms.txt`,
  or the path in `OAK_PRIVATE_TERMS`).
- To run that check on every commit, enable the bundled hook once per clone:
  `git config core.hooksPath .githooks`.
- When a skill changes, update its `metadata.version` and its scenarios in
  `tests/skills/cases.json`, as described in [`tests/skills/README.md`](tests/skills/README.md).
- Commit messages are a short imperative subject line with no body
  (for example `Harden charter activation`).

Agents editing OAK also follow [`AGENTS.md`](AGENTS.md).
