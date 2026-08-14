# Public Core and private Evolution Pack — deferred future direction

Status: direction retained, execution explicitly deferred. Continue improving
CloudBox as one repository/package. Do not split repositories, create a private
remote, move Skills, or change packaging until the user decides the product is
ready for marketing or broader external promotion and explicitly resumes this
work.

The current public repository is acceptable during the capability-maturation
period because active marketing is not in scope. This document preserves the
future design so the split can be evaluated before a later promotion campaign;
it is not a current roadmap commitment.

## Resume trigger

Reopen this design only when both conditions hold:

1. CloudBox is considered sufficiently complete and stable for deliberate
   marketing or broader external distribution.
2. The user explicitly authorizes the public/private packaging work.

**Refined by the user, 2026-08-14**: condition 1's "sufficiently complete and
stable" is validated through real product development pressure first — using
an actual product build (e.g. the CloudBox engine revival work, or the
user's own day-job engineering work) as the stress test for whether the
software-engineering Skills hold up — not just an internal review pass. Only
once that validation round and the current skill-optimization work reach a
natural stopping point does the public repository get finalized at that
state and the split actually executes.

**Category boundary, restated more concretely by the user, 2026-08-14**: the
"ordinary engineering" Skills in Core vs. "evolution" Skills in the Pack
below already matches what the user asked for, with one addition — the
planned `cloudbox-agent-*` multi-role work (see
`cloudbox-skills-private-only` memory / `CLOUDBOX_SKILLS_AGENT_HANDOFF.md`)
is explicitly grouped with the Evolution Pack (private), not Core, alongside
Skill development / mining / evolution. So: **Core = software-development
Skills only. Evolution Pack = Skill self-evolution/mining machinery AND any
multi-role agent-persona work**, not just the mining tooling alone.

**Ongoing update model once split, restated by the user, 2026-08-14**: after
the split executes, updates continue on a **dual-track** basis going
forward — a change to a Core-owned (software-development) Skill gets
published to both Core and the private full repository in the same pass
(the `teach-while-building` dual-publish pattern already in use, generalized
to the whole Core category instead of one named exception); a change to an
Evolution-Pack-owned Skill (mining/evolution machinery, multi-role personas)
stays private-only. This is still deferred execution per the Status line
above — recorded here so the ongoing-update shape is designed before the
split happens, not decided ad hoc when it does.

At that time, reassess the repository content, licensing, install experience,
product positioning, support boundary, and which evolution capabilities still
need to remain private. Do not assume today's proposed ownership map remains
correct after further evolution.

## Target products

- **CloudBox Core** stays public and contains Skills for ordinary engineering:
  analysis, architecture, design, implementation, review, test, deployment,
  quality, documents, and lifecycle use.
- **CloudBox Evolution Pack** is a separate private local repository/package.
  It contains Skill development, interaction/project mining, Eval Inbox and
  promotion, source synchronization, multi-model evolution, and private
  evolution operations.

Core must not depend on the Evolution Pack. The private pack may declare a
compatible Core version range and reuse Core contracts through stable public
interfaces. Public artifacts are assembled from an allowlist and scanned for
private paths, endpoints, credentials, candidates, provenance, and
evolution-only files; hiding an entry behind a flag is not sufficient.

## Local-first Git and GitHub sequence

The following sequence is dormant until the resume trigger above is met.

1. Define the file/Skill/contract ownership map and characterize current
   install, Eval, release, and manual import behavior.
2. Create a sibling local Git repository for the Evolution Pack with no remote.
   Move content incrementally while compatibility shims and rollback remain.
3. Keep the existing public GitHub repository as Core; verify its history and
   release artifact contain no newly private material.
4. Test both packages locally and test Core by itself.
5. Only in a later explicitly authorized operation, create and attach a private
   GitHub remote for the Evolution Pack. Do not push it during the initial
   split.

Avoid rewriting the public repository's existing history merely to separate
generalized Skill logic; perform a history purge only if a dedicated secret or
privacy scan finds material that actually requires removal.

## Private local installation

The Evolution Pack must remain installable before any private GitHub remote
exists. Its installer accepts an explicit local repository path and installs
to Codex/Claude user or project scope using the same canonical Skill layout as
Core. The install record stores package ID, pack version, compatible Core
range, source kind (`local_path` initially), normalized source path, installed
Skill IDs, and file hashes. It stores no credentials.

Required operations:

- install/update from a local path;
- verify Core compatibility and detect missing/wrong Pack versions;
- list which private Skills are active without exposing their content publicly;
- remove only Pack-owned files while leaving Core intact;
- refuse ambiguous ownership or collisions with Core Skill IDs;
- later switch the source to private Git over SSH/token secret reference
  without changing installed Skill IDs or losing local configuration;
- preserve the existing manual Eval import/export path inside the private Pack.

The installed private Skills are visible to the local agent host because that
is necessary for routing, but they are absent from public plugin manifests,
public release archives, and the public repository. Project-specific private
configuration and captured data remain ignored and outside both distributable
packages.

## Release and CI boundary

Core and Evolution Pack have independent versions, tags, manifests, CI, and
release evidence. A compatibility matrix connects them. Core CI must pass with
the Pack absent. Private CI may install a pinned Core release and run combined
integration tests. Neither pipeline may log or copy private repository URLs,
credentials, raw transcripts, candidate payloads, or private source paths into
public artifacts.

Before implementation, decide the sibling directory names, private package ID,
which generalized Eval runtime contracts remain public, and which evolution
Skills move. Those ownership decisions require a repository-level architecture
review because they change routing, installation, compatibility, and release
authority.
