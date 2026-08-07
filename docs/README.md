# Documentation map and ownership

This file defines the authoritative location for each concern.

| Concern | Authoritative document | Other documents may do |
|---|---|---|
| Product overview and navigation | `/README.md` | Link only |
| Installation | `/INSTALL.md` | Provide a short link |
| Always-on architecture guidance | `/AGENTS.md` | Import or summarize only when required by another tool |
| Claude Code adapter | `/CLAUDE.md` | Import `AGENTS.md`; do not restate it |
| Architect identity and capability | `profile/ARCHITECT_PROFILE.md` | Use a short role summary |
| Source evidence | `evidence/BENTO_SYSTEM.md`, `evidence/CLOUDBOX_ENGINE.md` | Cite, do not copy evidence lists |
| Engineering governance overview | `standards/ENGINEERING_GOVERNANCE.md` | Detailed procedures belong inside skills |
| Complex-work plan convention | `/PLANS.md` | Use the template in the agent skill |
| Version history | `/CHANGELOG.md`, Git commits and tags | `history/RELEASES.md` provides an index only |
| External references | `REFERENCES.md` | Link to it |
| Documentation duplication controls | `DOCUMENTATION_AUDIT.md` | Record future audit decisions here |
| Skill workflow | Each `.agents/skills/<name>/SKILL.md` | Supporting detail stays in that skill's references/assets |

## Document classes

- **Normative:** `AGENTS.md`, `PLANS.md`, standards, and skill instructions.
- **Descriptive:** profile and evidence.
- **Operational:** `INSTALL.md`, scripts, release and validation instructions.
- **Historical:** Git commits/tags and `CHANGELOG.md`.

## Duplication rule

Before creating a document:

1. Search for an existing owner of the concern.
2. Update that source when the audience and lifecycle are the same.
3. Create a separate view only when audience, approval status, or lifecycle differs.
4. Link to mutable facts rather than copying them.
5. Record the new owner in this map.
