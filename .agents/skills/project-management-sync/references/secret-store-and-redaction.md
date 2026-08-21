# Secret storage and redaction

## Portable boundary

The sync core requests `SecretStore.get(provider, profile)` and never calls a
platform credential API directly.

| Environment | Preferred backend | Configuration rule |
|---|---|---|
| macOS | Keychain | Store only a credential reference in config. |
| Windows | Credential Manager/DPAPI | Use the current user's vault and ACL-protected config. |
| Ubuntu/Linux | Secret Service/libsecret or an approved vault | Do not assume a desktop session; fail closed when unavailable. |
| CI/server | CI secret manager or injected short-lived identity | Do not persist the value in workspace files or command arguments. |

Use `Path.home()` and platform-aware paths. A plaintext file fallback is off by
default and requires explicit manual authorization; it must never be silently
selected because a backend is unavailable.

## Configuration

Portable configuration may contain provider URL, API family/version, project
scope, mode, capability policy, and `credential_ref`. Treat internal URLs and
hostnames as private operational metadata: keep them in ignored local config,
not public skills, Evals, or committed reports.

## Redaction rules

Before logging, exporting an Eval, sending model context, or writing an error:

- redact fields named `token`, `api_key`, `secret`, `password`, `authorization`,
  `cookie`, `private_key`, or equivalent case-insensitive variants;
- redact Bearer/Basic credentials, JWTs, known token prefixes, query-string
  credentials, email addresses, account names, and high-entropy secret-like
  strings;
- never include raw request headers, authentication URLs, or complete provider
  responses;
- retain only provider, API family/version, method, endpoint template, status,
  latency, correlation ID, and a redacted error class;
- replace internal URLs, IPs, usernames, email addresses, project names, remote
  IDs, and actor identities with placeholders in public or reusable evidence;
  use `actor@example.invalid` or another reserved placeholder rather than
  repeating the original value, even when explaining that redaction occurred.
- scan the final serialized output for email/account patterns. Any non-placeholder
  match is a redaction failure and blocks delivery.

Run the redactor before serialization, not after a log line or prompt has already
been emitted. A redaction failure is a stop condition.
