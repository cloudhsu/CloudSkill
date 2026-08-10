# CloudBox resumable lifecycle orchestration design

## Purpose

Define an AI-agent-compatible process owner that selects and composes an
engineering lifecycle from actual delivery pressures, preserves evidence and
authority across long-running work, and resumes safely after interruption.

The process owner governs workflow state, transitions, evidence, and decision
rights. It does not replace the domain, architecture, design, implementation,
quality, document, or release owner.

This design is separate from Review Assurance Levels. Lifecycle orchestration
requests a required review level; the review subsystem returns achieved level,
decision, findings, cost, and evidence lineage.

## Selected approach

Use reusable lifecycle capabilities rather than one fixed pipeline:

`Explore, Analyze, Architect, Design, Implement, Verify, Release, Operate, Learn`

The process owner selects a profile, includes only required capabilities and
gates, and recomposes the flow when evidence changes. This avoids both extremes:
a mandatory waterfall for every change and an ungoverned loop with no durable
baseline or release evidence.

## Process-owner responsibilities

The authoritative process owner must:

1. Classify work, uncertainty, risk, dependency, feedback latency, and release
   pressure.
2. Select or compose a lifecycle profile before substantial execution.
3. Define stage entry, exit, re-entry, authority, evidence, and handoff rules.
4. Route each technical decision to its owning Skill or human role.
5. Preserve durable state and reconcile interrupted or late-completing actions.
6. Invalidate only evidence affected by a changed source or decision.
7. Recompose the lifecycle when declared triggers fire.
8. Request the minimum Review Assurance Level required by current risk.
9. Distinguish implemented, verified, released, deployed, and operationally
   confirmed states.

`development-process-tailoring` is the semantic owner for profile selection and
recomposition. `using-cloudskill` remains the Skill router. Repository-agent
permissions and worktree rules remain with `coding-agent-project-governance`.

## Lifecycle profiles

| Profile | Use when | Typical topology |
|---|---|---|
| `iterative_incremental` | Target direction is plausible but detail becomes clearer through delivery evidence | Analyze -> bounded architecture/design -> implement/verify loop -> release |
| `eval_driven_evolution` | A Skill, Router, Eval, grader, or agent behavior must improve from repeatable evidence | Candidate -> RED -> owner -> minimum change -> GREEN -> regress -> review -> release |
| `stage_gated` | Contract, regulatory, safety, certification, hardware, or irreversible baseline requires formal control | Accepted baselines and explicit gates between analysis, architecture, design, verification, and release |
| `agile_incremental` | Requirements are unstable and user feedback is frequent and inexpensive | Short analyze/design/implement/verify/release/learn increments |
| `discovery_spike` | Technical or operational feasibility is unknown | Question -> bounded experiment -> evidence -> accept/reject/defer; no automatic production merge |
| `hybrid_hardware_software` | Hardware, firmware, software, certification, and device-lab clocks differ | Stage-gated interfaces/milestones plus iterative software workstreams |
| `hotfix` | Field or production impact requires bounded urgent correction | Reproduce -> minimum fix -> targeted verification -> release -> mandatory merge-forward/retrospective |
| `brownfield_migration` | Live responsibility must move without breaking contracts or recovery | Characterize -> seam -> incremental move -> dual evidence -> cutover/rollback |
| `lightweight_change` | Scope is local, reversible, well-understood, and low risk | Inspect -> change -> focused deterministic checks -> bounded review if required |

One product may run several profiles concurrently by workstream. Selecting
`stage_gated` for safety or interface baselines does not require every software
feature to use the same topology.

## Default profiles

### Software development default

Default to `iterative_incremental` with discovery awareness:

1. Round 0 locates the problem, current behavior, constraints, unknowns, risk,
   and the smallest validation.
2. Round 1 establishes a first verifiable slice with bounded requirements,
   architecture constraints, design, implementation, and tests.
3. Later rounds use new evidence to correct or extend the slice.
4. Release proceeds only when the applicable evidence and authority gates pass.

Two rounds are not mandatory. A small proven change may finish in one; a risky
or uncertain change may require more. Evidence, not round count, controls exit.

### Skill evolution default

Default to `eval_driven_evolution`:

1. Preserve a sanitized candidate and locate the authoritative owner.
2. Establish a repeatable RED case before editing.
3. Apply the smallest Skill, Router, Eval, grader, or runtime correction.
4. Execute the same case for GREEN evidence.
5. Regress adjacent routes, over-trigger behavior, context loading, output
   contract, and grader precision.
6. Request risk-selected review assurance and release with truthful evidence.

No reproducible RED means no claimed behavior fix. Static validation does not
become behavior PASS.

## Profile-selection inputs and rules

The process owner evaluates:

- requirement stability and feedback latency;
- technical, architecture, data, platform, and hardware uncertainty;
- safety, security, privacy, regulatory, contractual, and irreversible risk;
- external suppliers, certification, devices, customers, and release trains;
- integration and deployment cost;
- automated-test and environment maturity;
- compatibility, migration, rollback, and field impact;
- team/agent capability, decision latency, and available authority.

Default routing rules include:

- high safety/regulatory/contract pressure -> add `stage_gated` controls;
- unstable requirements with cheap feedback -> `agile_incremental`;
- known direction with gradual convergence -> `iterative_incremental`;
- feasibility unknown -> `discovery_spike` before commitment;
- urgent field impact -> `hotfix` plus merge-forward;
- differing hardware/software clocks -> `hybrid_hardware_software`;
- live legacy responsibility move -> `brownfield_migration`;
- local reversible low-risk correction -> `lightweight_change`.

## Stage contract

Every included capability exposes:

```text
Input
Decision owner
Activities
Required artifacts
Verification evidence
Required review level
Exit gate
Next-stage handoff
Feedback and re-entry routes
```

The process owner may omit a capability only when it records why its pressure
is absent or already satisfied by valid reusable evidence.

## Feedback and re-entry

The lifecycle is a graph, not a one-way pipeline. A failure returns to the
earliest failed layer:

| Observed failure | Re-entry owner |
|---|---|
| Implementation violates a valid design/contract | Implement |
| Interface, component responsibility, data model, or algorithm is wrong | Design |
| State/policy authority, system boundary, lifecycle, deployment, persistence, or recovery model is wrong | Architect |
| Requirement, constraint, acceptance criterion, or quality scenario is wrong | Analyze |
| Problem or use context is wrong | Explore |
| Test case, environment, harness, model context, or grader is invalid | Test/Eval system owner |

Re-entry preserves the failure evidence, identifies affected baselines, performs
impact analysis, invalidates affected downstream evidence, and reruns only the
required gates. A changed authority, safety, persistence, or recovery boundary
requires architecture re-entry and a risk-level reassessment.

## Durable work state

Long-running work must not depend on one chat session. Persist at least:

```yaml
work_id: stable-identifier
work_type: development | skill_evolution | architecture | document | release
selected_profiles: []
current_stage: verify
current_round: 2
status: active | paused | interrupted | blocked | deferred | failed | complete
source_baseline:
  commit: null
  contract_hash: null
  evidence_hash: null
completed_steps: []
current_action:
  action_id: null
  state: pending | running | completed | uncertain
  expected_artifacts: []
next_action:
  command: null
  prerequisites: []
authority:
  approved_actions: []
  prohibited_actions: []
review:
  required_level: null
  achieved_level: null
remaining_risks: []
```

Secrets, actual private URLs, raw transcripts, and credentials are referenced
indirectly and remain outside public workflow state.

## Checkpoints and action semantics

Safe checkpoints exist after exploration evidence, accepted analysis baseline,
architecture decision, design contract, implementation commit, verification
bundle, review state, release candidate, deployment record, and operational
observation.

Every consequential action has:

- stable `action_id` and deduplication key;
- explicit authority and target;
- bounded retry and timeout;
- expected artifacts and completion evidence;
- atomic local writes where possible;
- idempotency or a defined compensation operation;
- late-completion and restart reconciliation;
- checkpoint advancement only after evidence persists.

An external timeout is not proof of failure. A retry is prohibited until the
process owner checks whether the external action completed late.

## Concurrency, cancellation, and replanning

One durable work item has one state-transition writer at a time. Parallel
agents may own independent actions, but each action declares its artifact and
state ownership, dependency edges, merge point, and conflict policy. A lease or
equivalent fencing value prevents a stale agent from advancing state after a
new coordinator takes ownership. Worker completion cannot directly publish,
merge, release, or mark the parent complete unless that authority was granted.

Cancellation and user pivots are first-class transitions. They stop issuance
of new actions, preserve completed evidence, reconcile already-started external
effects, and classify unfinished work as cancelled, reusable, or unsafe. A
side question does not silently replace the parent task; a true pivot records
which prior objective was superseded.

Recomposition uses hysteresis: one weak signal may open a risk or uncertainty,
but the process does not oscillate repeatedly between profiles without new
decision-relevant evidence. Every profile change records its trigger, old and
new topology, invalidated evidence, and exit condition.

## Budget, retention, and schema evolution

Every long-running work item may declare time, token, provider-call, cost, and
retry budgets. Budget exhaustion causes a truthful pause or degraded decision;
it never converts incomplete evidence into PASS. Deterministic no-change and
reconciliation paths consume no hosted-review budget.

Durable state has an explicit schema version and forward migration path. A new
runtime must either migrate a copied state atomically, read the old version in
compatibility mode, or stop with `MIGRATION_REQUIRED`; it must not partially
interpret unknown state. Checkpoints, evidence, logs, and temporary artifacts
have retention classes. Garbage collection preserves release, authority,
incident, audit, and rollback evidence and never deletes the only recovery
source.

Observability records transition, action, latency, retry, cost, and failure
category without logging credentials, private URLs, raw prompts/transcripts,
or sensitive payloads. Clock timestamps aid audit but stable IDs and hashes,
not wall-clock order alone, determine identity and deduplication.

## Resume and reconciliation

Resume begins with read-only reconciliation, never blind continuation:

1. Load the latest durable checkpoint.
2. Verify source, contract, artifact, and evidence hashes.
3. Inspect repository and relevant external side effects.
4. Determine whether the interrupted action completed, failed, or remains
   uncertain.
5. Return one state:
   `SAFE_TO_RESUME`, `ALREADY_COMPLETED`, `RETRY_REQUIRED`,
   `RECONCILIATION_REQUIRED`, `STALE_BASELINE`, or `AUTHORITY_REQUIRED`.
6. Continue from the first step whose completion is not proven.

`paused` is an intentional resumable stop. `interrupted` means completion is
unknown. `blocked` means a dependency or decision prevents progress. `deferred`
moves work to a later horizon. `failed` records a confirmed failed action; none
of these states automatically erase prior valid evidence.

## Resumable review integration

Each review cell records the frozen packet/source/contract hashes, requested
and canonical model identity, family, state, verdict, tokens, attempts, and
cost. Resume reuses a completed cell only when its hashes remain applicable.
It executes only missing or invalidated cells. Repeated execution of one model
does not increase achieved assurance.

Candidate changes invalidate affected review cells. Evidence-only records do
not invalidate source review. A material scope or governing-contract change
requires a new frozen packet and risk reassessment.

Lifecycle advancement requires the review subsystem to return:

```text
required_level
achieved_level
decision
blocking findings and vetoes
degradation reason
exception authority, if any
evidence lineage
token/cost record
```

## Token-efficiency rules

- Use the default profile instead of redesigning process for routine work.
- Run deterministic checks before hosted reasoning.
- Load only the current state, changed evidence, governing contracts, and
  affected artifacts.
- Reuse hash-valid checkpoints and review cells.
- On re-entry, rerun only invalidated downstream gates.
- No-change synchronization and reconciliation make zero model calls.
- Stop reviewer execution on a valid blocking finding, fix it, and recheck only
  affected cells when lineage permits.
- Escalate model count and capability only to the risk-required level.

Token savings never justify skipped authority, fabricated completion,
misclassified assurance, or reuse of stale evidence.

## Deployment and operational closure

Release, deployment, and target verification are separate transitions.
High-impact changes support staged rollout, canary/bounded pilot, health gates,
automatic or authorized rollback, and stop-the-line criteria. A successful
deployment command is not operational success; the process closes only after
the required observation window and evidence are satisfied or explicitly
deferred with an owner.

Operational incidents and field evidence enter the same classifier as test
failures and may return work to Explore, Analyze, Architect, Design, Implement,
or the verification system. Hotfix completion includes merge-forward/backport,
regression preservation, document/release baseline repair, and a decision on
whether the default lifecycle or architecture must change.

## RED and GREEN evidence

Implementation must first preserve RED fixtures for:

1. Resume blindly repeats a completed external action.
2. A timeout is treated as failure without late-completion reconciliation.
3. A changed architecture baseline reuses stale downstream evidence.
4. A test-harness defect incorrectly routes product work back to implementation.
5. A low-risk edit unnecessarily selects the full stage-gated flow.
6. A high-risk authority change stays in a lightweight profile.
7. A completed review cell is rerun despite identical source/contract hashes.
8. A modified candidate incorrectly reuses its old review verdict.
9. A paused task is mislabeled blocked or complete.
10. Resume silently expands previously granted authority.
11. Two coordinators advance one work item without fencing.
12. Cancellation loses evidence or repeats a late external side effect.
13. Profile selection oscillates without new evidence.
14. An exhausted token/cost budget is reported as PASS.
15. A newer runtime partially reads an unsupported state schema.
16. Deployment command success is reported as target-environment verification.

GREEN requires correct classification, transition, evidence invalidation/reuse,
idempotent recovery, and adjacent regressions for the existing development and
Skill-evolution flows. Structural state-schema validation is not sufficient
behavior evidence.

## Documentation and operational evidence

The authoritative workflow record contains current state and lineage. Human
handoffs, dashboards, release notes, and management views are derived views.
They must not become independent mutable truth.

Every completion report distinguishes:

- implemented;
- deterministic checks passed;
- behavior or system verification passed;
- review required/achieved;
- CI passed;
- released/tagged;
- deployed;
- target environment verified;
- operational feedback observed;
- work deferred or excluded.

## Scope boundaries

Included in future implementation:

- profile contract and selection rules;
- default development and Skill-evolution profiles;
- stage, transition, re-entry, and evidence-invalidation contracts;
- durable work state, checkpoints, resume, and reconciliation;
- Review Assurance integration;
- deterministic anti-drift and interruption fixtures;
- truthful derived handoff and status views.
- concurrency fencing, cancellation/pivot, budget, retention, schema migration,
  staged deployment, and operational-closure contracts;

Excluded:

- one mandatory lifecycle for every project;
- replacing technical decision owners with the process owner;
- storing credentials or raw private evidence in public state;
- automatically granting new authority on resume;
- claiming deployment or operational success from build/CI evidence;
- always running two iterations or a full review panel;
- NAS monitoring implementation, which remains a separately scheduled source
  integration concern.
