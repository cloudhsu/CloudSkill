# Refactoring Evidence Checklist

## Contract

- Public methods unchanged or versioned.
- API routes/status/error codes preserved.
- Return shape preserved.
- Ordering semantics preserved.
- Authentication/RBAC preserved.

## Data

- Transaction invariants preserved.
- Historical snapshots preserved.
- Migration idempotent.
- Integrity check passes.
- Source database remains unchanged during compatibility tests.
- Future-version refusal is zero-write.

## Failure

- Validation failure performs no write.
- Mid-transaction failure rolls back.
- Persistence failure restores or blocks safely.
- Duplicate/retry behavior is defined.
- Audit/event writes follow the required order.

## Environment vs. Defect Attribution

Before treating an independent run on a differently-configured environment
(a CI pipeline on another OS, a colleague's machine) as corroborating
evidence for "this local failure is environment, not defect," classify the
failure first:

- **Environment-agnostic** (a missing generic dependency, general
  timing/flakiness): an independent run on a differently-configured
  environment is valid corroborating evidence — use it.
- **Mechanism-specific** (the failure path is genuinely tied to one
  environment's distinct underlying mechanism — for example POSIX
  permission bits vs. Windows ACLs, which are structurally different
  systems): a passing run on a DIFFERENT environment proves nothing, because
  that environment may not even exercise the mechanism in question. Do not
  cite it as evidence. Reproduce under the SAME environment instead — a
  clean VM/container on that OS, a colleague's machine running the same OS,
  or a same-OS CI runner if one exists.

Report the environment-vs-defect attribution as confirmed only once the
correctly-matched independent run (same environment for mechanism-specific
failures, either environment for agnostic ones) has actually executed and
its result observed — not from inspecting the failing code path alone, and
not from a CI run that predates the change under review.

Counterexample: if no independent, correctly-matched execution path exists
for the failing check, reasoning-based attribution is the best available
evidence and should be reported as such, explicitly flagged as unconfirmed
by an independent run.

## Delivery

- Focused tests pass.
- Regression passes.
- Build/package verified when affected.
- Documentation synchronized.
- Diff contains no unrelated generated artifact.
- Unrun tests are explicitly listed.
