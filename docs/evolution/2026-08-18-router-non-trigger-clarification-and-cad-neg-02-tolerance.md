# Router non-trigger clarification + `CAD-NEG-02` execution-order tolerance

Follow-up to `codebase-architecture-discovery`'s `experimental` -> `active`
promotion evidence: investigates and fixes the two open items flagged
there as "new, separate router-composition noise... not this skill's
defect."

## Diagnosis, from raw model output

Read the actual raw routing decisions for the 3 strict-gate misses
(`cad-routing-green-r3.jsonl`), not just the aggregate metric.

### `CAD-NEG-01` (2/3 attempts): a real, fixable router-instruction ambiguity

Prompt: an already-approved verbatim move of `PaymentValidator.legacy_check()`
into a new payments service. Expected `safe-incremental-refactoring`.

Two of three attempts returned `primary_skill: null`, and the raw `reason`
field in both nearly quotes `using-cloudbox-skills/SKILL.md`'s own
non-trigger line verbatim: *"the task is fully determined mechanical
execution of an already-approved move... not an analysis, review, or
design deliverable that any CloudBox skill governs"* — echoing the
router's own text, *"a task whose answer is already fully determined by
supplied text."*

This is a genuine conflation the router's instructions invited: "the
design **decision** is already made" is not the same claim as "the
**answer** is already fully determined by supplied text." The former
describes exactly when `safe-incremental-refactoring` applies — a settled
scope with real remaining behavior/contract/transaction-preservation risk
in the execution itself. The latter describes translation, arithmetic,
and inspection-only requests where no engineering judgment remains at all.
The router's own text did not distinguish these, and the model
demonstrably conflated them in 2 of 3 independent attempts (not a fluke —
a repeatable framing effect).

**Fix**: added a clarifying paragraph immediately after the ambiguous
sentence in `.agents/skills/using-cloudbox-skills/SKILL.md`'s "Selection
rule" section, naming this exact scenario shape as the counter-example.

### `CAD-NEG-02` (1/3 attempts): eval over-specification, not a routing defect

Prompt: compare two database-architecture options on state-consistency and
migration-risk tradeoffs. Expected `architecture-review`, primary
correctly selected in all 3 attempts. The 1 miss added
`application-client-server-architecture` as a supporting skill with a
defensible high-confidence reason ("the trade-off inherently spans
persistence, transaction, and state-authority boundaries" — which the
prompt genuinely does touch).

The case already declared `allow_additional_supporting_skills: true`
(signaling this addition should be tolerated), but the grader's
`execution_order` check ignores that flag and requires an exact match
against a single literal `execution_order` value unless the case also
supplies `allowed_execution_orders` — an existing, already-used mechanism
(`evals/runtime/cases/canary.json`'s `R02-code-and-command-state`) for
exactly this situation. The case was under-specified, not the routing
behavior wrong.

**Fix**: added `allowed_execution_orders` to `CAD-NEG-02` in
`evals/runtime/cases/cad-routing.json`, listing both the primary-only and
primary-plus-the-defensible-supporting-skill orderings as acceptable.

## Verification

### CAD routing suite, `repeat=3`, post-fix (21 records)

| Metric | Pre-fix | Post-fix |
|---|---:|---:|
| Overall strict pass rate | 85.7% (18/21) | **100.0% (21/21)** |
| Primary-skill accuracy | 90.5% | 100.0% |
| Execution-order accuracy | 85.7% | 100.0% |
| Gate | FAIL | **PASS** |

### Canary regression suite, `repeat=1` (10 records)

Run because the fix edits `using-cloudbox-skills/SKILL.md`, shared router
infrastructure loaded for every routing decision system-wide, not just
this skill's own cases.

| Metric | Result |
|---|---:|
| Overall strict pass rate | 100.0% (10/10) |
| Gate | PASS |

No regression on any of the 10 canary cases (network-stream staleness,
code+command-state composition, versioned multi-audience report,
greenfield internal web, component-state/recovery-ownership/composition,
Chinese-translation no-skill, English equipment architecture, historical
interaction optimization).

`scripts/run_all_checks.py` and `scripts/manage_skill.py audit --check`
both pass.

## Scope note

Only 10 of `using-cloudbox-skills`' own routing cases were re-run
(the full canary suite), not its complete `routing_case_ids` set (also
includes `USE-01..07`/`USE-NEG-01..03` in `evals/skill-routing-cases.csv`,
graded by the simpler CSV harness rather than this JSON harness) and no
behavior-layer re-run was performed. This is a targeted regression check
proportional to a 2-sentence instruction-text addition, not a full release-
grade re-certification of the router skill itself.
