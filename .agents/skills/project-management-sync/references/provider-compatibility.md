# Provider compatibility

Provider adapters isolate transport and schema drift from reconciliation.

Each adapter declares:

```text
provider, api_family, supported_versions, discovery_endpoint,
capabilities, read_only_fallback, contract_tests, migration_notes
```

At startup, discover the server identity and capabilities. Prefer advertised
resource links, schemas, and allowed operations over hard-coded assumptions.
Unknown versions or missing required capabilities fail closed for writes.
Discovery probes must be non-mutating. If discovery is unavailable, do not
infer compatibility from a URL shape, a successful login, or any 2xx response;
fall back to `read-only`/`manual-review` and record the missing evidence.

## Provider guidance

- Vikunja: keep API v1 and v2 behavior in separate adapters. New integrations
  should target the current supported API; do not make v1 behavior the neutral
  contract.
- OpenProject: treat API v3 resources as hypermedia/capability-driven. Follow
  returned links and forms, and do not assume every installation exposes every
  operation or that a project is the only workspace type.
- Redmine: account for resource-specific REST behavior, JSON/XML selection,
  offset/limit pagination, API-key authentication, and custom fields.

## Version policy

Support a declared version range, test the current and compatibility boundary,
and record the exact provider version in every sync report. A newly discovered
version may be read-only until its adapter and contract tests are reviewed.

An adapter is not ready for writes until its discovery probe, pagination,
identity mapping, status/timestamp mapping, mutation, timeout reconciliation,
and readback contract tests pass for the declared version range.

Do not scatter version branches through the canonical model or reconciliation
engine. Add or replace a provider adapter instead.
