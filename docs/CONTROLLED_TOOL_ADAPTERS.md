# Controlled tool adapters

CloudBox 6.3 separates agent judgment from bounded external execution. Skills
decide why a capability is appropriate and which evidence is required. The
lifecycle owner controls the plan and gates. A local broker validates and
executes one registered CLI capability. The external system remains
authoritative for side effects.

## Shipped 6.3 slice

- Transport-neutral invocation, result, registry, and durable-action contracts.
- A local CLI broker that denies raw commands, validates authority and paths,
  verifies adapter provenance, resolves secret references through the host,
  bounds output, and persists action state.
- `git.inspect`, `git.fetch`, and `git.import_bundle` capabilities.
- Interruption state and `UNCERTAIN` reconciliation rules owned by the adaptive
  lifecycle process.
- Temporary-repository fixtures; no live GitHub mutation is claimed.

MCP, GitHub PR/merge/tag/Release automation, NAS polling, and unrestricted shell
remain deferred.

## Validate without external side effects

```bash
python3 scripts/validate_tool_adapter_contract.py
python3 scripts/validate_tool_action_recovery.py
python3 scripts/validate_tool_execution_broker.py
python3 scripts/validate_git_tool_adapter.py
```

The Git validator creates only temporary local repositories. It does not use a
configured GitHub remote.

## Invoke a registered capability

Create a contract-valid invocation JSON outside tracked source, then run:

```bash
python3 scripts/cloudskill_evolution.py tool invoke \
  --registry config/tool-adapters.json \
  --invocation .local/tool-actions/invocation.json \
  --state-dir .local/tool-actions/state \
  --root-ref REPOSITORY_ROOT=/approved/repository/parent \
  --authority git.fetch
```

Root references are operator/host policy. An invocation contains a path relative
to that root and cannot select an arbitrary working directory or executable.
Read-only `git.inspect` does not need an authority flag. Mutating operations
need the exact authority declared by the registry.

If an adapter later requires a private endpoint or token, the registry stores
only a reference such as `SOURCE_REMOTE_URL`. Bind it to an environment variable
at invocation time:

```bash
python3 scripts/cloudskill_evolution.py tool invoke \
  ... \
  --secret-ref SOURCE_REMOTE_URL=CLOUDBOX_SOURCE_REMOTE
```

The environment variable value is not written to the invocation, registry,
action state, or model-visible result. Do not put a literal URL or credential
after `--secret-ref`.

## Interruption and recovery

Every action is stored under the requested state directory. `SUCCEEDED` and
`FAILED` are evidenced terminal observations. `BLOCKED` preserves missing
authority or prerequisites. `UNCERTAIN` means timeout or transport evidence
cannot prove external completion; inspect and reconcile the external system
before authorizing another attempt. Do not delete the checkpoint and repeat the
command.

The lifecycle owner reads the plan revision and action checkpoint, preserves
completed evidence, and chooses reconciliation, re-plan, architecture re-entry,
or stop. The adapter cannot make that decision.

## Manual import remains supported

The existing operator path is unchanged:

```bash
python3 scripts/import_eval_candidates.py --eval-inbox .local/eval-inbox
```

Use it when adapter automation is unavailable. Unsupported legacy bundles
remain retained under the existing unsupported queue; the controlled adapter
does not silently migrate or delete them.

## Registering another adapter

Add a narrow entry to `config/tool-adapters.json`, use a closed argument schema,
declare risk/authority/retry/reconciliation/output limits, pin the repository
script SHA-256, and add RED/GREEN fixtures. Run the complete suite. Do not add a
generic command/argv capability or let another consumer hand-copy the registry.
