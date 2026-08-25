# ExecPlan: Public/private plugin cache surface separation

## Goal and User-Visible Outcome

When the private repository is registered as a marketplace, installing
`cloudbox-skills` must cache only core/public Skills. Installing
`cloudbox-skills-private` must cache only non-core/private Skills. A user must
not need to trust the plugin manifest's declared Skill list to keep private
files out of the public package.

## Scope and Non-Goals

In scope:

- marketplace source paths and generated plugin package projections;
- public/private package-surface validation and smoke checks;
- public export compatibility;
- installation documentation and release handoff evidence.

Non-goals:

- changing Skill content, IDs, tiers, or routing;
- changing standalone `install.sh`/`install.ps1` behavior;
- deleting or repairing already-installed Claude host caches in this slice;
- publishing, tagging, or changing version numbers.

## Current-System Reconstruction

- `.agents/skills/` is the canonical source for all Skills.
- The private marketplace currently points `cloudbox-skills` at `./`, so a
  plugin manager copies the whole private repository root into the public
  cache.
- `private-plugin/` and `private-gemini-plugin/` are already private
  projections; `private-plugin/codex-skills/` is a regular-file projection
  for Codex.
- `scripts/export_public_bundle.py` filters a public checkout correctly, but
  the private local marketplace installation does not run that export.

## Constraints and Assumptions

- Plugin managers copy package source directories and do not apply a file
  allowlist derived from the manifest.
- Codex must receive regular files; generated projections must not depend on
  symlink dereferencing.
- The public mirror keeps its existing root package shape after export, so
  export rewrites its marketplace source from `./public-plugin` to `./`.

## Architecture / Approach

Add `public-plugin/` as a generated, regular-file core-only package containing
the Claude/Codex manifests, core Skills, and referenced branding assets.
Change the private marketplace's public entry to `./public-plugin`; keep the
private entry at `./private-plugin`. Extend validators, export filtering, and
smoke tests to assert both package surfaces.

## Milestones

- [x] Add and generate the core-only public projection.
- [x] Point the private marketplace at the public projection and update
  export/validation logic.
- [x] Update install documentation and handoff evidence.
- [x] Run projection checks, export dry-run, packaging validators, smoke tests,
  and diff checks.

## Verification and Acceptance

- `public-plugin/skills` names equal exactly the core tier and hashes match
  `.agents/skills/<core>`.
- `private-plugin/codex-skills` and `private-gemini-plugin/skills` names equal
  exactly the non-core tiers.
- Private marketplace source paths are `./public-plugin` and
  `./private-plugin`.
- Public export contains neither `public-plugin/` nor any private path and
  rewrites the public marketplace source to `./`.
- Existing deterministic checks and the install smoke test pass.

## Risks and Rollback

The main risk is stale generated package content. `--check` validation and the
full suite detect this before release. Rollback is to restore the marketplace
public source to `./` and remove the generated projection, without changing
canonical Skills or private projections.

## Progress Log

- 2026-08-25: confirmed the defect in both installed caches and reproduced it
  from the private marketplace root source; no source files were changed.
- 2026-08-25: generated `public-plugin/` as a regular-file core-only
  projection and changed both Claude/Codex marketplace manifests to point to
  it. Extended export, validation, smoke, documentation, and architecture-map
  coverage.
- 2026-08-25: projection checks, private/Gemini projection checks, plugin and
  pack validators, smoke installation, public export dry-run, and the full
  `run_all_checks.py` suite passed before any host-side reinstall was
  requested.
- 2026-08-25: after the explicit Codex reinstall request, removed the old
  Codex `7.7.0` public/private plugin entries and installed `7.7.1`. Host
  verification confirmed 21 public core Skill directories, no private-named
  paths in the public cache, and 21 private `codex-skills` directories.

## Decision Log

- 2026-08-25: use a generated public plugin projection instead of relying on
  manifest declaration filtering, because the observed cache contains files
  not declared by the manifest.

## Discoveries and Deviations

- The standalone installers are not part of the defect: they copy only the
  canonical Skill tree to standalone destinations.

## Final Outcome and Remaining Work

The private marketplace now exposes a physically separate core-only
`public-plugin/` package and a private-only `private-plugin/` package. The
public export keeps its existing root package shape by rewriting the public
source path during export. Verification passed for both package boundaries.

Remaining work is release/operation work outside this slice: review and merge
the change, publish or otherwise make the corrected marketplace revision
available, and later decide whether Claude host state should be refreshed.
Codex `7.7.0` cache entries were replaced by the verified `7.7.1` install;
Claude host caches and standalone copies were intentionally left untouched.

Follow-up verification at `7.7.2` reinstalled public/private plugins on both
Codex and Claude. Codex also produced and validated an Eval-export ZIP from an
isolated temporary project using only the exporter bundled in its installed
private Skill cache. Claude execution was not run by operator request.
