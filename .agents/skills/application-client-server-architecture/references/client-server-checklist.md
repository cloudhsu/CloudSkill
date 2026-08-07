# Client/Server Architecture Checklist

## Authority

- Can a client forge price, identity, owner, state, deadline, or permission?
- Does the server independently validate every consequential mutation?
- Is the authoritative state returned after mutation?

## Consistency

- Which writes must commit together?
- Can a request be duplicated?
- Can a response be lost after commit?
- What happens after timeout?
- Can retries repeat a non-idempotent operation?
- Are unique constraints aligned with business invariants?

## History

- Does deleting a master record destroy history?
- Which names, prices, roles, or contact details require snapshots?
- Is history immutable or correctable through compensating events?
- Are time zone and ordering rules explicit?

## API

- Stable error codes.
- Validation limits.
- Authentication and RBAC.
- Concurrency/precondition semantics.
- Pagination and ordering.
- Compatibility/version policy.

## Frontend

- Loading/error/empty/retry states.
- Mobile/narrow layout.
- Touch and keyboard behavior.
- Safe dynamic content.
- Stale-session handling.
- No reliance on hidden controls as authorization.

## Deployment

- Version consistency.
- Migration before traffic.
- Backup and rollback.
- Health checks.
- Logs and secret redaction.
- Supported writer/process topology.
