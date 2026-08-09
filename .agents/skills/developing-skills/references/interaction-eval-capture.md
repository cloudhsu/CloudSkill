# Interaction-derived Eval Capture

## Purpose

Convert a useful live Codex or Claude Code interaction into a private, reviewable candidate without publishing the raw conversation or allowing the daily project agent to modify CloudSkill itself.

## Candidate lifecycle

Same-machine session (a reachable CloudSkill repository clone):

`current interaction -> sanitized draft -> capture_eval_candidate.py -> candidates | manual-review -> batch review -> formal Eval | rejected -> processed`

Disconnected/external session (no reachable CloudSkill repository on this machine):

`current interaction -> sanitized draft -> export_eval_candidate.py -> local eval-outbox + zip -> user transfers zip -> <CloudSkillRepo>/.local/eval-inbox/imports/ -> import_eval_candidates.py -> candidates | manual-review | rejected -> batch review -> formal Eval | rejected -> processed`

The private Inbox is evidence staging in both paths. The public `evals/` tree contains only reviewed, generalized, repeatable cases.

## Configuration discovery

Use the first valid configuration in this order:

1. `<current-project>/.cloudskill/config.local.json`
2. `$HOME/.cloudskill/config.json`

A valid configuration must keep `default_sanitization=true`, `save_raw_transcript=false`, `auto_modify_skills=false`, `auto_commit=false`, and `auto_push=false`. Stop rather than weakening these controls.

## When no configuration resolves: disconnected/external session export

Do not guess a write location and do not silently skip capture when neither
config path exists or resolves to an unreachable directory (a different
machine, a cloud sandbox, a project that was never locally configured). Use
this Skill's own `assets/export_eval_candidate.py` instead:

```bash
python3 .claude/skills/developing-skills/assets/export_eval_candidate.py \
  --kind positive --input draft.json
# or --kind negative
```

This script:

- performs the same structural validation and sanitization scan as
  `capture_eval_candidate.py`, with no dependency on the CloudSkill
  repository (stdlib only, so it works wherever the Skill is installed);
- writes into a local, config-free `.cloudskill/eval-outbox/{candidates,
  manual-review}/` folder inside the current project (no CloudSkill
  repository access required);
- packages the result into one timestamped
  `CloudSkill-eval-export-<label>-<timestamp>.zip` in the current directory;
- without a reachable private `sensitive-terms.local.txt` (pass one with
  `--sensitive-terms PATH` if one happens to be available on this machine),
  conservatively routes the candidate to `manual-review` rather than risking
  an automated `PASS`.

Tell the user the exact zip path and this instruction: copy the zip into
`<CloudSkillRepo>/.local/eval-inbox/imports/` on the machine that hosts the
CloudSkill repository, then run `python3 scripts/import_eval_candidates.py`
there. That import step re-validates every candidate, re-scans it against
the repository's own private sensitive-terms file, de-duplicates against
what the Inbox already has, and files it into `candidates/`,
`manual-review/`, or `rejected/`. It never touches formal `evals/`, Skill
files, or Git state — the same authority boundary as direct capture.

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
