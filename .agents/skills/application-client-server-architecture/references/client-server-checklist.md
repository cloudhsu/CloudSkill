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

## Multi-endpoint / inter-process transport

Apply when several long-lived processes (front end, coordinator, worker or
device-facing services) talk over a network, not only one client to one server.
Keep this layer generic: transport acknowledgement never stands in for the
owning domain's completion or readback semantics.

- Endpoint and session ownership: who listens, who dials, who owns each
  session's identity and lifecycle (startup, handshake, version negotiation,
  authentication, health).
- Duplicate session: one live session per endpoint identity; state whether a
  second connect is rejected or supersedes the first, and how the stale
  session is fenced so its late messages cannot mutate state.
- Reconnect: define the states from disconnected to ready (resync or replay
  before new work) and what happens to in-flight requests; never leave it
  implicit.
- Bounded queues: every inbound/outbound queue has a size, an overflow policy
  (reject, drop-oldest, or back-pressure the sender), and a slow-peer rule so
  one slow endpoint cannot stall the others.
