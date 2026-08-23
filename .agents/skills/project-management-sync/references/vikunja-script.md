# Vikunja helper contract

The optional `scripts/vikunja_sync.py` helper is the mechanical implementation
of this Skill's synchronization gates. It is intentionally a small Vikunja
adapter, not a replacement for the provider-neutral reconciliation model.

## Plan input

The local plan is authoritative and must contain:

```json
{
  "source_system": "example-backlog",
  "target_provider": "vikunja",
  "target_profile": "local",
  "agent": "Codex 5.6 Luna xhigh",
  "project": {
    "title": "example-project",
    "description": "Project-level scope and ownership."
  },
  "tasks": [
    {
      "source_key": "EXAMPLE-1",
      "title": "A concrete task",
      "problem_background": "Why this task exists.",
      "approach": "The smallest safe approach.",
      "acceptance_criteria": ["A checkable result."],
      "source": "Repository path, issue, or decision record.",
      "status": "planned"
    }
  ]
}
```

Every task description is rendered with the fixed sections `標題`, `問題/背景`,
`建議處理方式`, `Acceptance Criteria`, and `Source`. A dated append-only
progress block is added and always contains `Agent: <agent>`. The helper
rejects plans without the agent field; it never infers an agent from git config,
the logged-in account, or the host process.

## Modes and safety boundary

```text
audit      discover and enumerate; never mutate
dry-run    produce no-op/create/update/ambiguous/blocked counts; never mutate
apply      create only after discovery, exact-scope enumeration, and capability checks
reconcile  inspect journaled unknown mutations; never retry automatically
```

The helper first probes `/api/v1/info` as a service-existence check. If the
service is missing or unavailable it stops before enumeration and reports
`BLOCKED`; it does not mistake a login or URL shape for service availability.
It then requires a supported Vikunja v2 server, reads `OPTIONS` capability headers, and handles collection pagination. It selects
the advertised project/task creation method (`PUT` on the current server,
`POST` only when explicitly advertised). It does not assume that a 2xx response
is final: every create is read back and the created title plus agent marker are
verified.

Exact title matching is only a fallback after the complete target scope is
listed. Zero matches may plan a create; one match is a no-op; multiple matches
are ambiguous and block writes. The helper does not perform ordinary updates or
deletes. This preserves provider-owned work logs and the append-only human
record. A transport timeout is journaled as `unknown`; run `reconcile` before
considering a retry.

Credentials are resolved from macOS Keychain by default (`--keychain-service`
and `--keychain-account`) or, explicitly for CI, from a secret-manager-injected
environment variable (`--credential-source ci-env`). A token is never accepted
as an argument or stored in the plan, mapping, journal, or output.

Example local invocation:

```bash
python3 .agents/skills/project-management-sync/scripts/vikunja_sync.py \
  path/to/plan.json --mode dry-run \
  --base-url "$VIKUNJA_BASE_URL" \
  --keychain-account "$VIKUNJA_KEYCHAIN_ACCOUNT"
```

Keep mapping and journal files in an ignored local directory. They are machine
identity caches and recovery evidence, not source-of-truth plan data.

The reconciliation core is provider-neutral at the adapter boundary. The first
adapter is Vikunja; OpenProject and Redmine can be added later by implementing
the same discovery, enumeration, mutation, and readback contract with their own
version/capability rules. Until an adapter and its contract tests exist, an
unknown provider is rejected before transport and no write is attempted.
