# Lifecycle template pilot evidence

| Field | Value |
|---|---|
| Status | Candidate; independent exact-tip review pending |
| Observation scope | Three implemented templates and seven deferred registry entries |
| Registry authority | `config/lifecycle-templates.json` |
| Plan Owner | `development-process-tailoring` |
| Implementation source tip | `0d17f40e74c04d760de2418d792c8b4d344adb8c` |
| Provider-backed Runtime Eval | `NOT RUN` |
| Version/push/PR/merge/tag/Release | `NOT RUN` |

## Evidence inventory and lineage

Repository evidence read for this record includes the approved design and
plan, Task 1 through Task 4 reports, the registry, selector/composer, lifecycle
plan contract, focused validators, behavior cases, Skill text, handoff, and
change history. No private Inbox, raw transcript, credential, external project
source, or hidden runtime trace was used. Provider-backed Runtime Eval was not
run for this pilot and therefore supplied no Runtime Eval output.

The implementation lineage is:

- base before the pilot: `b31ac352c950fda6752d6ea8b6063e9eaa5d740b`;
- design/plan: `b6ebd07` and `ed76f5f`;
- registry RED and repairs: `2519fce`, `3366baa`, `966df65`;
- selection and typed-exclusion GREEN: `af39df0`, `15eba41`;
- composition/replan and evidence-integrity repairs: `02b9e87`, `bfc96b0`,
  `0ad81d0`;
- Skill behavior candidate: `0d17f40e74c04d760de2418d792c8b4d344adb8c`.

The candidate documentation commit that contains this record is intentionally
not self-certified as independently reviewed. The controller-assigned final
reviewer must record the exact candidate tip used for review and return PASS
only after resolving every High/Medium finding.

## Authority and delivered boundary

`config/lifecycle-templates.json` is the sole mutable template authority. The
catalog and Skill are views/routing instructions. The selector/composer is pure:
it reads explicit facts plus the supplied registry, returns evidence, and has no
task execution, model, background-agent, network, external-tool, Git, release,
or persistence authority. Existing lifecycle orchestration remains the durable
state/reconciliation owner.

Implemented IDs are `lightweight-change`, `bounded-feature`, and
`skill-evolution`. The seven deferred IDs remain `unsupported`; no mechanics or
fallback were added for them.

## RED and GREEN evidence

Deterministic RED/GREEN was preserved across the task reports:

- Task 1 initially failed because both the registry and contract were absent;
  after the registry was added, it retained the intended missing-contract RED.
- Task 2 made the selector GREEN, then a true-exclusion mutation reproduced
  nine unsafe accepts before the typed exclusion fix.
- Task 3 initially failed because composition was absent. Later REDs reproduced
  unsealed resolution admission, invalidation-unsafe replans, resealed deferred
  forgery, unrelated-evidence over-invalidation, and incomplete lineage. The
  focused validators are GREEN after authoritative replay and selective
  invalidation repairs.
- Task 4 mapped the pre-change Skill at `0ad81d0` to
  `PROC-BEH-007..016`. Cases 007 and 008 were already PASS and remain
  regression-only. Cases 009, 010, 011, 012, 014, 015, and 016 are classified
  `FAIL` because required template-contract behavior was missing, while their
  prior generic process behavior is noted as partially satisfying the rubric.
  Case 013 is also `FAIL` because unknown-delta escalation was absent. The same
  separate read-only static/manual adjudicator mapped the changed Skill at
  `0d17f40` to PASS for all ten cases.

The Task 4 report identifies the adjudicator only as a "separate read-only
agent" that manually mapped each rubric to the before/after Skill. It records no
stable reviewer/agent ID, human reviewer identity, provider/model ID, prompt or
raw-output hash, or human-only attestation. Whether the adjudication was model-
assisted or performed by a human is therefore `UNKNOWN`; reviewer independence
cannot be established from the retained provenance. The report does establish
that the adjudicator did not edit repository files and that no repository
Runtime Eval provider was invoked. This remains static/manual semantic
adjudication. The behavior case validator proves only contract structure.
Neither is represented as provider-backed Behavior execution.

## Fast-path and size evidence

Measurement method: for each implemented template, construct the smallest
exact-match facts from registry applicability, all declared exclusion facts as
literal `false`, and all six bounded deltas as literal `false`. Serialize a
request envelope of `template_id` plus `facts`, and the returned
`assess_template()` result, as sorted compact UTF-8 JSON. Byte counts are exact
for this method at source tip `0d17f40`.

| Template | Request bytes | Result bytes | Result | Full-risk calculation |
|---|---:|---:|---|---|
| `lightweight-change` | 437 | 607 | `selected` | avoided for this exact match |
| `bounded-feature` | 470 | 640 | `selected` | avoided for this exact match |
| `skill-evolution` | 455 | 625 | `selected` | avoided for this exact match |

Denominator: three canonical exact-match scenarios, one per implemented
template. Therefore three repeated full-risk calculations are avoided in this
fixture set. This is not a claim about production frequency or elapsed-time
savings. The registry file is 11,871 bytes on disk and is deterministic input
data, not model context.

For comparison only, a four-UTF-8-bytes-per-token heuristic gives request/result
estimates of approximately 110/152, 118/160, and 114/157 tokens. These are not
provider tokenizer measurements, usage records, or billing evidence. The pure
selector/composer makes zero model calls. Provider-backed Runtime Eval is
`NOT RUN`, so provider input/output/reasoning-token and provider-cost evidence
for that Eval is unavailable. The Task 4 adjudicator's execution modality is
unknown, so this record makes no call, token, or cost claim for that separate
adjudication.

The fast path removes only a fresh full-risk calculation. It retains lifecycle
ownership, all selected gates/evidence, verification, Review Assurance, durable
reconciliation, and invalidation/replan rules.

## Composition and regression findings

- Direct selection is deterministic for all three implemented templates.
- Every true or unknown delta and every missing/malformed exclusion fact fails
  closed to `escalation_required`.
- Deferred and unknown templates return `unsupported` without fallback.
- Duplicate, incompatible, and owner/gate/completion-conflicting overlays
  return `conflict`.
- The current authoritative `bounded-feature + skill-evolution` pair is
  declared compatible but returns `conflict` because policy/action/evidence
  owners differ. Successful strongest-gate composition is proved only against
  a synthetic owner-aligned registry fixture.
- Selected plan admission requires authoritative replay, provenance, and an
  integrity seal. Replans keep contiguous selected/unresolved lineage and
  invalidate the selected resolution only when its delta-evidence identity is
  affected.
- Legacy lifecycle-plan callers without a template resolution retain their
  previous shape and default Review Assurance behavior.
- Adjacent controls keep trivial work lightweight, keep generic detailed
  planning subordinate, and preserve lifecycle first, evidence/verification
  second, token reduction third.
- Task 4's historical uppercase `PARTIAL` label is normalized here to `FAIL`
  with partial prior behavior satisfaction retained as explanatory detail.
  Final review should still confirm that the Skill's literal-boolean/all-false
  wording is sufficiently unambiguous; Task 4 classified that as a minor.

## Deterministic checks

Before Task 5 documentation, a fresh
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_all_checks.py` exited 0 and ended
with `All CloudSkill checks passed.` It validated 19 Skills, 94 routing cases,
136 behavior case contracts, lifecycle audit, packaging/install smoke, planning
priority, template selection/composition, lifecycle replan/reconciliation, and
the rest of the repository suite. The behavior validator explicitly reported
that case validation is not model behavior execution.

After Task 5 documentation, the exact combined command

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_all_checks.py && git diff --check
```

exited 0 and again ended with `All CloudSkill checks passed.` `git diff
--check` produced no diagnostics. This is local deterministic/static, fixture,
package, and install-smoke evidence; it is not CI or provider behavior evidence.

## Review and release truth

Task 4 used a separate read-only static/manual adjudicator of unknown identity
and unknown human/model execution modality for the pre/post Skill comparison.
Task 5 self-review covers documentation consistency and evidence transcription
only. Independent exact-tip review of authority,
lifecycle continuity, evidence validity, composition conflict, deferred
behavior, anti-drift tests, token claims, privacy, and documentation is
`NOT RUN` at this checkpoint; the controller has assigned it to a final
reviewer after the candidate commit.

No version synchronization, push, PR, merge, tag, GitHub Release, provider
Runtime Eval, external host reload, deployment, or field verification was
performed. The pilot is a local candidate, not a released capability.
