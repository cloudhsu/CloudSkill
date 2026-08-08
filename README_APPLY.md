# CloudSkill conversation-optimized overlay

This package is a **review candidate** for the current `cloudhsu/CloudSkill` repository version 5.5.2.

It does not pretend that all historical conversations were available. The changes were derived from:

- the current conversation and available durable context,
- the connected GitHub repository,
- recurring generalized corrections around skill routing, command/readback semantics, version-scoped metrics, audience-specific documents, client/server systems, native/Qt systems, equipment architecture, and AI-agent/repository boundaries.

## What changes

- Strengthens `using-cloudskill` as a bilingual, conversation-aware top-level router.
- Adds explicit routing cues for recurring Chinese engineering questions.
- Extends `developing-skills` with a truthful historical-interaction mining workflow.
- Adds sanitized behavior cases for routing and read-only GitHub fallback.
- Adds a reusable reference for conversation-derived optimization.
- Refreshes `SKILL_MANIFEST.json` descriptions and file counts.

The official repository `VERSION` and `CHANGELOG.md` are intentionally unchanged. This is not labeled as a released 5.6.0 until behavior evaluations and repository checks are reviewed.

## Apply on this Mac

```bash
cd <extracted-package>
chmod +x apply_to_local.sh build_full_package.sh
./apply_to_local.sh /Users/cloudhsu/projects/cloudskill/CloudSkill
```

The script:

1. verifies the target is a CloudSkill Git clone,
2. backs up every overwritten file,
3. copies the overlay while preserving repository paths,
4. runs `python3 scripts/run_all_checks.py`,
5. prints the changed files and review commands.

## Build a complete upload ZIP

After the overlay passes review:

```bash
./build_full_package.sh /Users/cloudhsu/projects/cloudskill/CloudSkill
```

The default output is:

```text
/Users/cloudhsu/projects/cloudskill/CloudSkill-conversation-optimized-full.zip
```

This full ZIP excludes `.git`, local Eval data, backups, caches, and macOS metadata.

## Roll back

The apply script prints the exact backup directory. Restore it with:

```bash
rsync -a "<backup-directory>/" /Users/cloudhsu/projects/cloudskill/CloudSkill/
```

You can also discard all local changes with Git only when you are certain no unrelated work must be preserved:

```bash
cd /Users/cloudhsu/projects/cloudskill/CloudSkill
git restore .
git clean -fd
```
