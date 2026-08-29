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

## Disabled Assignment on the Return Path

Before considering a function's implementation complete, grep it for a
commented-out line that assigns to (or reads from) the function's own return
value or output parameter -- a disabled assignment on the return path
silently produces a default/empty result on every call, with no exception
and no error. Do not trust a logging wrapper's "succeed"/"complete" message
as evidence a call produced a real result when that logging only measures
the call returning without throwing -- verify the actual returned/output
value is non-default on at least one real invocation. Do not leave a
commented-out assignment on the result path of a function that is otherwise
wired up and called in production without a companion issue/TODO explaining
why it is disabled.

## Configured Field Shadowed by a Hardcoded Literal

When a class exposes a configurable field intended to control a downstream
call, grep every call site that performs the actual operation the field is
supposed to influence, and confirm it reads the field rather than a
hardcoded literal -- especially one matching the field's default value,
which makes the bug invisible until the field is changed away from that
default. When a user-facing "change X" feature appears to have no effect,
check first whether the value is correctly stored but never actually read
at the point of use, rather than assuming the storage or UI layer is broken.

## A Rate/Metric Formula Must Actually Use Its Time Term

When a formula is supposed to compute a rate or an average over a time
window (frames/sec, requests/sec, throughput), verify algebraically or
empirically that the formula's result actually changes when the
elapsed-time input changes -- a formula with multiple terms and
coefficients can still algebraically reduce to a constant or to one of its
inputs alone, disguising the fact that it never uses the time measurement
it claims to depend on. When replacing a formula that looked simplistically
wrong (a bare count with no time normalization), confirm the replacement
actually incorporates the time measurement already available in the
surrounding code, rather than trusting that a more complex-looking
expression is automatically more correct.

## Paired/Symmetric Computation With One Side Un-Updated

When a code block that computes one side of a paired/symmetric calculation
(left/right, before/after, source/target) is duplicated to compute the
other side, verify by direct read that every input reference inside the
duplicated block was updated to the second side's own source -- not only
that the output variable was renamed. A renamed output with an un-updated
input compiles and runs cleanly while silently combining two values from
the same side. Confirm each side's inputs actually trace back to a
distinct, correct source by reading the variable's assignment, not by
trusting the variable's name. When a loop consumes two independently-
populated collections that are supposed to stay in lockstep, check the
loop bound accounts for a possible length mismatch between them rather
than assuming both are always the same size, and verify an accumulating
output container is cleared at the start of each call unless
accumulation-across-calls is the explicit, documented intent.

## Copy-Pasted Sibling Branch in an Enum/Case Dispatch

When reviewing or writing an enum-to-resource dispatch table (a switch or
if-else chain mapping a discrete value to a resource/config identifier),
verify each branch's returned/selected value actually corresponds to that
branch's own case label, not a copy-pasted neighbor's -- the function can
still compile, still return a non-empty, valid-looking value, and produce
no crash for any input, while silently loading the wrong resource for
specific cases. Test each enum value's dispatch outcome individually
(assert the actual returned identifier per case) rather than only
confirming the function returns some non-null/non-error value for a
sample input.

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

### Development-Tool Presentation State Is Not App State

A visual symptom (rotated/mirrored layout, wrong colors, misplaced UI) can
originate from a simulator, emulator, or dev-tool presentation setting that
merely displays the app differently, rather than from the app's own logic.
Before writing a source-level fix for a visual symptom, inspect the actual
live runtime state directly -- attach a debugger and read the real object
state the app is producing (e.g. the actual screen-bounds/orientation
value), or use an equivalent direct-introspection mechanism -- rather than
inferring the cause from the rendered appearance alone. If the live state
is already correct, the defect is in the tool's presentation layer, not the
app; revert any source change made before this was known instead of
layering more app-side changes on top of a correctly-behaving app.

Counterexample: a genuine layout defect can look identical to a
presentation-setting artifact from a screenshot alone -- this check does
not replace fixing a real defect once live state inspection confirms the
app's own state is actually wrong.

### Perceptual Outcomes Require a Perceptual Check

Some outcomes (audible sound, visible rendering, haptic feedback) cannot
be confirmed by API return values, logs, or callbacks alone -- every layer
a mechanism exposes can report success while the actual perceptual result
never occurs, because the gap is in a layer the mechanism does not
instrument. Do not report such an outcome as working from log/API
evidence alone; it requires a human or sensor observation of the actual
perceptual result.

When that observation channel is not currently available (the person who
can confirm it is unavailable, or no sensor exists), stop making further
speculative source changes rather than guessing at additional fixes with
no way to confirm any of them worked. Report the current best-supported
theory explicitly as unconfirmed, and hand off the cheapest untried
diagnostic steps for when the observation channel is available again.

### A Synchronous Launch With No Error Is Not Success

After a build succeeds and a process launches without crashing or logging
an error, independently verify the actual expected observable effect of
that launch (e.g. a window/surface was created, a specific state was
reached) via an external inspection mechanism, rather than treating "no
crash" as evidence of correct behavior. This is distinct from the async-
completion and perceptual-outcome sections above: a synchronous lifecycle
bootstrap can run with zero errors while silently failing to reach its
expected state, because the API it calls has its own contract (e.g. nib/
storyboard delegate wiring) that a naive port from a different platform's
equivalent API does not satisfy. Report the verification step actually
taken (e.g. "confirmed window count = 1 via an external inspection tool"),
not a vaguer claim like "process is running."

### Known Defect as an Attribution Control

When a verification pass covers a component that also carries a separate,
already-known, unrelated open defect, deliberately exercise that known
defect's scenario within the same pass rather than avoiding or ignoring it,
and record its observed status explicitly (e.g. "observed / tracked,
pre-existing, not introduced by this change"). This disambiguates a new
symptom from a pre-existing one for a later reader, who otherwise has to
reconstruct the distinction from memory or a separate issue tracker. This
is distinct from -- and not a substitute for -- "Known-Issue Record Closure"
below: that governs when a record may be *closed*; this governs keeping a
live regression check's evidence unambiguous while the issue stays open.

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

## Transitive-Consumer Discovery Before a Split

A direct search for the moved item's own name only finds consumers that
reference it *directly*. It misses a consumer that reaches the moved item
through another file: a validator that imports another script, which
imports another script, which hardcodes a path to the thing you moved,
three hops away. That consumer never matches a grep for the moved name --
it matches a grep for the name of whatever it directly imports, which has
no obvious connection to your change.

Before finalizing a split (a skill, a module, a shared file, a config
entry), trace the dependency graph outward from the moved item, not just
the literal string:

- Grep for the moved item's own name (the obvious first pass), *then*
  grep for the names of anything the moved item's own consumers import or
  hardcode paths to, one more hop out. Repeat until a pass finds nothing
  new.
- Distinguish "no result" from "not searched" -- a clean grep for the
  moved name proves nothing about hop-two or hop-three consumers unless
  they were searched for too.
- A test suite that runs entirely inside the source repository proves the
  source repository is internally consistent. It does not prove a split
  is complete when part of what makes a change "complete" is how the
  result behaves once consumed downstream -- packaged, exported,
  installed, or otherwise handed to something outside the repo. If such a
  downstream consumption step exists, run it for real before calling the
  split done, not only the in-repo checks.
- A grep pass finds consumers that reach the moved item *by name* --
  direct reference, indirect import, hardcoded path. It cannot find a
  consumer that reaches it by something specific to what the moved item
  *is*: a serializer whose output gets pickled and later reconstructed by
  dotted path, an identifier persisted in a cache key or replay log, a
  schema version baked into stored data. Grepping harder does not surface
  this class of consumer -- asking "what's unusual about this specific
  item, given what it does" does. Treat the discovery methods above as a
  minimum, not a checklist that closes the question once satisfied.

Counterexample: a moved item with no downstream packaging/export/install
step, and no other script that imports or hardcodes a path into it, does
not need multi-hop tracing -- a single-repo grep and its own test suite
are sufficient evidence there.

## Escalating Evidence Shape as Complexity Grows

When recording comparison/verification data (e.g. the shared-consumer
table above), default to the flattest shape that stays correct, and
escalate only when a concrete complexity signal appears -- do not default
to the most structured format "to be safe," and do not stay on prose past
the point a table would already remove ambiguity.

**Start with a flat table** (one row per entity, one column per fact)
when facts are short, few, and directly comparable across entities; a
human is the primary consumer scanning for an asymmetric outcome; and no
downstream tooling needs to parse or validate the data.

**Escalate to a schema'd, self-labeling format** (JSON, or an equivalent
key-value structure) once any of these appear: a single entity needs more
than one fact per "cell" (a list of sub-results, not one value -- a 2D
table cannot represent this cleanly without collapsing structure into a
delimited string); the data needs a machine-checkable schema (a
validator, a CI check, a downstream consumer parsing it) rather than only
human review; or the data will be revised repeatedly and diffed over
time -- a schema'd format with stable keys diffs predictably, while a
table's column/row identity depends on position, which shifts under
edits.

This is the same principle a private companion capability already applies to its own
evidence: a RED finding starts as a short, typed note (case/contract
layer, etc.) and is escalated into a formal JSON case file
(`evals/behavior/cases/*.json`, schema-validated) once it needs to be a
repeatable, machine-checked contract rather than a one-time observation.
Do not jump straight to JSON for a quick, one-off comparison a table would
represent just as correctly with less overhead -- the escalation should
track an actual complexity signal, not a general instinct toward more
structure.

## Verify via the Pipeline Stage That Actually Parses the Changed File

Identify which build/verification pipeline stage actually parses or
processes the specific file type being changed (a manifest is validated by
a manifest-merger step inside a full package-build tool, not by a
native/compiler-only build step) before treating any pipeline result as
evidence the change is valid. Run the full pipeline stage that processes
the changed file type, not only a narrower stage that happens to already
run for other reasons, especially for a change that "feels" doc-only or
trivial (a single XML comment edit can still be structurally illegal).
Treat a passing result from a stage that does not parse the changed file
type as no evidence at all about that file's correctness, even if the
overall build reports success.

## Verifying a General Mechanism Requires a Non-Degenerate Input

When verifying a fix intended to generalize over a class of inputs (a path
resolver, a parser, a key-based lookup), identify the structural feature
that actually distinguishes members of that class (a subdirectory
component in a resource key, a special character, a boundary length) and
include at least one test input exercising that feature, not only the
simplest/flattest example. Do not consider a general-purpose mechanism
verified merely because the one input used during development happened to
succeed -- state explicitly which subset of the input space was actually
exercised. When the fix involves a filesystem or I/O write whose success is
not checked, add that check as part of the same fix, since a silent I/O
failure is exactly the kind of defect a degenerate-input-only test cannot
surface.

## Method-Name Collision When Adding a Shared Base Class

Before compiling a change that adds a shared base class (a mixin, an
intrusive ref-counted base, any base contributing named methods) to an
existing class, grep the target class for any pre-existing method sharing a
name with the new base's contract. A same-name, compatible-signature method
silently shadows the base's method instead of producing a compiler error,
and the two can have unrelated meanings (a domain-specific "release a GPU
handle" versus "decrement the reference count"). When a collision is found,
rename the pre-existing method to something unambiguous -- updating its
declaration, definition, and every call site -- before the base class is
introduced, and verify via grep that the rename's call-site count matches
expectations.

## Build-Wrapper Cache Trust

A build wrapper's own "cached / up-to-date, nothing to do" result is not
evidence the underlying toolchain actually recompiled the changed file --
after editing a source list (adding/removing/renaming a compiled source),
force a direct toolchain invocation and confirm the changed file's own
compile step actually ran, in its own compile log, before trusting a green
wrapper result for that change.

Counterexample: an incremental build reporting "up to date" immediately
after a source-list edit, with no compile-log line for the newly added or
renamed file, is not confirmed -- it is exactly the shape of a stale-cache
false pass.

## Known-Issue Record Closure After a Backend/Migration Change

A known-issue record (a tracked defect, a documented workaround, a
compatibility note) is not closed by one non-reproduction on a replacement
backend or migration path. Non-reproduction on a new path is weaker
evidence than reproduction was on the old one, because the new path may
simply not exercise the same mechanism yet. Close a known-issue record only
against an updated characterization/comparison tied to that specific
record -- what mechanism the old defect depended on, and why the new path
does or does not share it -- not against a bare "could not reproduce."

## Workaround-Mechanism Churn Versus Diagnostic Evidence

When an intermittent failure resists a first fix, add diagnostic evidence
(per-call logging, a reproducing test, state capture at the failure point)
before or alongside trying a structurally different mechanism as the next
attempt. Do not substitute mechanism after mechanism (library A, then
library B, then a third approach) as the search strategy itself -- each
swap without diagnostics discards whatever the previous attempt's failure
pattern could have revealed about the actual cause.

## Backend-Selector Build-Cache Isolation

A compile-time backend/renderer selector macro is part of build identity,
not merely a code-path choice. When a build selects between backends via a
compile-time macro or flag, use isolated object/library output directories
per selector value, and verify which backend actually linked into the
result independently -- do not assume a shared build-cache output reflects
the currently-selected backend just because the build reported success.

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
