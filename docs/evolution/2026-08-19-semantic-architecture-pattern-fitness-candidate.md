# Semantic architecture and pattern fitness — optimization candidate

Status: candidate only. It has not completed RED/GREEN or lifecycle review and
is not yet an authoritative Skill rule.

## Core decision

Do not score architecture by counting SOLID principles, layers, interfaces or
named design patterns. Score a decision in a declared domain context by the
pressure it answers, semantics it preserves, failure behavior it exposes and
evidence that proves the result. The same pattern may be strong in one domain
and unsafe in another.

## Required context profile

Before scoring, record:

- Domain and consumers.
- Existing/brownfield/refactored status.
- Invariants and real variation axes.
- State and physical/digital authority.
- Lifecycle, concurrency and failure cost.
- Platform/hardware/deployment boundaries.
- Evidence level and hard gates.

No profile means no comparable score.

## Semantic SOLID interpretation

| Principle | Review meaning | Failure signal |
|---|---|---|
| SRP | One authoritative outcome/owner and one coherent reason to change | A module changes for unrelated policy, platform, persistence and recovery reasons |
| OCP | A demonstrated variation axis can extend without destabilizing existing consumers | Interfaces exist for hypothetical variation, or extensions bypass safety/observability |
| LSP | Substitution preserves observable behavior, lifecycle, errors, timing assumptions and resource ownership | Types compile but origin, completion, cancellation, custody or recovery semantics differ |
| ISP | A consumer receives the least capability needed for its responsibility | Broad façade exposes lifecycle, write, safety or privileged operations unnecessarily |
| DIP | Policy depends on a stable capability contract while variable mechanism remains outside | Every concrete type is wrapped, but unstable domain policy leaks into the abstraction |

## Pattern transformations

| Semantic pressure | Game/engine transformation | Equipment transformation | Required evidence |
|---|---|---|---|
| State | Scene/action/input state may update per frame and sometimes replay | Actual/readback/command/unknown must be distinct and reconciled | Transition and failure cases |
| Command | Local actions may cancel, replay or predict | Async, possibly irreversible, identity/idempotency/late completion required | Attempt ledger and recovery tests |
| Observer/Event | Some visual/resource updates may coalesce | Custody/alarm/process evidence needs authority, ordering and audit | Ordering, loss, duplicate and replay tests |
| Strategy | Backend/resource policy selected by platform/capability | Dispatch/recipe/recovery constrained by interlocks and qualification | Capability and prohibited-path tests |
| Adapter | Preserve Metal/GLES/DirectX differences behind render capability | Preserve device protocol completion/error/safety differences | Shared-consumer before/after matrix |
| Composite | Scene/GUI hierarchy, transform and Z-order | Module/capability topology plus pressure/resource/interlock edges | Topology and route feasibility tests |
| MVC/MVVM | UI projects game state and sends intent | HMI never becomes equipment readiness or physical authority | Projection-versus-authority tests |
| Factory | Backend/resource creation and lifecycle | Device/module capability, version, diagnostics and safe lifecycle | Compatibility and failure-construction tests |
| Repository | Saves/assets, often application-owned | Recipe/config/history/audit with durability and version gates | Transaction/migration/trace tests |
| Mediator | Component/scene coordination | Scheduler/sequence coordination without hiding custody/interlock owners | Traceability and authority tests |

## Quantitative score

Rate each dimension 0–4, multiply by weight, divide by four. Keep raw ratings
and evidence; do not publish only the total.

| Dimension | Weight |
|---|---:|
| Pressure fit | 15 |
| Semantic preservation | 20 |
| Ownership/state authority | 20 |
| Lifecycle/failure behavior | 15 |
| Change isolation | 10 |
| Testability/observability | 10 |
| Cognitive/operational cost | 10 |

Ratings: 0 conflicts/missing; 1 pattern shape only; 2 useful happy path with
material gaps; 3 complete contract and executable tests; 4 target-platform or
field-proven inside the declared envelope.

Attach evidence level `E0`–`E4`: not run, documented, deterministic contract,
model/simulator/integration execution, target/field evidence. A score of 85/E1
is not stronger than 78/E4 for an operational release decision.

## Domain weighting profiles

- Cross-platform game engine: increase platform semantics, frame/resource
  lifecycle, performance determinism and shared-consumer compatibility.
- Equipment software: increase state authority, command completion, custody,
  restart/reconciliation, traceability and safety/interlock consequences.
- Business/client-server application: increase transaction, identity, data
  history, authorization, deployment and version compatibility.

Changing weights requires a named pressure; weights are not tuned to make a
preferred option win.

## Hard gates

Regardless of total score, fail a decision that permits duplicate/lost physical
custody, unsafe interlock bypass, unowned durable state, silent data corruption,
unreconciled irreversible command ambiguity, unversioned breaking migration,
unapproved whole rewrite, or evidence claims above the executed layer.

## Review output

For each option report context profile, semantic responsibility map, score by
dimension, evidence level, hard gates, failure counterexamples, rejected
alternatives, smallest incremental slice, rollback/stop conditions and the
condition that would justify revisiting the decision.

## Required RED before promotion

Test at least the same State, Command, Adapter and Observer pressures in both a
cross-platform engine and an equipment-control scenario. Baseline failure must
show that a textbook/template interpretation chooses the same shape while
missing domain-specific authority or failure semantics. GREEN must improve both
without turning the rubric into domain-specific memorization.
