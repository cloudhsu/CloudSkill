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

### Convergent Failure Across Independent Implementations

When two or more independently-built implementations of the same
capability (different libraries, different platform mechanisms/backends,
different vendors) exhibit the identical symptom, while each one's own
API reports success at every layer it exposes, treat that convergence
itself as evidence pointing at something the implementations share --
the host, the session, a common upstream dependency, a common resource or
config file -- rather than continuing to separately hypothesize about
each implementation in turn. Two unrelated implementations independently
containing the same bug with the same symptom is a much lower-probability
explanation than one shared cause underneath both.

Corroborate this with a live control: run an unrelated, already-trusted
consumer of the same shared resource (a different application, a
previously-working build, a different device/session) and observe its
result directly, before spending further effort hypothesizing about the
component under test. A control that also fails narrows the search to the
shared layer; a control that succeeds narrows it to something specific to
the current session/instance rather than the host as a whole.

Counterexample: convergence across implementations does not, by itself,
prove environment -- a bug in a shared upstream dependency, a shared
resource file, or shared configuration that both implementations read
could produce the identical symptom just as easily. Only close the
attribution once the specific shared mechanism is actually identified, or
once a differently-configured/fresh instance of the environment is
confirmed to work while this one does not.

### Verifying Async Completion, Not the Synchronous Call That Started It

A log line confirming a synchronous call returned proves the call
returned -- nothing about a deferred, async, or eventually-consistent
operation the call merely started. Do not report an async-backed
operation as confirmed successful without independently verifying the
completion signal that specific mechanism actually exposes (a callback,
an event, a terminal status, a change to observable state) -- and confirm
it fired, with a success payload, not merely that it was registered.

If no completion signal is currently observed (neither success nor
failure), that is not evidence of success -- add tracing at the actual
completion point before concluding anything about the operation's
outcome.

## Shared-Consumer Before/After State

When a slice replaces, consolidates, or changes the behavior of a component
used by more than one consumer -- multiple call sites, multiple platform
adapters, multiple subclasses of a shared base, multiple client
integrations, multiple tenants -- record each consumer's state immediately
before and immediately after the change, in a table, not only in prose.

Prose summarizing "confirmed working" for some consumers reads the same
whether every consumer improved or one silently regressed while others
improved -- the asymmetric outcome is invisible until someone notices it
later, often from memory rather than from the verification record itself,
after it has already reached whoever depends on the affected consumer. A
table with one row per consumer and explicit before/after columns makes
that outcome visually impossible to miss at write time.

Minimum table shape:

| Consumer | State before | State after | Evidence |
| --- | --- | --- | --- |

- List every consumer known to depend on the replaced component, not only
  the ones exercised by the immediate test. A consumer with no test
  coverage still gets a row, marked accordingly (untested, not silently
  omitted).
- "State" is whatever the consumer's contract actually promises -- output
  correctness, a specific response shape, a performance bound, an
  observable side effect -- not merely "ran without throwing."
- Build the table at the moment verification is written, as part of Step 7
  (Verify) and Step 8 (Handoff), not reconstructed afterward once a
  regression is reported. Reconstructing it later from memory or logs is
  strictly worse: slower, and it only happens after the regression has
  already shipped to whoever depends on the affected consumer.
- This applies to platform adapters as one case among several -- the same
  requirement applies to a shared service replaced under multiple call
  sites, a base class behavior changed under multiple subclasses, or an
  interface implementation swapped under multiple integrations.

Counterexample: a slice with exactly one consumer (no fan-out) does not
need this table -- a single before/after state pair in prose is sufficient.
The table earns its cost specifically when a shared component serves more
than one consumer, because that is where an asymmetric regression can hide
behind prose about the consumers that improved.

## Delivery

- Focused tests pass.
- Regression passes.
- Build/package verified when affected.
- Documentation synchronized.
- Diff contains no unrelated generated artifact.
- Unrun tests are explicitly listed.
- When the slice touches a component used by more than one consumer: a
  shared-consumer before/after state table exists (see above), not only
  prose confirmation.
