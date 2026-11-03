---
id: establish-immutable-oak-release-identity
title: Establish immutable OAK release identity
scope: project
status: paused
createdAt: 2026-09-20T21:15:00Z
updatedAt: 2026-09-22T07:17:11Z
---

# Establish immutable OAK release identity

## Objective

Ensure each OAK release identifies exactly one complete canonical source file set, at both project and component scope, whose integrity can be verified reproducibly before that content is installed unchanged across supported computers.

## Sub-steps

- A committed release manifest completely identifies every distributed skill.
- Version rules bind each released version to one immutable canonical content identity.
- Installation verifies and reports content state without modifying canonical skill files.
- Deterministic fixtures and a cross-computer installation establish that verification is portable.
- A project version identifies each release as a whole, independently of which component types it contains.

## Success

- A committed manifest enumerates every distributed regular file in each skill, including `SKILL.md`, supporting files, and dotfiles.
- Each manifest entry records a `/`-separated relative path, byte size, and SHA-256 digest of the file’s raw bytes.
- Manifest entries are ordered deterministically, empty directories do not affect identity, and symlinks inside skill directories are rejected.
- Changed, added, removed, and renamed files all change the canonical content identity.
- A release containing changed canonical content without a corresponding `major.minor` version increment is rejected.
- A released `(skill name, version)` cannot subsequently be associated with different canonical content.
- `MAJOR` identifies a breaking skill-contract change; `MINOR` identifies every other released content change, including corrections.
- The installer verifies source content before copying it and reports at least: new skill, version change, unchanged verified content, and same-version content drift.
- Installed canonical skill files remain byte-for-byte identical to their verified source files.
- Harness selection no longer requires rewriting `task/references/core.md`; it is resolved at runtime or through configuration stored outside the canonical skill directory.
- Deterministic fixtures cover modified, added, removed, and renamed files; supporting files; dotfiles; line-ending differences; unlisted files; and rejected symlinks.
- From a fresh checkout on another operator computer, verification and installation produce the same canonical identities without unrecorded local input. A different operating system is not required.
- Repository documentation defines the release event, version-increment rules, first immutable boundary, verification procedure, historical-version treatment, and the distinction between integrity and authenticity.
- OAK carries a `major.minor` project version covering the whole repository at the release event, not only the distributed skill set.
- Project version increments follow the component rule: major for a breaking contract change in any component, minor for every other released content change.
- A released project version cannot subsequently be associated with different repository content.
- An audit finding can record `found_in` as a project version without naming a component.

## Failure

- Two different canonical file sets are accepted for the same released skill name and version.
- A changed, added, removed, renamed, or unlisted distributed file escapes detection.
- Equivalent committed content produces different identities because of traversal order, checkout behavior, or machine-local state.
- Installation modifies a verified canonical skill file.
- Verification succeeds only inside the originating Git checkout or depends on an unrecorded local input.
- A historical version predating the immutable boundary is represented as verified.
- A matching digest is represented as proof of authorship or trust.

## Constraints and non-goals

- Preserve OAK’s portable skill-directory model and support multi-file skills such as `task`.
- Keep verification independent of a particular agent harness.
- Retain the existing `major.minor` version shape.
- Treat the committed manifest as the authoritative distributed file set.
- Use raw file bytes for content digests; do not define semantic Markdown or YAML normalization.
- Begin enforcement with the first release produced after this objective is completed. Earlier releases remain explicitly legacy and unverified.
- Keep installer changes limited to verification, classification, reporting, and removal of in-directory harness mutation; do not redesign its copy/update behavior.
- Keep this objective separate from the coherent-workflow charter.
- Do not create a package registry, update service, dependency-management system, or release channel.
- Cryptographic signing, attestations, and full supply-chain provenance are follow-ups. This objective provides integrity, not authenticity.
- Record a checkpoint for the current workflow evaluation before implementation changes shared skills or installer behavior.

## Premises

P1. **Claim:** At revision `b0202056c562cbeeefc8461f06e0eb8d661a35f5`, OAK documents that a skill version covers its whole directory while leaving version-increment and release rules undefined.
   - Basis: observed
   - Authority: agent
   - Evidence:
     - supports: `skills/README.md` lines 61-76 @ `b0202056c562cbeeefc8461f06e0eb8d661a35f5`
   - AssessedAt: 2026-09-20T21:13:30Z

P2. **Claim:** At revision `b0202056c562cbeeefc8461f06e0eb8d661a35f5`, the installer compares `metadata.version`, copies complete skill directories, and rewrites installed `task/references/core.md` with the selected harness.
   - Basis: observed
   - Authority: agent
   - Evidence:
     - supports: `scripts/install-skills.sh` lines 79-123 @ `b0202056c562cbeeefc8461f06e0eb8d661a35f5`
   - AssessedAt: 2026-09-20T21:13:30Z
   - RevalidateWhen: `scripts/install-skills.sh` changes

P3. **Claim:** An empty `HARNESS` in `task/references/core.md` already directs agents to use the harness name supplied by system context.
   - Basis: observed
   - Authority: agent
   - Evidence:
     - supports: `skills/task/references/core.md` lines 3-16 @ `b0202056c562cbeeefc8461f06e0eb8d661a35f5`
   - AssessedAt: 2026-09-20T21:13:30Z
   - RevalidateWhen: `skills/task/references/core.md` changes

P4. **Claim:** The operator currently uses the installer to distribute updated OAK skills to other computers.
   - Basis: stated
   - Authority: operator
   - AssessedAt: 2026-09-20T21:13:30Z

P5. **Claim:** OAK history contains different `task` directory contents carrying version `0.2`.
   - Basis: observed
   - Authority: agent
   - Evidence:
     - supports: `skills/task/` @ `8bdf65993a`
     - supports: `skills/task/` @ `baf9214ea2`
     - supports: `skills/task/` @ `5f6148f4c8`
   - AssessedAt: 2026-09-20T21:13:30Z

P6. **Claim:** OAK is expected to gain component types beyond skills, such as frameworks and a harness.
   - Basis: stated
   - Authority: operator
   - Evidence:
     - supports: `IDEAS.md` @ `22558ab`
   - AssessedAt: 2026-09-21T08:07:25Z

## Key decisions

D1. This is a standalone project task, not a new charter or an expansion of the coherent-workflow charter.

D2. Canonical identity covers the published source skill directory, not a harness-specific installed variant.

D3. The manifest is the authoritative distributed file set. It records deterministic relative paths, sizes, and SHA-256 digests of raw file bytes; empty directories are irrelevant and symlinks are rejected.

D4. OAK retains `major.minor`. A component version increments for every content change that reaches the distribution channel: major for a breaking contract change, minor for all other changes.

D5. Immutability begins with the first release produced after this objective is completed. Earlier versions remain legacy and unverified.

D6. Canonical skill files are installed unchanged. Harness identity is inferred at runtime or configured outside the skill directory.

D7. Initial portability verification requires a fresh checkout and installation on another operator computer, but not a different operating system.

D8. Installer changes are limited to integrity verification and content-state reporting; registry, channel, and update-management behavior remain out of scope.

D9. SHA-256 establishes content integrity, not authenticity. Signing and provenance are deferred.

D10. The project version covers the whole repository at the release event, not only the distributed component set. Scoping it to skills would require redefinition as new component types arrive.

D11. Component versions remain independent of the project version. A component version tells an operator whether the component they installed changed; the project version names the set released and verified together.

D12. A component's version increments in the commit that changes its distributed content. `main` is OAK's distribution channel, so content reaching `main` is installable and must describe itself.

D13. A project version is assigned at a release tag, which freezes the whole repository and names the component set verified together. Release verification confirms that every component whose content changed since the previous tag carries a version increment; it is not the moment increments are made.

D14. Paused while OAK is experimental and no official release is planned; resume before the first release. Removing the installer's in-directory `HARNESS` rewrite (D6) proceeds separately in the meantime.

## Open questions

_None._
