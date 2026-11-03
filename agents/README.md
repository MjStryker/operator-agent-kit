# Reusable specialists

These Markdown profiles define expertise, not executable workflows or native agent
registrations. Read [common.md](common.md) and the selected profile; supply a mission,
scope, permissions and output. The invoking workflow owns orchestration and delivery.
Profiles work for audits, investigations, planning and implementation.

- [QA](qa.md): observable correctness and regression evidence.
- [Security](security.md): trust boundaries, authorization and data exposure.
- [Senior Fullstack](fullstack.md): cross-layer contracts and affected consumers.
- [UI/UX React](ui-ux-react.md): interaction, accessibility and UI states.
- [DevOps](devops.md): delivery, configuration and operational recovery.

Profile 0.3 retains historical IDs from 0.2 as coverage families; workflows derive
bounded obligations before investigation. Tools are optional and discovered per
project; common defines their execution/evidence rules. Audit policies and output
are owned by `skills/audit/SKILL.md`, not these reusable profiles.

`scripts/install-skills.sh` copies these canonical files unchanged to the audit
bundle's `references/specialists/`. Other workflows may read that bundle. Edit source
files here; native registration remains a harness-specific adapter outside OAK.
