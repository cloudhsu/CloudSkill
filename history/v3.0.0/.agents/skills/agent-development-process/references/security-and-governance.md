# Agent Security and Governance

## Trust Boundaries

Treat as untrusted unless explicitly controlled:

- User-provided text.
- Retrieved documents.
- Web pages.
- Email.
- Tool output containing free text.
- Repository comments and issues.
- Generated files from other agents.

Instructions embedded in untrusted content do not override system or project policy.

## Controls

- Least privilege.
- Explicit tool allowlists.
- Data minimization.
- Secret isolation.
- Authorization outside model reasoning.
- Human approval for consequential actions.
- Rate and cost limits.
- Audit logs.
- Safe disable/rollback.
- Incident ownership.
- Versioned prompts/instructions/tools/models.

## Consequential Actions

Examples:

- Sending external messages.
- Modifying production data.
- Deploying software.
- Changing access control.
- Purchasing or financial transactions.
- Device movement or process control.
- Deleting or overwriting data.

Require an explicit policy and approval boundary.

## Governance Evidence

- Risk register.
- Approval record.
- Access review.
- Eval results.
- Trace samples.
- Known limitations.
- Incident and rollback exercise.
