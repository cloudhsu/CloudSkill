# CloudSkill evolution change history

This document records the evolution rationale and evidence chain for work that may span multiple conversations. Git commits and tags remain the authoritative source history.

## 2026-08-09 — Claude repeat=3 import and adaptive 2x2 Skill-evaluation workflow

Continued an interrupted evidence-import session from repository handoff rather
than chat memory. A sub-agent executed
`./cloudskill-eval --provider claude --behavior-repeat 3` and wrote the normal
fixed artifact `.local/runtime-evals/CloudSkill-local-eval-review-latest.zip`
plus timestamp bundle
`CloudSkill-local-eval-review-local-review-20260809-180816.zip` (both SHA-256
`815370cd6b233437299c916629a4a010332d8018c58ff38b2578141046e362bb`).
Pipeline SUCCESS, evaluation gate PASS, routing 15/15; R07 Behavior 3/3 PASS at
archived scores 82.7/85.0/92.0 (average 86.6), no refinement.

**RED 1 — demonstrated grader false negative.** All three Claude outputs had
numbered bold Markdown fault-injection scenarios with `Expected:` outcomes, but
`verification-scenarios` scored 0/8 on all three. The regex recognized plain
numbered imperative scenarios but not this equally valid format. Added the exact
format family and a negative control to the existing precision regression
fixture. Re-grading preserved raw evidence, without a new model call, now yields
90.7/93.0/100.0 (average 94.6).

**RED 2 — semantic safety is not deterministic coverage.** Independent Luna and
Sol judges agreed that current keyword/proximity grading cannot determine whether
an epoch issuer really prevents split brain, a late completion can overwrite a
newer attempt, physical evidence is valid, or a generic topology was over-assumed.
They differed on Claude's release label (`MANUAL_REQUIRED` versus semantic
`FAIL`), which is itself evidence for explicit adjudication rather than score
averaging. No equipment Skill was changed: its existing contract already owns
these safeguards, and one n=1 answer is not proof of a Skill defect.

**RED 3 — multi-model process was implicit.** `developing-skills` and
`runtime-evaluation-engineering` mentioned second-model/semantic review but did
not specify blinded evidence packets, role separation, adaptive 2x2 escalation,
safety vetoes, disagreement capture, or stop conditions. Added behavior cases
that reproduce this gap, an adaptive role-separated workflow, and a review
template section. The protocol uses independent sanitized extraction, RED and
owner selection, one minimal patch, blinded judges and adjacent controls, then
mechanism-level adjudication. Multi-model agreement alone is never GREEN.

**Evidence lineage.** Behavior reports now persist input and rubric SHA-256
values. This prevents archived 78-point reports and later 100/84 offline regrades
from being reported as new model behavior. Provider results remain separate and
all comparative conclusions are limited to R07, the only live Behavior case.

**Claude-led symmetry.** The user required the same process to work when Claude
is the coordinator. Added a host-neutral execution contract: Claude Code may
launch Codex CLI judges/extractors and Codex may launch Claude CLI workers, with
least capability, an immutable allowlisted packet, unique per-worker outputs,
canonical returned-model evidence, and truthful `BLOCKED`/degraded-panel states.
Only read-only work is parallel; the stable Runtime Eval ZIP and repository or
release mutations retain one owner. This capability is not claimed for
claude.ai/Desktop or another surface without subprocess evidence.

The live 2x2 experiment used Luna, Sol, Claude Sonnet 5, and Claude Opus 5.
All four found Codex's R07 output stronger or free of a blocking semantic defect,
and all found Claude's cross-host local epoch-store assumption at least
ambiguous. Sonnet returned Claude PASS while Luna/Opus required manual review
and Sol treated it as semantic failure. The adjudicated result is
`MANUAL_REQUIRED` for Claude n=1 semantic safety despite deterministic coverage
PASS; disagreement is preserved rather than averaged away.

Focused validation performed before the full release suite:

- `scripts/validate_behavior_runtime_evals.py`: PASS.
- `scripts/validate_behavior_evals.py`: 98 contracts / 19 Skills, PASS; this is
  structural case validation, not model behavior execution.
- Claude preserved raw regrade: 3/3 PASS, average 94.6, input/rubric hashes
  recorded under `/tmp`; no new provider call.
- Full repository and install checks are recorded separately in the 5.8.0
  release evidence: `scripts/run_all_checks.py` PASS, including lifecycle,
  packaging, Codex/Claude smoke install, provider/contract, portability,
  handoff, and interaction-capture validation.
- The first sandboxed publish preflight could not read the macOS keyring and
  reported an invalid token. The user re-authenticated; keyring-capable preflight
  then confirmed the active account, required scopes, repository access, and
  default branch. No failed preflight was misreported as a push or PR.
- Commit `a869f74` was pushed to
  `feat/multimodel-skill-evaluation-20260809`; PR #2 passed both GitHub
  `validate` checks and merged normally as `348063d`. The official
  non-draft/non-prerelease `v5.8.0` GitHub Release was published from `main` at
  2026-08-09T10:41:15Z. The remote feature branch remains intentionally
  undeleted.

## 2026-08-09 — First live Codex evidence, retired CLI flag fixed, second-round grader precision hotfix

First-ever live Codex Runtime Eval in this repository's history (confirmed
by earlier static-only investigation: `codex_eval_adapter.py` had existed
since commit `61f33c3` but no run directory or change-history entry ever
recorded a real `provider: codex` execution).

**Retired CLI flag.** First attempt: all 5 routing cases failed in ~100ms
(too fast to be a real model call) with `CodexCLIError: unexpected argument
'--ask-for-approval' found`. `codex --version` confirmed `codex-cli 0.147.0`;
`codex exec --help` confirmed `--ask-for-approval` no longer exists in this
version (superseded by `-s/--sandbox <read-only|workspace-write|
danger-full-access>`, which the adapter already passed). Fixed by removing
the retired flag from `codex_eval_adapter.py`'s command construction.
Verified with one cheap manual `codex exec` smoke call (a two-word prompt,
not the full case suite) before re-spending eval quota. Also fixed
`validate_codex_eval_path.py`, which had been asserting the now-removed flag
as a required marker, and added a negative check so `--ask-for-approval`
cannot silently reappear.

**Second live run: SUCCESS.** Routing 5/5 (100%). R07 Behavior: raw 78.0/100,
gate PASS, no refinement attempted (matches `refinement_default: "skip"` for
hosted-agent providers). Contract ID/fingerprint consistent with Ollama and
Claude.

**Second-round grader precision hotfix**, found by reading this real Codex
output against its own rubric before assuming a content gap: the answer
contains 12 well-written, numbered, imperative fault-injection scenarios
("1. Disconnect a chamber IPC... Expect quarantine...") and an explicit
"Authority matrix" table assigning per-concern ownership — both textbook
examples of what `verification-scenarios` (0/8) and `state-authority`
(partial 2/3) are meant to detect, but:

- `verification-scenarios` only recognized `test that X` / `inject a X`
  phrasing, not a numbered `N. <imperative verb> ... Expect ...` scenario
  style. Added `\b\d{1,2}\.\s+[A-Z][a-z]+.{0,200}?\bExpect\b` as a third
  alternative.
- `state-authority` group 1 only recognized `authoritative state`/`state
  authority`/`owns the state` phrasing, not an `Authority matrix`/`sole
  authority` table. Added both as alternatives.
- `reconnect-reconciliation` matched all 3 required groups but still scored
  "partial" because `max_span: 800` was too tight for a long, well-organized
  answer that legitimately discusses reconnect and reconciliation-before-new-
  work in different sections rather than one paragraph (computed minimal
  real span: 1673 characters). Widened to `max_span: 2000` (~13.5% of the
  14.7K-character document, still a real proximity constraint, not
  "anywhere in the document").

Re-graded the already-captured raw output from all three providers with no
new model call:

| Provider | Before | After |
|---|---:|---:|
| Codex (this run) | 78.0 | **100.0** |
| Ollama (repeat=3 avg) | 79.8 | **83.8** |
| Claude (n=1) | 78.0 | **84.0** |

Consistent improvement across three independently-run, architecturally
different providers is strong evidence this was grader precision, not
content quality -- exactly the same conclusion and fix pattern as the first
grader-precision hotfix earlier today, now for a third and fourth criterion.
Extended the existing `validate_behavior_runtime_evals.py` regression
fixture (rather than adding a new one) to cover `state-authority` and
`verification-scenarios` alongside the original two criteria, confirmed RED
against the pre-fix rubric and GREEN against the fix.

Answers the user's question "should we refine [the model output]?": no --
refining would have rewritten already-strong answers to chase a score the
grader was wrongly withholding. Fixing the grader was the earlier failing
layer.

Validation performed:

- `python3 scripts/run_all_checks.py` passes.
- RED confirmed against the original (pre-fix) rubric using the real
  captured Codex output before editing; GREEN confirmed after.

## 2026-08-09 — Git-based Eval Inbox exchange between machines

Requested by the user: they capture real subagent-development patterns on
a work laptop (running Codex), have not yet distilled them (deferred to
Monday, when usage quota resets — not a machine/network restriction as
initially assumed), and want to move candidates via Git specifically, not
manual file transfer, so the exchange works "cross-agent, cross-session"
regardless of which machine/tool captured them.

Corrected assumption before designing anything: the work laptop *can*
reach the CloudSkill repository (the user corrected this directly). That
does not solve the transport problem — `.local/eval-inbox/` is gitignored
on every clone, by design (candidates are unreviewed evidence, never
committed to CloudSkill itself), so two machines both having repository
access still leaves captured candidates stranded on whichever machine
captured them.

Change:

- Added `scripts/sync_eval_exchange.py`: `--push` zips new
  `candidates/`/`manual-review/` files (same format
  `export_eval_candidate.py` already produces) and commits+pushes them to a
  separate, user-owned private Git repository (`eval_exchange_repo` in
  `.cloudskill/config.local.json`/`~/.cloudskill/config.json` — transport
  only, never CloudSkill's own repository), then moves the source files
  into a new `eval_inbox/synced/` folder (never deleted, mirrors the
  existing `processed/`/`rejected/` bookkeeping pattern). `--pull` copies
  any zip not already reflected in `eval_inbox/imports/processed/` into
  `eval_inbox/imports/`, ready for the existing
  `scripts/import_eval_candidates.py` unchanged.
- Deliberately did not duplicate `import_eval_candidates.py`'s validation/
  sanitization/dedup logic into the new script: `--pull` only moves zips
  into `imports/`; the existing import tool still does all the real
  decision-making, so the git-transport layer is additive, not a second
  code path to keep in sync.
- Added `eval_exchange_repo` (optional) to
  `config/cloudskill-config.template.json`.
- Added "Git-based transport between machines" to
  `.agents/skills/developing-skills/references/interaction-eval-capture.md`
  and INSTALL.md section 8d, both pointing out explicitly that "both
  machines can reach the CloudSkill repository" is not sufficient — this
  was the actual misunderstanding being corrected.
- Extended `scripts/validate_interaction_capture.py` with a full push ->
  pull -> import round trip through a real local bare Git repository
  (standing in for a private GitHub exchange repo, no network access
  needed) plus an idempotent-re-pull check, mirroring the manual
  verification performed first.

Validation performed:

- Manual end-to-end verification first, before writing the permanent test:
  a temp bare Git repo simulating GitHub, a "source machine" config with a
  pre-seeded candidate, `--push`, a separate "dest machine" config,
  `--pull`, then `import_eval_candidates.py` — confirmed the candidate
  correctly reached `manual-review/` and the source `candidates/` queue was
  cleared into `synced/`. Confirmed idempotent re-pull reports "Nothing new
  to pull" rather than re-processing.
- Same round trip then encoded as a permanent automated test in
  `scripts/validate_interaction_capture.py`, using real `git init --bare`/
  `clone`/`push`/`pull` subprocess calls, not mocked.
- `python3 scripts/run_all_checks.py` passes.

Explicitly NOT done: no real GitHub (or other hosted Git) exchange
repository has been created or used — the round trip is proven against a
local bare repository only. The user has not yet created their actual
exchange repository or run this against real work-laptop-captured
candidates; that is explicitly deferred to Monday.

## 2026-08-09 — Platform/surface support matrix, formalized architecture-parity rule

Requested by the user: confirm and formalize CloudSkill's real Windows/Mac +
Codex/Claude Code CLI install coverage, then treat Claude Desktop/claude.ai
web upload and Google Gemini as new install targets to design for (Gemini
verification explicitly deferred at the user's request — "1,2,3 4就不用了").

Investigated before writing anything (not assumed):

- Windows PowerShell + macOS/Linux `install.sh`/`install.ps1`, for both
  Codex and Claude Code, plugin-marketplace and standalone modes, were
  already real and documented (INSTALL.md sections 2-6). Nothing to build
  here, only confirm.
- Web research (WebSearch/WebFetch against Anthropic's and Google's own
  docs, not memory) found: claude.ai/Claude Desktop upload custom Skills as
  one zip at a time via Settings/Customize -> Skills, require the skill
  folder itself at the zip root (`<skill-name>/SKILL.md`), do **not** sync
  Skills across claude.ai/API/Claude Code, and run Skills in a sandboxed VM
  with different filesystem/network access than Claude Code CLI. Confirmed
  no CloudSkill skill name violates Anthropic's reserved-word (`claude`,
  `anthropic`) or length constraints. Gemini CLI's own docs state
  `.agents/skills/` — CloudSkill's existing canonical directory — is a
  supported interoperable alias referencing the same Agent Skills open
  standard; not independently verified against a real Gemini CLI session,
  as the user explicitly deferred that step.

Change:

- Added `config/skill-portability.json`: classifies every Skill `portable`
  (no CloudSkill-repository dependency), `hybrid` (portable judgment, some
  CLI-only workflow steps), or `cli-only` (excluded from sandboxed
  packaging). Only `local-runtime-eval-debugging` is `cli-only`;
  `developing-skills` is `hybrid` (its interaction-capture/export workflow
  steps invoke repository scripts); the other 17 are `portable`.
- Added `scripts/package_surface_skills.py`: packages each eligible Skill as
  a claude.ai/Desktop-structured zip (skill folder at archive root) into
  `.local/surface-packages/` (gitignored, matching how every other generated
  bundle in this repository is treated).
- Added `scripts/validate_skill_portability.py`: re-scans every
  `portable`-tier Skill's own files for CloudSkill-repository-relative
  references and fails if found (the safety-critical direction — a
  `portable`-tagged Skill must not actually depend on repository tooling);
  actually runs the packaging script against a temp directory and checks
  each zip's real internal structure against Anthropic's documented
  requirement, rather than only validating the classification data;
  confirms a `cli-only` Skill is never packaged by a default run; confirms
  every classified Skill is mentioned in the human-readable matrix doc so
  it cannot silently drift. Confirmed the "portable must not reference CLI
  tooling" check is real by testing it against a deliberately misclassified
  `local-runtime-eval-debugging` (correctly flags 3 file hits).
- Added `docs/PLATFORM_SUPPORT_MATRIX.md`: the authoritative record of what
  is verified, documented-but-unverified, or not attempted, per
  platform/interface combination.
- Added INSTALL.md sections 10b (Claude Desktop/claude.ai) and 10c (Gemini
  CLI), pointing to the matrix doc rather than duplicating its content.
- Formalized two of this session's own retrospective principles into
  `developing-skills/SKILL.md` as an explicit rule and two "common mistakes"
  entries, so they are enforced going forward rather than only living in
  chat history and this change log: (1) a new instance of an
  authoritative-contract pattern is not complete until it reaches the same
  anti-drift mutation-test rigor as its closest existing sibling; (2) a fix
  that adds a new validator/import path must be checked for whether its own
  side effects can reintroduce the class of problem it was meant to
  prevent.

Validation performed:

- `python3 scripts/run_all_checks.py` passes, including the new validator.
- Manually packaged a portable, a hybrid, and (with `--include-cli-only`) a
  cli-only Skill and inspected the resulting zip structure directly with
  `unzip -l` before trusting the automated structural check.
- Confirmed the portability-drift check is real (RED against a deliberately
  misclassified Skill) before relying on it.

Explicitly NOT done:

- Gemini CLI compatibility was not installed or tested — deferred at the
  user's explicit request this round.
- No zip produced by `package_surface_skills.py` has been uploaded to a real
  claude.ai/Desktop account. The structural check proves zip *shape*; it
  does not prove the Skill *behaves* correctly once loaded into Anthropic's
  sandboxed VM.

## 2026-08-09 — Project-history-derived Eval capture

Requested by the user: after a whole-session retrospective (problems
encountered + distilled principles, mirroring the earlier ChatGPT-handoff
comparison but scoped to this session), design and add a capability where,
inside any project with CloudBox installed (a downloaded open-source repo or
the user's own), the user can tell Codex/Claude to analyze commit history,
architecture, docs, and code, and export the result as skill-optimization
candidates — the same output pipeline as interaction capture, but sourced
from a whole project instead of a live interaction.

Design decision (confirmed with the user before implementing): reuse
`developing-skills`' existing "conversation-derived-optimization" ownership
rather than create a new Skill — its evidence boundary already explicitly
listed "connected repository files, issues, pull requests, and release
history" as an allowed source; this only needed a documented workflow for
that source, not new architecture or ownership. Two design forks confirmed
with the user: (1) a new dedicated trigger phrase rather than overloading
`整理成正向/負向案例` with a source-type parameter; (2) auto-bounded scope by
default (agent picks significant commits by signal), user-overridable,
rather than always asking for an explicit range first. Trigger phrase itself
was iterated live with the user from an initial proposal to
`從專案提煉優化案例`, converging on grammatical consistency with the existing
two phrases (imperative, no "幫我", ends in "案例" — the term used everywhere
else in this pipeline, e.g. `INTERACTION_EVAL_CANDIDATE`) while adopting the
user's preferred verb.

Change (pure documentation/workflow — no new scripts, no model calls,
entirely reuses infrastructure already built this session):

- Added "Project-history mining" to
  `.agents/skills/developing-skills/references/conversation-derived-optimization.md`:
  auto-bounded scope algorithm (cheap overview first — tags/CHANGELOG/ADRs —
  then rank commits by signal, cap detailed reading, state what was
  excluded), confidence discipline (`inferred`/`unknown` only, never
  `observed` — commit history doesn't reveal actual reasoning), third-party
  attribution caution (cites `skill-authoring-sources.md`), and output
  format (same `capture_eval_candidate.py`/`export_eval_candidate.py`
  pipeline plus one `EVAL_MINING_REPORT.md`-based summary per mining pass,
  candidates prefixed `[project-history]` for reviewer filtering).
- Added the trigger phrase and workflow summary to
  `.agents/skills/developing-skills/SKILL.md` and `AGENTS.md` (the
  cross-cutting instruction that propagates to every installed project via
  the managed guidance block).
- Added INSTALL.md section 8c documenting the trigger and workflow for
  end-user discoverability, parallel to section 8 (interaction capture) and
  8b (disconnected-session export).
- Extended `scripts/validate_interaction_capture.py` to check the trigger
  phrase and required workflow markers are present in all four files, so
  this documentation cannot silently drift out of sync the way earlier
  literal-marker validators did before the shared-contract pattern existed.

Validation performed:

- `python3 scripts/run_all_checks.py` passes.
- No live mining run was performed — this increment is the documented
  workflow only; the first real use (against either a downloaded
  open-source project or the user's own) is what actually confirms it.

Explicitly NOT done: did not add a new candidate JSON schema field to
formally distinguish project-history-derived candidates from
interaction-derived ones (the `[project-history]` `task_summary` prefix
convention was judged sufficient and avoids touching the validated
`capture_eval_candidate.py`/`export_eval_candidate.py` schema logic for a
non-enforced distinction).

## 2026-08-09 — Provider registry mutation tests + decoupled Behavior repeat count

Requested by the user: after comparing a handoff document exported from an
earlier ChatGPT/Codex session against this session's actual work, do the
remaining non-model-call items first — (1) the provider registry lacked the
positive-propagation/negative-drift-injection mutation test pair that
document calls the single most valuable pattern in the whole project (it
already exists for the Behavior output contract, not for the newer provider
registry), and (2) `run_local_eval_review.py` hard-codes R07 Behavior to
`--repeat 1`, blocking merge criterion 4 (Behavior repeat>=3) even when the
top-level `--repeat` flag is set to 3.

Change:

Provider registry mutation tests (`scripts/validate_providers_contract.py`):

- **Positive propagation** (static, not live-execution, because a
  `--provider` argparse `choices` tuple is baked into the parser once per
  process — unlike the Behavior contract's prompt text, which re-renders
  live at runtime and can be compared directly): parse
  `run_runtime_evals.py`/`run_local_eval_review.py` with `ast` and require
  every `--provider` `choices=` expression to reference
  `providers_contract.PROVIDER_IDS` symbolically, not a copied tuple. This
  is the actual guarantee that adding/removing a provider in `providers.json`
  propagates without editing either consumer.
- **Negative drift injection**: scan every `scripts/*.py` (except the two
  validators that legitimately quote it as a documented anti-pattern
  string) and `cloudskill-resume`'s case statement for the exact stale
  literals this session already hand-fixed once —
  `choices=("ollama", "codex")` and the equivalent 3-provider copy, plus
  `cloudskill-resume`'s old `ollama|codex)` case pattern.
- Verified both are real tests, not decorative: extracted the pre-Claude
  version of `run_local_eval_review.py` (`git show 7d37a53~1:...`) and
  confirmed the negative-drift check flags it (RED) while the current file
  passes cleanly (GREEN); confirmed the positive-propagation check's exact
  extraction function also flags the old file's hand-typed
  `('ollama', 'codex')` tuple.

Decoupled Behavior repeat count:

- Added `--behavior-repeat N` to `run_local_eval_review.py`, independent of
  `--repeat` (which only ever threaded to routing). Default stays `1` —
  identical behavior to every prior run — so this is additive, not a
  default-cost change.
- Threaded `--behavior-repeat` through `cloudskill-resume` too, so it is
  reachable through the safe commit/push path, not only by calling
  `./cloudskill-eval` directly. Two safety details: (a) rejected in
  combination with `--provider codex`/`--provider claude`, since those
  routes go through the intentionally-fixed quota-conscious smoke wrappers;
  (b) implies `--force-eval`, because the existing source-hash ZIP-reuse
  check has no way to know a reusable completed ZIP was produced with a
  different Behavior repeat count, and would otherwise silently reuse stale
  n=1 evidence.
- Recorded `routing_repeat`/`behavior_repeat` in `STATUS.json` and
  `REVIEW_SUMMARY.md` so a future reviewer can see the repeat count a bundle
  represents without reading `run.log`.

Validation performed:

- `python3 scripts/run_all_checks.py` passes.
- `./cloudskill-resume --behavior-repeat 3 --provider codex --status` and
  `--behavior-repeat abc --status` both fail fast with a clear message,
  before touching any model or the Runtime Eval lock.
- `./cloudskill-resume --behavior-repeat 3 --status` (default ollama)
  passes through cleanly and correctly reports the implied `--force-eval`.

Explicitly NOT done this increment: no model was called. The Behavior
repeat>=3 evidence this unblocks, and the Codex live comparison, are still
open — see "Latest verified evidence" and Open evolution items.

## 2026-08-09 — First live Claude/Ollama Runtime Eval confirmation + real adapter bugs found and fixed

Requested by the user: actually run the `ollama` and `claude` providers (not
just static validation) and fix whatever the live evidence surfaces.

Observed and fixed, in order, all against real live processes:

1. **`/no_think` leaked into the Claude behavior prompt.** First live
   `./cloudskill-eval-claude` run: routing 5/5 passed, but Behavior execution
   failed with `RuntimeError: model output is not JSON: Unknown command:
   /no_think`. Root cause: `runtime_eval_common.py::_behavior_user_prompt()`
   unconditionally prepended `/no_think` (a Qwen3/Ollama thinking-mode
   directive) to every provider's behavior user prompt. Ollama treats it as
   literal text; Claude Code CLI's `-p` stdin parser treats a leading
   `/word` as an attempted slash command, which does not exist, and errors
   before the real prompt is even read. Fixed by removing the directive from
   the shared, provider-neutral prompt builder and moving it into a new
   `ollama_user_prompt()` helper applied only inside `call_ollama()` /
   `prompt_request_payload()`'s Ollama branch in `run_runtime_evals.py`. The
   Ollama-only refinement prompt builder in `run_local_eval_review.py` still
   has its own `/no_think` prefix, unchanged — that path is already
   Ollama-exclusive via `refinement_default(provider) == "auto"`.
2. **Occasional `stop_reason: tool_use` / `error_max_structured_output_retries`
   on Claude.** Second live run (after fix 1): routing 4/5 passed; R05C
   failed with the Claude CLI reporting `"errors":["Failed to provide valid
   structured output after 5 attempts"]` after the model attempted a tool
   call. A same-config retry then passed 5/5 routing + behavior cleanly,
   confirming it was not a hard block, but the unnecessary tool-call attempt
   was wasting the CLI's own structured-output retry budget. Root cause:
   unlike `codex_eval_adapter.py`, `claude_eval_adapter.py` never told the
   model it was in a no-workspace-access controlled evaluation, so the model
   occasionally tried a tool anyway even though `--tools ""` had already
   disabled all built-in tools. Fixed by (a) framing the piped prompt with
   the same "do not inspect the workspace, do not use any tool" instruction
   Codex's adapter already uses, and (b) adding `--permission-mode
   acceptEdits` so a non-interactive session cannot stall/error on a
   permission prompt it has no way to answer (the ephemeral empty directory
   has nothing real for an accepted edit to affect).

Validation performed:

- `python3 scripts/run_all_checks.py` passes after each fix.
- Re-ran `./cloudskill-eval-claude` after the fixes: routing 5/5, Behavior
  raw score 78.0/100, **gate PASS outright, no refinement needed** —
  `final-answer-discipline` and `assumptions-unknowns` both scored full
  marks (the R07 grader precision hotfix from earlier today confirmed
  correct against a second, independent real model's output, not just
  Ollama's).
- Contract ID/fingerprint (`behavior-final-json-v1` /
  `07fe9878330232f9fa2e85dba40a97860402c2be7d33ad74b33e7c82aedf5166`)
  confirmed consistent in the Claude run's `environment.json`, matching
  Ollama/Codex.
- Ollama `--force-eval` run launched separately (see next entry once it
  completes) — the two providers cannot run concurrently by design
  (`run_local_eval_review.py`/`run_runtime_evals.py` process-presence check
  refuses a second Runtime Eval while one is active); confirmed this
  correctly deferred rather than corrupting either run.

The separately-launched Ollama `--force-eval` run then completed:
`CloudSkill-local-eval-review-local-review-20260809-134358.zip`. Routing:
15/15 (3 repeats x 5 cases), strict pass 100%, all four case groups 3/3.
Raw R07 Behavior: 78.0/100, gate PASS outright, no refinement needed —
matching the live Claude run's score exactly and consistent with the
grader-precision hotfix's offline re-grade of the earlier 74/88 bundle.

Unresolved:

- Both providers' Behavior evidence above is still n=1, not n=3. Discovered
  why while pushing for repeat>=3 Ollama evidence: `run_local_eval_review.py`'s
  `behavior_command` hard-codes `--repeat 1` independent of the top-level
  `--repeat` flag (which only threads to the routing command). Routing
  repeat>=3 is real; Behavior repeat>=3 needs a decoupled `--behavior-repeat`
  option (or a direct `run_runtime_evals.py --eval-kind behavior --repeat 3`
  invocation outside the packaged bundle format) before merge criterion 4 is
  actually satisfiable through the standard tooling.
- The `error_max_structured_output_retries` failure mode is now
  substantially less likely (0 failures in 6 calls after the fix, versus 1
  failure in 11 calls before it) but not proven impossible; keep the error
  message from `claude_eval_adapter.py` distinguishable in future review so
  a recurrence is classified as provider/CLI reliability, not a
  Skill/Behavior-contract defect.

## 2026-08-09 — Eval Inbox import path and disconnected-session candidate export

Requested by the user: a unified local folder to drop exported archives from
external sessions where this Skill set is installed but no CloudSkill
repository is reachable, a convenient way to collect that data (asked
whether a new "collect data" Skill was the right shape or something more
convenient existed), and merge-to-main guidance for the ongoing optimization
work.

Change:

- Initialized `.local/eval-inbox/` in this repository via the existing,
  already-validated `scripts/install.sh --config-only` (self-referential:
  `.cloudskill/config.local.json` points at this repository itself). Added
  `imports/` and `imports/processed/` to the documented Inbox structure —
  these two folders complete the `eval-outbox/` concept that
  `scripts/install.sh`/`scripts/install.ps1` had already reserved in their
  generated per-project `.gitignore` but never implemented.
- Added `.agents/skills/developing-skills/assets/export_eval_candidate.py`:
  a self-contained (stdlib-only, no CloudSkill-repository import) exporter
  that ships with the installed Skill. It performs the same structural
  validation and sanitization scan as `scripts/capture_eval_candidate.py`,
  writes into a config-free `.cloudskill/eval-outbox/` in the current
  project, and packages the result into one timestamped zip. Chose to
  extend the existing `developing-skills` capture flow (`整理成正向/負向案例`)
  with a config-free fallback rather than create a new Skill, per the "do
  not create a new Skill until an existing owner is ruled out" rule — the
  user still says the same two phrases in an external session; the only
  change is which script the Agent picks based on whether a CloudSkill
  repository config resolves.
- Added `scripts/import_eval_candidates.py`: scans `<eval_inbox>/imports/`
  for zips, re-validates every candidate with the same rules as
  `capture_eval_candidate.py` (imported directly, since this tool only ever
  runs inside the CloudSkill repository), re-scans against this machine's
  own private `sensitive-terms.local.txt`, de-duplicates by content hash
  against everything already in the Inbox, and files each candidate into
  `candidates/`, `manual-review/`, or `rejected/`. Moves processed zips to
  `imports/processed/` (never deletes the source archive). Never touches
  formal `evals/`, Skill files, or Git state.
- Extended `scripts/validate_interaction_capture.py` with a constant-drift
  check (`ALLOWED_KINDS`/`PROHIBITED_KEYS`/`SENSITIVE_PATTERNS` must match
  between `capture_eval_candidate.py` and `export_eval_candidate.py`) and a
  full export -> zip -> transfer -> import round-trip smoke test, including
  confirming a no-reachable-terms export conservatively lands in
  `manual-review/`, and that re-running import with nothing new is a no-op.
- Updated `.agents/skills/developing-skills/SKILL.md`,
  `references/interaction-eval-capture.md`, `AGENTS.md`, and `INSTALL.md`
  (new section 8b) to document the disconnected-session path and where to
  physically drop the transferred zip.
- Added an explicit, enumerated "Release / merge-to-main criteria" section
  to `CLOUDSKILL_AGENT_HANDOFF.md` — this had previously only been referenced
  as "the current release criteria" without a concrete checklist.

Validation performed:

- Manual end-to-end smoke test (export with no sensitive-terms file ->
  `MANUAL_REQUIRED`; export with a clean local terms file -> `PASS`; hand-
  crafted malformed candidate inside a zip -> `rejected/`; re-export of
  identical content -> detected as a duplicate on import) before encoding it
  as the permanent automated test in `validate_interaction_capture.py`.
- `python3 scripts/run_all_checks.py` passes in full.
- Test candidates/zips created during manual verification were deleted from
  `.local/eval-inbox/` before commit; the Inbox ships empty and ready for
  real captures.

Explicitly NOT done:

- No formal `evals/` case was created from this work; the Inbox import path
  only stages candidates for a later, separate, explicit batch-review.
- Did not merge PR #1 to `main` — see the new "Release / merge-to-main
  criteria" section; several criteria (R07 repeat >= 3, Codex/Claude live
  comparison) are not yet satisfied.

CI caught a second real gap in this increment: the pushed `SKILL_MANIFEST.json`
recorded `developing-skills` `file_count: 17`, but GitHub Actions regenerated
it from a clean checkout as `16` and failed `git diff --exit-code`.

First diagnosis (incomplete): a stray `__pycache__/` under
`.agents/skills/developing-skills/assets/` from a manual `py_compile` smoke
test inflated the count picked up by `scripts/validate_pack.py` (the actual
`SKILL_MANIFEST.json` writer; `manage_skill.py refresh --all` does not touch
`file_count`). Deleting the cache and recommitting `file_count: 16` looked
like the fix, but the very next `./cloudskill-resume` run silently
regenerated `17` again and committed it — because the real, recurring source
was the new drift check in `scripts/validate_interaction_capture.py`, which
imports `capture_eval_candidate.py`/`export_eval_candidate.py` via
`importlib` and writes bytecode cache back into that same skill's `assets/`
directory as a side effect on *every* `run_all_checks.py` run. `validate_pack.py`
runs first in the check sequence and snapshots whatever is on disk from the
*previous* run — so the two validators oscillated the manifest between 16
and 17 depending on run order, and one clean-looking manual fix could not
hold.

Root-caused and fixed at both ends instead of re-committing the number a
third time:

- `sys.dont_write_bytecode = True` in `scripts/validate_interaction_capture.py`
  before its `importlib` calls, so it stops creating the cache in the first
  place.
- `scripts/validate_pack.py`'s per-skill `file_count` now excludes
  `__pycache__`, `.pyc`, and `.DS_Store` defensively, so any *other* future
  transient artifact cannot cause the same run-order-dependent oscillation.

Confirmed stable by running `run_all_checks.py` twice in a row with no
cleanup in between and diffing `SKILL_MANIFEST.json` — identical both times,
and no `__pycache__` reappeared under the skill's `assets/` directory.

## 2026-08-09 — Claude Code CLI Runtime Eval provider + provider registry

Requested by the user: run Codex-provider Evals with GPT (already true, via
Codex CLI), run a new Claude provider with Claude models, keep local at
Ollama for now, and make the local family easy to extend later.

Change:

Provider registry (mirrors the Behavior-output-contract precedent: one
authoritative JSON contract + one executable adapter + one drift Validator):

- Add `evals/runtime/contracts/providers.json` declaring `ollama` (family
  `local`), `codex` (family `hosted-agent`, GPT via Codex CLI), and `claude`
  (family `hosted-agent`, Claude via Claude Code CLI), plus
  `required_consumer_paths` and an extension guide for adding a fourth
  provider later.
- Add `scripts/providers_contract.py` (`PROVIDER_IDS`,
  `LOCAL_PROVIDER_IDS`, `HOSTED_AGENT_PROVIDER_IDS`, `get_provider`,
  `refinement_default`).
- Add `scripts/validate_providers_contract.py`: validates contract shape,
  that every hosted-agent adapter exports `<name>_preflight`/
  `call_<name>_cli`, that every local adapter's declared `call_site` function
  exists, that every Python consumer imports `providers_contract`, and that
  the shell-based `cloudskill-resume` (which cannot `import` Python) contains
  every registered provider ID literal.

Claude Code CLI adapter (mirrors `scripts/codex_eval_adapter.py`):

- Add `scripts/claude_eval_adapter.py`: `claude_preflight()` (`claude
  --version` + `claude auth status`) and `call_claude_cli()`, which runs
  `claude -p --output-format json --safe-mode --tools "" --no-session-persistence
  --strict-mcp-config --system-prompt <system> [--model <alias>]
  [--json-schema <schema>]` from an isolated empty temporary directory, piping
  the user prompt over stdin. `--safe-mode` and `--tools ""` were confirmed to
  exist via `claude --help` before writing this adapter (not guessed).
- Add `cloudskill-eval-claude`, a quota-conscious `--repeat 1 --no-refine`
  smoke wrapper mirroring `cloudskill-eval-codex`.
- Wire `--provider claude` / `--claude-model` through
  `scripts/run_runtime_evals.py` (`call_model`, `resolve_model_label`,
  `prompt_request_payload`, `dry_run_plan`, preflight dispatch),
  `scripts/run_local_eval_review.py` (`requested_model`,
  `runtime_provider_args`, environment preflight, refinement eligibility now
  driven by `refinement_default(args.provider)` instead of a hardcoded
  `== "ollama"` check), and `cloudskill-resume` (`--provider`/`--claude`
  flag, dispatch to `./cloudskill-eval-claude`).
- Extend `scripts/validate_local_eval_debugging.py` and
  `scripts/validate_pack.py` to also require the new Claude files; fix two
  markers in `scripts/validate_codex_eval_path.py` and
  `scripts/validate_local_eval_debugging.py` that hard-coded the pre-refactor
  literal `choices=("ollama", "codex")` / `args.provider == "ollama" and not
  args.no_refine` and would otherwise have gone stale silently.
- Extend `scripts/validate_evolution_handoff.py` and
  `CLOUDSKILL_AGENT_HANDOFF.md` to require/document a
  `./cloudskill-resume --provider claude --force-eval` continuation command.

Validation performed:

- `python3 -m py_compile` on every new/changed module.
- `--dry-run` smoke test of `scripts/run_runtime_evals.py` for all three
  providers (`ollama`, `codex`, `claude`) confirming correct dispatch and no
  stray output files.
- Confirmed the two stale-marker Validators genuinely failed (RED) before the
  fix and passed (GREEN) after.
- `python3 scripts/run_all_checks.py` passes in full.

Explicitly NOT done:

- No live `claude`, `codex`, or `ollama` model call was made. The
  `--output-format json` result-field parsing in `claude_eval_adapter.py` is
  grounded in `claude --help` and documented CLI behavior, not in an actual
  executed response — `./cloudskill-eval-claude` is the first point that gets
  confirmed against a real process, and it spends Claude usage/quota, so it is
  deferred until explicitly requested.

Unresolved:

- Run `./cloudskill-eval-claude` (one repeat, no refine) to confirm the JSON
  result-shape parsing against a live Claude Code CLI process.
- `ollama` stayed a local, inline `call_ollama()` in `run_runtime_evals.py`
  rather than moving to `scripts/local_providers/ollama_adapter.py` — the
  registry documents the extension shape but does not force a working path to
  move file location without a second local backend actually needing it yet.

CI caught a real gap in this increment: `cloudskill-eval-claude` was created
but `cloudskill-resume` only stages/commits paths listed in its hardcoded
`FORMAL_PATHS` array, and `cloudskill-eval-claude` was not added to it, so the
first push landed without the launcher file and `validate_pack.py` failed in
GitHub Actions (`missing required file: cloudskill-eval-claude`) even though
every local `run_all_checks.py` pass had been GREEN — local checks run against
the working tree, not the committed diff. Fixed by adding
`"cloudskill-eval-claude"` to `FORMAL_PATHS`, and by extending
`scripts/validate_providers_contract.py` to parse that array and fail when a
registered hosted-agent provider's `smoke_command` launcher is absent from
it — confirmed this check fails against the pre-fix `cloudskill-resume` (RED)
and passes after (GREEN), so the same class of provider-launcher omission is
now caught before push, not by CI after.

## 2026-08-09 — R07 Behavior grader precision hotfix (assumptions/restart false negatives)

Evidence: `CloudSkill-local-eval-review-local-review-20260809-113507.zip`.

Observed:

- Pipeline: SUCCESS, evaluation gate: PASS.
- Routing: strict pass 100%, contract valid 100%, primary accuracy 100%; R02
  now returns `code-review` plus `equipment-domain-modeling` 3/3 (the prior
  R02 regression is resolved).
- R05A/B/C and R07 routing remain 3/3 each.
- Raw R07 Behavior scored 74/100 (below the 75 gate); refined R07 Behavior
  was accepted at 88/100 with no planning-leak (final-answer-discipline
  criterion passed on both raw and refined).

Diagnosed earliest failing layer:

- Deterministic grader (layer 7), not the model or the Skill. Re-reading the
  actual captured raw and refined text against the rubric regexes showed both
  answers already contained a dedicated "Assumptions & Unresolved Inputs"
  section and explicit wafer/occupancy/physical-state restart-reconstruction
  evidence. Two rubric patterns in `assumptions-unknowns` and
  `restart-reconstruction` (case `R07-english-equipment-architecture`) were
  too rigid for realistic formatting:
  - the heading pattern required a bare line start or a Markdown `#`, so a
    numbered (`9. `) or bold (`**Assumptions**`) heading never matched;
  - the inline pattern required singular `assumption:`, so the model's
    natural plural `Assumptions:` never matched;
  - `physical state` required that exact two-word phrase, so `physical/material
    state` (the model echoing the rubric's own label wording) never matched.

Change:

- Widen the two `R07-english-equipment-architecture` rubric patterns in
  `evals/runtime/cases/behavior-rubrics.json` to accept numbered/bulleted/bold
  headings, plural `assumptions:`/`unknowns:`, and `physical[/ ]material
  state` without loosening them into a generic match (still anchored to the
  keyword at/near line start).
- Add an executable regression fixture to
  `scripts/validate_behavior_runtime_evals.py` that grades a positive
  synthetic snippet (must match) and a negative-control snippet (must not
  match) through the real `grade_output` function, so this precision
  regression cannot silently reappear.

Validation performed without a new model call:

- Re-ran `scripts/grade_behavior_evals.py` against the exact captured
  `behavior-raw.jsonl` / `behavior-refined.jsonl` from the
  `local-review-20260809-113507` run directory before and after the patch:
  - raw: 74.0 → 78.0 (now legitimately passes the 75-point gate on its own,
    without refinement);
  - refined: 88.0 → 100.0.
- Confirmed the fixture fails against the pre-patch pattern text (RED) and
  passes against the patched rubric (GREEN).
- `python3 scripts/run_all_checks.py` passes.

Unresolved:

- This is n=1 behavior evidence (one Ollama attempt); the repetition policy
  in `runtime-evaluation-engineering` calls for at least three repeats before
  treating a local-model behavior score as stable. A fresh
  `./cloudskill-resume --provider ollama --force-eval` run is the next
  Ollama-dependent step, deferred at the user's request for this increment.
- Content-fidelity risk in the Refiner: the accepted refined answer replaced
  raw's concrete authority class names (`ChamberStateAuthority`,
  `WaferCustodyAuthority`, `FencingToken`, …) and exact `wafer
  location`/`occupancy` phrasing with vaguer prose. It still passes under the
  corrected grader because it independently states "reconstruct the
  physical/material state", but this narrowed margin is worth watching over
  additional repetitions before deciding whether the Refiner Prompt needs an
  explicit "preserve concrete identifiers from the raw answer" instruction.
- Codex quota-conscious comparison still pending Codex availability.

## 2026-08-09 — Behavior contract consumer registry closure

Observed:

- The shared Behavior output contract and dedicated anti-drift Validator were
  present in the working tree.
- `validate_local_eval_debugging.py` still searched the local review runner for
  the retired literal `json-final-v1`.
- Static validation therefore stopped before Ollama or Codex was called.

Root cause:

- The shared contract centralized Prompt, schema, extraction, and planning
  rules, but it did not yet enumerate every required consumer.
- One adjacent Validator was omitted from the anti-drift migration and could
  retain a copied implementation detail.

Change:

Consumer registry:

- Add `required_consumer_paths` to the authoritative Behavior output contract.
- Register Runtime, Refiner, local Eval validation, and anti-drift validation
  consumers.
- Make `validate_local_eval_debugging.py` execute the shared extraction and
  Refiner Prompt contracts instead of searching for a contract-name literal.
- Make `validate_behavior_contract.py` parse every registered consumer, require
  a shared-contract import, scan all other Validators for retired API names and
  Prompt literals, and compare contract IDs/fingerprints at runtime.
- Add positive contract-propagation and negative injected-drift tests to the
  release package validation.

Expected evidence:

- Editing the authoritative Prompt requirements propagates through Runtime and
  Refiner Prompt assembly without editing Validators.
- Injecting a retired contract literal into another Validator is detected.
- Full static validation reaches the model stage without another contract-copy
  failure.
- One new Ollama Review ZIP is generated and then committed with the complete
  working-tree increment.

Unresolved:

- Interpret the resulting R02/R05/R07 evidence.
- Run the Codex comparison after the available usage pool resets.

## 2026-08-09 — Single-source Behavior output contract and anti-drift validation

Observed:

- The structured Behavior/refinement overlay was applied locally.
- Static validation first failed because one Validator imported the retired
  `extract_final` API.
- After that API was aligned, another Validator still required four copied
  prompt markers from the retired tag-based `<final>` contract.
- No model call occurred in either failure; the earliest failing layer was
  deterministic contract validation.

Root cause:

- Prompt text, JSON schema, extraction rules, refinement rules, planning-leak
  patterns, and Validator expectations had multiple independent copies.
- A format migration could update Runtime code while leaving one or more
  Validators on the old contract.

Change:

- Add one authoritative data contract:
  `evals/runtime/contracts/behavior-output-contract.json`.
- Add one executable adapter:
  `scripts/behavior_output_contract.py`.
- Runtime Prompt, Refiner Prompt, schemas, extraction, minimum lengths,
  planning-leak patterns, contract ID, and contract fingerprint now come from
  that source.
- Add `scripts/validate_behavior_contract.py` to test actual generated prompts,
  schemas, wrappers, structured extraction, strict legacy fallback, and
  planning-leak detection.
- Remove copied Behavior prompt-marker assertions from
  `validate_behavior_runtime_evals.py`.
- Delegate Behavior-contract consistency out of the Codex-path Validator.
- Record contract ID and fingerprint in Runtime Eval evidence.

Expected evidence:

- Static validation passes without looking for retired prompt sentences.
- A contract edit automatically changes both prompts and schemas.
- A consumer that stops importing the contract fails
  `validate_behavior_contract.py`.
- One fresh Ollama Review ZIP is produced before commit/push.
- PR #1 remains Draft until the new Runtime evidence is interpreted.

Unresolved:

- Review the next R02/R05/R07 Routing and Behavior results.
- Run the quota-conscious Codex comparison after availability resets.

## 2026-08-09 — Validator API alignment hotfix

Observed:

- The structured-refiner increment was applied locally.
- Static validation stopped before Runtime Eval because
  `validate_codex_eval_path.py` imported the removed `extract_final` API.
- The production refiner now exposes
  `extract_refined_final(text) -> (value, extracted, contract)`.

Earliest failing layer:

- Deterministic validator compatibility, before any Ollama or Codex model call.

Change:

- Align synthetic refiner checks with `extract_refined_final`.
- Validate structured `{ "final": "..." }`, strict terminal legacy fallback,
  unstructured tag mentions, and non-terminal legacy blocks.
- Continue through `cloudskill-resume --provider ollama` without reapplying
  the already completed evolution overlay.

Expected evidence:

- `scripts/validate_codex_eval_path.py` passes without a model call.
- `scripts/run_all_checks.py` passes.
- One fresh Ollama Review ZIP is produced.
- The complete overlay and this hotfix are committed and pushed together.

Unresolved:

- Interpret the new Routing and Behavior evidence before changing PR #1 from Draft.

## 2026-08-09 — Structured Behavior final contract and durable handoff

Planned increment based on `CloudSkill-local-eval-review-local-review-20260809-101744.zip`.

Observed:

- R05A/R05B/R05C and R07 routing all passed 3/3.
- R02 regressed 0/3 by selecting `equipment-control-architecture` instead of the required `equipment-domain-modeling` support.
- Raw R07 Behavior scored 70.
- Refinement was reported as accepted at 84, but the accepted text still contained planning and did not satisfy a real final-deliverable boundary.

Change:

- Reassert the code-review plus component-state-modeling composition rule for R02.
- Add a dedicated R07 `behavior_prompt` that removes routing-only wording.
- Require structured Behavior output: `{ "final": "..." }`.
- Preserve raw provider output separately from the graded final value.
- Require structured or strict terminal-final refinement output; reject unstructured keyword-rich planning.
- Expand planning-leak detection.
- Add design, flow, history, and agent-handoff documents plus deterministic validation.

Expected evidence:

- R02 returns `code-review` plus `equipment-domain-modeling`.
- R05A/B/C remain unchanged.
- Raw Behavior output contains only the structured final deliverable value after parsing.
- An unstructured refinement cannot be marked accepted.

## 2026-08-09 — Codex Runtime Eval path

Commit: `61f33c39ce9ba4628dd1225ead5df9542bb64d4c`

- Added `cloudskill-eval-codex`.
- Added Codex CLI adapter and provider-aware resume logic.
- Isolated Codex execution in a temporary read-only Git repository.
- Kept Codex authentication and quota failures separate from Skill-quality results.
- Tightened legacy terminal `<final>` extraction.
- Strengthened the R05C composition instruction.
- GitHub Actions passed.

## 2026-08-09 — R05 decomposition and R07 recovery evidence

Commit: `7a67da8a62a4449b09bcd477a2aba23bf2f5a42e`

- Split the ambiguous R05 case into R05A component state contract, R05B recovery ownership, and R05C combined composition.
- Added explicit component-versus-control ownership boundaries.
- Added minimum distributed ownership/recovery evidence.
- Preserved raw and extracted Behavior outputs separately.
- GitHub Actions passed.

## 2026-08-09 — Interruption-safe continuation command

Commit: `fa054afcce6e141f90eb0000dc33a76e2115330b`

- Added `cloudskill-resume`.
- Added provider/process detection, source-hash ZIP reuse, stage logging, commit/push/PR continuation, and stale-lock handling.
- Kept stashes and `.local` evidence outside commits.

## 2026-08-09 — Standardized Skill lifecycle and Runtime Eval engineering

PR: `#1`, initial lifecycle commit series.

- Established `draft -> experimental -> active -> stable -> deprecated`.
- Added per-Skill lifecycle metadata and lifecycle validation.
- Added `runtime-evaluation-engineering`.
- Kept `local-runtime-eval-debugging` focused on host execution, diagnosis, reports, and bundle handoff.
- Fixed canonical routing-evidence retrieval for version-scoped multi-audience reports.
- Separated pipeline success from evaluation-gate success.
- Updated GitHub Actions action versions.

## 2026-08-08 — Local Runtime Eval debugging foundation

Baseline commit: `a060ac9b4f18d137abb52eb3a02d48ba062bd9f1`

- Added one-command local Runtime Eval tooling.
- Added Ollama execution, adaptive context selection, grading, reporting, and uploadable review ZIP generation.
- Established the evidence used by the subsequent lifecycle and evaluation-engineering work.

## Maintenance rule

For each future increment, add a new entry at the top containing:

- date and commit/PR when available;
- observed evidence;
- diagnosed earliest failing layer;
- change made;
- expected or actual validation result;
- unresolved risks and next decision.
