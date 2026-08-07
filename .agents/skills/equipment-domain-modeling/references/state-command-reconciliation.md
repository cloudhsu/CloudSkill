# State, Command, and Reconciliation

## Core separation

| Artifact | Meaning | Typical lifetime | Authority |
|---|---|---|---|
| Component state | Last known device/readback state | Continuous | Polling/callback/device service |
| Desired state | Software target | Until superseded/reconciled | Command coordinator |
| Command request | One requested operation | One execution attempt | Caller/request record |
| Execution result | Accepted/progress/completed/faulted | Event/history | Equipment service |
| Snapshot | Versioned projection of current state | Point in time | Snapshot producer |

## Writable signal example

A writable signal may contain Actual, Desired, Pending, LastCommandId, LastAttempt, LastWriteTime, LastReadbackTime, Error, and Quality. Include only fields that have defined writers and transition rules.

## Reconciliation rules

- Transport success does not necessarily mean device acceptance or readback equality.
- Actual changes only from the authoritative observation path.
- Pending ends on explicit completion/readback criteria, rejection, timeout policy, supersession, or operator resolution.
- A late readback can reconcile a timed-out attempt.
- Overlapping commands require attempt identity and a replace/queue/reject policy.
- Stale state is distinct from false/off/zero.
