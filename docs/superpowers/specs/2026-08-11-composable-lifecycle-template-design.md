# Composable Lifecycle Template Design

Status: approved design; implementation plan pending.

## Goal

Allow CloudBox to select and compose pre-qualified lifecycle templates when a
task fits a known risk envelope, replacing repeated full risk calculation with
a bounded applicability and delta check.

## Fixed authority and priority

`development-process-tailoring` remains the sole Plan Owner. It selects the
governing lifecycle before any detailed plan or implementation workflow.

Resolve every trade-off in this order:

1. preserve the lifecycle and complete dynamic feedback loop;
2. preserve required evidence and verification;
3. reduce token and context cost.

Templates optimize lifecycle selection; they never bypass lifecycle ownership.
Evidence drives entry, transition, re-entry, replan, and completion.

## Template model

Each template is a versioned contract containing:

- template ID and contract version;
- intended pressures and positive applicability conditions;
- explicit exclusions and unsupported conditions;
- lifecycle stages, gates, and feedback/re-entry paths;
- state, policy, action, and evidence owners;
- required artifacts and evidence by gate;
- default Review Assurance level and escalation rules;
- interruption, checkpoint, resume, and reconciliation behavior;
- reusable evidence conditions and invalidation rules;
- allowed companion templates and composition precedence;
- exit conditions and triggers for a full risk reassessment.

A selected template instance records the template version, task/source identity,
matched conditions, delta-check result, composition order, overrides, plan
revision, evidence lineage, and achieved review level. Template definitions are
immutable for an active instance; changes create a new template version or plan
revision.

## Initial template catalog

Implement these first:

### `lightweight-change`

For small, local, reversible, low-risk work with no material semantic,
authority, persistence, security, platform, deployment, or external-side-effect
change. It retains lifecycle ownership but projects it into minimal scope,
verification, and completion evidence.

### `bounded-feature`

For a medium increment with approved design, stable scope, known owners,
reversible implementation, and available automated verification. It may
delegate detailed implementation planning within the current lifecycle revision.

### `skill-evolution`

For CloudSkill candidate review and evolution: evidence inventory,
sanitization/deduplication, owner selection, RED, minimum change, GREEN,
adjacent regression, review, release boundary, and effectiveness feedback.

Record but defer implementation of:

- `iterative-discovery`;
- `architecture-change`;
- `brownfield-refactor`;
- `hotfix`;
- `release`;
- `hardware-integration`;
- `incident-recovery`.

They are planned catalog entries, not shipped capabilities until their own RED,
contract, validator, and behavior evidence exist.

## Composition

Use one base template and zero or more overlays. A composed plan is a resolved
view, not a bag of independent workflows.

Precedence:

1. authority, safety, privacy, and irreversible-effect constraints;
2. deployment/platform/hardware constraints;
3. architecture and persistence constraints;
4. domain/change-method constraints;
5. lightweight execution optimization.

An overlay may strengthen a gate, add evidence, or add a feedback path. It may
not weaken a base or higher-precedence constraint. Conflicting owners, gates,
or completion semantics fail closed and require Plan Owner adjudication.

Example future composition:

```text
bounded-feature
  + architecture-change
  + hardware-integration
  + release
```

The initial implementation needs to compose only the three implemented
templates where their declared compatibility permits it. Deferred template IDs
must return unsupported rather than silently degrade.

## Fast applicability and delta check

Before applying a template, perform six bounded checks:

1. Does the task introduce a new external side effect?
2. Does it change authority, authoritative state, transaction, or durable
   ownership?
3. Does it add sensitive data, credentials, privileges, or authorization scope?
4. Does it add hardware, platform, deployment, protocol, schema, or
   compatibility variation?
5. Does it introduce an irreversible action or an outcome that cannot be
   deterministically reconciled?
6. Does any known condition fall outside the template's verified envelope?

If every answer is false and all positive applicability conditions match, use
the template without a fresh full risk calculation. Record the answers as
evidence rather than silently assuming them.

If any answer is true or unknown, do not treat that as automatic rejection.
Return to the Plan Owner to add a compatible overlay, select another template,
run a full risk assessment, or create a new plan revision. Unknown never means
safe.

## Runtime and persistence boundary

The first increment may implement pure deterministic selection/composition and
JSON contracts without introducing a background agent, external tool adapter,
or autonomous Git/release authority. Existing lifecycle orchestration remains
the durable runtime owner.

Template selection must be reproducible from normalized task facts. The
selector returns selected, escalation-required, unsupported, or conflict with
machine-readable reasons. It never performs the planned work.

## Verification

Establish RED/GREEN evidence for:

- direct selection of each initial template;
- a small task remaining lifecycle-owned without heavyweight artifacts;
- a bounded feature delegating detailed steps without delegating authority;
- Skill evolution retaining privacy, RED/GREEN, adjacent regression, manual
  exchange, and release truth;
- a matched template avoiding a repeated full risk calculation;
- every true or unknown delta escalating rather than being normalized to safe;
- composition preserving the strongest gate and detecting owner conflicts;
- deferred templates returning unsupported;
- new risk producing a new plan revision and selective evidence invalidation;
- deterministic positive propagation and negative drift mutation from the
  authoritative template registry into every consumer.

Run structural contracts, Behavior cases, lifecycle/replan validators, package
and install checks, full repository regression, and independent exact-tip
review. Provider-backed Runtime Eval must remain `NOT RUN` unless executed.

## Token model

Token savings come from deterministic template selection, bounded delta checks,
predeclared gates, and evidence reuse. Do not load detailed template bodies
until selected. Do not invoke a model to compare exact or already-qualified
template matches.

Measure selector input/output size and avoided full-assessment calls. Do not
claim provider billing savings from approximate byte/token estimates.

## Stop conditions

Stop template application when:

- owner or authority is ambiguous;
- a delta is true or unknown without a qualified overlay;
- composition weakens an existing gate;
- the task requires a deferred template;
- evidence identity or validity cannot be established;
- resume/reconciliation is undefined;
- deterministic selection is non-reproducible;
- token reduction would remove lifecycle or verification evidence.

## Planned later evolution

After the three-template pilot has field evidence, evaluate:

1. Engineering Evidence Graph linking need, decision, architecture, design,
   change, test, artifact, deployment, observation, and feedback.
2. Feedback Ingress Classification routing verification-system,
   implementation, design, architecture/authority, requirement,
   deployment/environment, process, and Skill/agent defects to the earliest
   failed layer.
3. Deployment/Operational Outcome Closure separating built, packaged, deployed,
   started, ready, exercised, observed, and accepted states.
4. Skill Effectiveness Ledger tracking recurrence, false routing, context cost,
   evidence quality, and review/deprecation triggers.
5. Periodic Skill prune/merge/deprecate evaluation.
6. Cross-host plugin activation evidence from source through cache, reload, new
   session, and representative behavior.

These are recorded future increments, not implied parts of the initial template
implementation.

## Delivery boundary

Deliver the pilot through an independently reviewed PR. Do not merge template
implementation into the already published `6.3.0` identity. Reassess the
planned `6.4.0` candidate only after the template pilot is implemented,
validated, and merged. Tag and GitHub Release require separate release gates.
