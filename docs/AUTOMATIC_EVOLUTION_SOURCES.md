# Archived: CloudBox evolution sources

> Archived on 2026-08-20. The Git source synchronization workflow, CLI,
> schema, and validator described below were removed because no remote source
> was configured and every scheduled run failed its secret preflight. This
> file is retained only as historical design context; these commands are no
> longer supported.

CloudBox 6.1 supports manual versioned candidate transfer and token-free Git
source discovery. The public repository contains control logic and schemas;
actual source/destination URLs, credentials, candidates, provenance, and
transfer state remain in ignored local configuration or a user-owned private
Exchange repository.

## Entry phrases

- `從專案提煉優化案例`: first bounded project-history pass.
- `同步優化來源`: incremental Git discovery.
- `匯入優化候選`: import a supported bundle.
- `審核優化候選`, `評估演化候選`, `執行技能演化`, and `發布技能演化`:
  increasingly consequential manual stages.

`採集技能` is intentionally not the primary phrase because it can mean Skill
installation.

## Versioned manual export

On the first interactive export, provide a project-safe export name. It is
stored in ignored `.cloudbox-skills/config.local.json` as `export_project_name` and
reused later. A non-interactive runner must configure it first.

```bash
python3 .agents/skills/developing-skills/assets/export_eval_candidate.py \
  --kind positive --input draft.json --project-name engine-core
```

Archives use `<project>-<host>-<agent>-<UTC YYYYMMDDTHHMMSSZ>-<short ID>.zip`.
`manifest.json` records CloudBox, exporter, bundle, and candidate schema
versions plus payload hashes. Import remains manual:

```bash
python3 scripts/import_eval_candidates.py
```

Unknown or legacy unimported archives move to `imports/unsupported/` without
partial import or deletion. Inspect and delete only by exact bundle ID:

```bash
python3 scripts/manage_unsupported_eval_bundles.py inspect --directory .local/eval-inbox/imports/unsupported --bundle-id ID
python3 scripts/manage_unsupported_eval_bundles.py delete --directory .local/eval-inbox/imports/unsupported --bundle-id ID --confirm ID
```

Already imported Inbox candidates remain available.

## Git source registry

Use logical IDs and environment secret names; never put real URLs in the
public registry:

```json
{"schema_version":"1.0","sources":[{"source_id":"engine-history","url_secret":"EVOLUTION_SOURCE_URL","ref":"refs/heads/main","paths":["docs","src"]}]}
```

```bash
python3 scripts/cloudbox_skills_evolution.py source sync --registry .cloudbox-skills/evolution-sources.private.json --exchange /private/eval-exchange --source-id engine-history
```

No changed commit means `NO_CHANGE` and `model_calls: 0`. Background authority
ends after sanitized private candidate/provenance/checkpoint persistence.
Review, evaluate, apply, and release require separate explicit approval.

Candidate and provenance persist before the checkpoint. Re-running the same
commit is idempotent. Source credentials should be read-only and separate from
Exchange write credentials. Logs expose only logical source IDs and commit
fingerprints. GitHub Actions may wrap the CLI but does not own transitions.
NAS folder watching is deferred to 6.2.
