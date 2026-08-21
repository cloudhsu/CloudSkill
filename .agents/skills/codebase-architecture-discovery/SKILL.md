---
name: codebase-architecture-discovery
description: Use when a codebase area is being extended, is unfamiliar, or is suspected of accumulated duplication, and no current architecture map or duplication survey exists for it -- before proposing or executing any specific refactor.
---

# Codebase Architecture Discovery

Read `references/batch-discovery-method.md` before starting a survey of more
than a handful of files.

## Core principle

A codebase this large has not been read end to end recently enough for
anyone to know what actually duplicates what. Find out by reading, not by
grepping for filenames or trusting naming conventions -- then produce a
map durable enough that the next change doesn't have to re-derive it. This
skill owns the *discovery* phase only: it hands off a confirmed cluster and
a recommended target to `safe-incremental-refactoring` for the actual
extraction, the same way `legacy-game-product-archaeology` hands a
reconstructed core loop to `gameplay-core-modernization` rather than doing
the extraction itself.

## Trigger conditions

- A codebase area (a directory, a subsystem, "all of `scripts/`") is about
  to be extended and no current architecture map exists for it.
- A naming convention (`_contract`, `_adapter`, `_service`) is being relied
  on without ever having been checked against what the files actually do.
- Multiple files independently implement what sounds like the same small
  primitive (a subprocess wrapper, a hashing helper, a schema validator) and
  no one has confirmed whether they've already drifted apart.
- Before adding a new cross-cutting helper, per this repository's own
  `AGENTS.md` architecture rule 15.

## Non-trigger conditions

- The specific slice to extract is already known and agreed -- go straight
  to `safe-incremental-refactoring`; re-surveying the whole area first adds
  cost without adding a decision.
- A single, already-decided architecture question needs a recommendation
  between options -- use `architecture-review`.
- The codebase is small enough (a handful of files) that direct reading
  needs no staging discipline of its own.

## Required workflow

1. **Scope and stage the read.** Group the target files by subsystem or
   theme, not alphabetically or by size. Read the largest/most-connected
   files in each batch, not just the smallest ones first -- the small files
   dispose of quickly and defer nothing; the size that actually matters is
   the batch's *thematic* boundary, not any one file's line count.
2. **Checkpoint after every batch into a durable, resumable record** (an
   ExecPlan; see `agent-development-process`'s template) before continuing.
   Record raw observations, not conclusions yet. A crash should lose at
   most one batch, never the whole survey.
3. **Defer cross-file conclusions until enough of the set is read.** A
   single early pattern-match risks exactly the reactive, piecemeal fixing
   this discipline exists to prevent -- an apparent duplicate in batch one
   may turn out to be one of three, with the real extraction target only
   visible once a later batch's superset version is seen.
4. **Verify a plausible duplicate empirically before concluding it is safe
   to merge.** Code that "looks the same" is not evidence; run both
   implementations against real data the codebase actually validates, and
   write targeted adversarial cases for the specific points where they
   could diverge (a type check, a boundary condition) rather than trusting
   that similarity implies equivalence. See
   `references/batch-discovery-method.md` for the exact technique.
5. **Before renaming or removing anything, search the whole tree for its
   exact old name** -- not just whether a module import still resolves.
   `python3 -m py_compile` and an import smoke test both pass while a
   sibling file's own test still calls the old private function by name;
   only a literal grep across the repository catches that.
6. **Produce a maintained architecture map as the artifact**, not a prose
   report alone -- the actual layers, the actual duplication clusters with
   file/function evidence, and the naming convention's real exceptions.
   This is what makes the discovery reusable by someone who wasn't in the
   room, and what a future "read the map first" rule has to point at.
7. **Hand off extraction, don't silently do it as an afterthought.** Once a
   cluster is confirmed, name the recommended target and let
   `safe-incremental-refactoring`'s own slice/verify/rollback discipline
   own the actual merge -- unless explicitly asked to execute it in the
   same pass, in which case follow that skill's workflow for each cluster
   individually, not all of them as one undifferentiated change.

## Required output

1. Confirmed layers/responsibilities, with real file examples, not an
   assumed taxonomy.
2. Every duplication cluster found, each with: the exact files/functions
   involved, whether they are byte-identical or already drifted apart, and
   the specific evidence used to confirm they are (or are not) safe to
   merge.
3. Naming-convention findings: which conventions hold, which files break
   the pattern their own name implies.
4. A recommended target for each cluster (which existing implementation
   becomes the shared one, or a new location) -- not a decision to execute
   it, unless asked.
5. What was explicitly *not* checked, stated as plainly as what was.

## Common mistakes

- Concluding "safe to merge" from code similarity alone, without running
  both versions against real data where they could plausibly disagree.
- Drawing a cross-file conclusion from the first batch instead of holding
  it until enough of the set is read.
- Renaming or removing a symbol after confirming its module import still
  resolves, without a repository-wide search for the exact old name.
- Proposing a new shared-module directory or package before checking
  whether the codebase already has (or deliberately lacks) that structure
  -- a flat codebase's own existing convention is itself evidence about
  where a new shared module belongs.
- Treating a maintained architecture map as a one-time report instead of
  something the next change is expected to read and keep current.
