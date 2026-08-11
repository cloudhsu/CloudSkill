# CloudBox Manual Eval Exchange Design

## Decision

CloudBox keeps one manual Eval exchange workflow and removes the unreleased 6.3
controlled execution experiment from the product surface. Operators export
versioned ZIP bundles, place any number directly in the configured Eval Inbox
`imports/` directory, and ask CloudBox to import them. Import is deterministic:
it does not call a model, modify formal Evals or Skills, commit, push, or release.

## Fixed filename contract

Every supported bundle filename is exactly:

```text
<project>-<host>-<agent>-<YYYYMMDDTHHMMSSZ>-<bundle-id8>.zip
```

- `host` is `codex` or `claude`.
- `project` and `agent` are safe normalized components stored in the project's
  ignored `.cloudskill/config.local.json` as `export_project_name` and
  `export_agent_name`.
- The timestamp is UTC.
- `bundle-id8` is the first eight characters of the manifest's 32-hex bundle ID.
- The importer reconstructs the expected filename from `manifest.json`; any
  mismatch is unsupported and is never partially imported.
- The manifest remains authoritative for CloudBox/exporter/candidate/bundle
  versions and payload hashes.

## Manual batch flow

1. `匯出優化案例` creates one sanitized candidate bundle with the fixed name.
2. The operator copies one or more ZIPs directly into
   `.local/eval-inbox/imports/` or the configured private Inbox equivalent.
3. `匯入優化案例` runs `scripts/import_eval_candidates.py` once over the batch.
4. Supported valid payloads are deduplicated and routed to `candidates/`,
   `manual-review/`, or `rejected/`.
5. Supported processed source ZIPs move to `imports/processed/`; unsupported
   version/name/manifest bundles move to `imports/unsupported/`; malformed or
   unsafe archives remain in `imports/` with an explicit report and are never
   deleted automatically.
6. Formal Eval/Skill evolution requires a later explicit review instruction.

## Automation withdrawal

Remove the unreleased registry, broker, action store, adapter CLI, tool schemas,
controlled-tool Behavior cases, lifecycle routing, validators, and product docs.
Preserve the architectural lessons and review fault matrix only in
`docs/future/CONTROLLED_EXTERNAL_TOOL_ADAPTERS.md`. The existing manual importer,
unsupported-bundle lifecycle, Git evolution-source synchronization, and 6.2
release remain intact.

Because the controlled execution experiment was never released, there is no
runtime migration. Local experimental action files remain ignored local data and
may be manually deleted; CloudBox does not discover or modify them.

## Verification

- RED: a supported manifest under a renamed ZIP is currently accepted.
- GREEN: exact filename match is required; mismatched bundles become unsupported.
- Exporter parity tests cover project/host/agent/time/ID naming and persisted
  project/agent aliases.
- Batch tests cover multiple valid ZIPs, duplicates, mixed supported/unsupported,
  malformed retention, no partial import, and zero model calls.
- The complete deterministic suite passes twice after automation withdrawal.
- A fresh exact-tip review checks that no executable controlled-tool surface or
  stale documentation remains.
