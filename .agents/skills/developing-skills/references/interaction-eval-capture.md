# Interaction-derived Eval Capture

## Purpose

Convert a useful live Codex or Claude Code interaction into a private, reviewable candidate without publishing the raw conversation or allowing the daily project agent to modify CloudSkill itself.

## Candidate lifecycle

`current interaction -> sanitized draft -> candidates | manual-review -> batch review -> formal Eval | rejected -> processed`

The private Inbox is evidence staging. The public `evals/` tree contains only reviewed, generalized, repeatable cases.

## Configuration discovery

Use the first valid configuration in this order:

1. `<current-project>/.cloudskill/config.local.json`
2. `$HOME/.cloudskill/config.json`

A valid configuration must keep `default_sanitization=true`, `save_raw_transcript=false`, `auto_modify_skills=false`, `auto_commit=false`, and `auto_push=false`. Stop rather than weakening these controls.

## Mandatory sanitization

Remove or generalize direct and indirect identifiers, including:

- Organization, customer, department, person, project, product, machine, site, and facility names.
- Email, account, IP address, URL, internal repository, server, share, and absolute filesystem path.
- Device serial, lot identifier, unreleased schedule, staffing, topology, customer requirement, recipe value, interlock threshold, and safety limit.
- Private namespace, host, database, branch, ticket, and source reference that could reconstruct the original environment.

Keep the reusable technical pressure: command/readback mismatch, state ownership, timeout, retry, lifecycle, modeling boundary, missing evidence, overengineering, or correct skill composition.

A generic domain term such as EFEM, MFC, Load Lock, PVD, Qt, C#, or REST is not an identifier by itself.

## Positive candidate

Record:

- A generalized prompt.
- Expected and observed/inferred/unknown skills.
- Behaviors that must remain.
- Excess architecture or unsupported claims that were correctly avoided.
- Outcome and actual verification status.

Do not turn stylistic preference alone into a normative Eval.

## Negative candidate

Record:

- The initial failure or omission.
- The user's sanitized correction.
- Required future behavior.
- Forbidden repeated behavior.
- Failure category: routing, composition, behavioral omission, prohibited action, domain correctness, evidence discipline, or overengineering.

Do not infer hidden routing traces. Use `observed`, `inferred`, or `unknown` explicitly.

## Batch review into formal Evals

Only from the CloudSkill repository and only after explicit instruction:

1. Re-scan sensitive content.
2. Reject or manually resolve uncertain records.
3. Deduplicate equivalent mechanisms.
4. Identify the authoritative skill owner and adjacent negative controls.
5. Rewrite the prompt into a standalone repeatable case.
6. Add routing, behavior, composition, or counterexample coverage.
7. Establish RED evidence before modifying a skill.
8. Run structural and behavioral regression checks.
9. Review the diff before commit or push.

One interaction may justify a candidate. A skill rule normally requires a repeatable failure or a high-severity prohibited behavior.
