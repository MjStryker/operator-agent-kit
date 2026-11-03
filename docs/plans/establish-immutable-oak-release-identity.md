# Plan: immutable OAK release identity

Serves [`establish-immutable-oak-release-identity`](../tasks/establish-immutable-oak-release-identity.md). Criteria and decisions live in the task; this plan holds only the execution order and verification points.

Moving parts: one script (`scripts/oak-release.py`, Python 3 standard library), one current manifest (`skills/MANIFEST.json`), one append-only release history (`releases.json`), and small changes to the installer and documentation.

## 1. Install skill files unchanged

- Remove the `HARNESS` rewrite from `scripts/install-skills.sh`; the installed `task` skill falls back to the harness name in system context (task premise P3).
- Update the Deployment section of `skills/README.md` accordingly.
- Verify: install for Codex and Claude into scratch directories; `diff -r` against `skills/` is empty. Run `task resume` once in each harness to confirm the empty `HARNESS` still resolves.

## 2. Manifest and identity

- Add `.gitattributes` forcing LF checkout for `skills/**`, so checkout settings cannot change raw bytes.
- `oak-release.py manifest` writes `skills/MANIFEST.json`: for each skill, every regular file's `/`-separated relative path, size, and SHA-256, sorted bytewise; empty directories ignored; symlinks rejected. A skill's identity is the SHA-256 of its sorted entries.
- `oak-release.py check` fails when the committed manifest does not match the files on disk.

## 3. Release rules

- `releases.json` is an append-only list of releases: project version, commit, and each skill's `(name, version, identity)`. The latest entry is the current project version; the Git tag `v<version>` marks the release commit.
- `oak-release.py verify-release <version>` rejects: a skill whose identity changed without a version increment; a released `(name, version)` associated with different content; a project version that does not increase.
- Versions released before the first entry are legacy and unverified.

## 4. Fixtures

- `tests/release/` covers modified, added, removed, and renamed files; a supporting file; a dotfile; CRLF versus LF bytes; an unlisted file; a rejected symlink; and each step 3 rejection. One command runs them all.
- Verify: every negative case is seen failing against broken input before it is trusted.

## 5. Installer verification and reporting

- Before copying, the installer runs `check` and stops on mismatch.
- The preview classifies each skill as new, version change, unchanged, or same-version drift. Copy behavior is otherwise unchanged.
- Verify: an installed skill edited without a version change is reported as drift.

## 6. Documentation

- Replace "not defined yet" in `skills/README.md` with the release event, increment rules (task D4, D12, D13), immutability boundary, verification procedure, legacy treatment, and the integrity-versus-authenticity distinction.
- Note that local edits to installed `task/references/core.md` configuration report as same-version drift.
- Allow audit `found_in` to name a project version alone.

## 7. First release

- Run `verify-release`, append the first `releases.json` entry, and tag. Commit and tag only with operator approval.

## 8. Cross-computer check (operator)

- On another computer, from a fresh clone: `oak-release.py check`, then install. Skill identities must match the `releases.json` entry.
