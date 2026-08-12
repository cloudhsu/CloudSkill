# Interaction-derived Eval Capture

## Purpose

Convert a useful live Codex or Claude Code interaction into a private, reviewable candidate without publishing the raw conversation or allowing the daily project agent to modify CloudSkill itself.

## Candidate lifecycle

Same-machine session (a reachable CloudSkill repository clone):

`current interaction -> sanitized draft -> capture_eval_candidate.py -> candidates | manual-review -> batch review -> formal Eval | rejected -> processed`

Disconnected/external session (no reachable CloudSkill repository on this machine):

`current interaction -> sanitized draft -> export_eval_candidate.py -> local eval-outbox + zip -> user transfers zip -> <CloudSkillRepo>/.local/eval-inbox/imports/ -> import_eval_candidates.py -> candidates | manual-review | rejected -> batch review -> formal Eval | rejected -> processed`

Second machine with a reachable CloudSkill repository, but `.local/eval-inbox/` is gitignored there too (a repository clone on a second machine does not, by itself, get candidates from that machine's local disk to this one's):

`current interaction -> sanitized draft -> capture_eval_candidate.py -> candidates | manual-review -> sync_eval_exchange.py --push -> private exchange Git repository -> sync_eval_exchange.py --pull -> <CloudSkillRepo>/.local/eval-inbox/imports/ -> import_eval_candidates.py -> candidates | manual-review | rejected -> batch review -> formal Eval | rejected -> processed`

The private Inbox is evidence staging in every path. The public `evals/` tree contains only reviewed, generalized, repeatable cases.

## Configuration discovery

Use the first valid configuration in this order:

1. `<current-project>/.cloudskill/config.local.json`
2. `$HOME/.cloudskill/config.json`

A valid configuration must keep `default_sanitization=true`, `save_raw_transcript=false`, `auto_modify_skills=false`, `auto_commit=false`, and `auto_push=false`. Stop rather than weakening these controls.

If the operator supplies an Inbox path explicitly, still search the normal
configuration locations for a configuration whose resolved Inbox is exactly
that path. Reuse its private sensitive-term policy. If no owner can be proven,
say that policy resolution failed and route all content to `manual-review/`;
explicit destination selection is not a privacy-policy override.

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

## Git-based transport between machines: `sync_eval_exchange.py`

A second machine having its own reachable CloudSkill repository clone (for
example, a work laptop with both Codex and this repository already
installed) does not by itself move candidates to the machine you review
from — `.local/eval-inbox/` is gitignored on every clone, by design, because
its contents are unreviewed evidence, not a formal Eval. Do not assume
"both machines can reach the CloudSkill repository" means capture output is
already available in both places.

`scripts/sync_eval_exchange.py` moves candidates through a separate,
private Git repository the user owns and lists as `eval_exchange_repo` in
their `.cloudskill/config.local.json` / `~/.cloudskill/config.json` (this
repository is transport only — never CloudSkill's own repository, and never
committed to it).

```bash
# On the machine where capture_eval_candidate.py already wrote candidates:
python3 scripts/sync_eval_exchange.py --push

# On the machine that hosts the CloudSkill repository you review from:
python3 scripts/sync_eval_exchange.py --pull
python3 scripts/import_eval_candidates.py
```

`--push` zips whatever is currently in `candidates/`/`manual-review/` (the
same format `export_eval_candidate.py` produces), commits and pushes it to
the exchange repository's `incoming/` folder, then moves the source files
into a local `synced/` folder — never deleted, mirroring the
`processed/`/`rejected/` bookkeeping already used elsewhere in the Inbox.
`--pull` copies any zip not already reflected in
`eval_inbox/imports/processed/` into `eval_inbox/imports/`; from there,
`import_eval_candidates.py` behaves identically to the disconnected-session
path above, including the same private-terms re-scan and de-duplication.
Both directions are idempotent: re-running either with nothing new to send
or receive is a no-op, not an error.

Use this path instead of the disconnected-session zip-and-manually-transfer
path whenever both machines can reach a shared private Git remote — it
removes the "remember to physically move the file" step entirely.

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

Container intake is a separate precondition to this list. The exporter must
produce a versioned manifest with declared payload hashes and a manifest-bound
filename, and the real importer must validate the completed ZIP. Importers plan
the whole archive before publishing any candidate. Before candidate routing,
require a supported bundle/exporter/candidate schema and exact agreement between
manifest and payload CloudBox version, candidate schema, and host/runtime.
Contract mismatch fails the whole archive closed and preserves it as unsupported
evidence; do not partially import matching members. These checks prove declared
structural-contract consistency, not that the external model reasoned correctly.
Use only locally generated
output names, reject queue escape/symlink and unsafe member forms, bound member
count/path/size/expansion, preserve collisions, and leave malformed input for
manual review. These are executable obligations; this reference does not
replace their tests.

One interaction may justify a candidate. A skill rule normally requires a repeatable failure or a high-severity prohibited behavior.
