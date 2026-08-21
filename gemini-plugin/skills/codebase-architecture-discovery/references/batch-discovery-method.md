# Batch discovery method

Distilled from a real full-codebase audit (64 files, ~25,900 lines) that
found and consolidated four independently-duplicated primitives. Every
technique below is what actually worked or actually caught a real mistake
during that pass, not a generic checklist assembled in advance.

## Why staged batches, not one pass and not file-by-file

Reading one file at a time and reacting to each finding immediately
produces exactly the piecemeal, reactive pattern this method exists to
avoid: an apparent duplicate found in the second file read might turn out
to be one of three, and the actual best merge target might be the fourth
file's superset version, seen only much later. Reading the whole codebase
in one unstructured pass, with no checkpoint, risks losing the entire
survey to a session crash or context loss partway through.

The resolution used successfully: group files by subsystem/theme (not
alphabetically, not by size), and after each batch, write raw observations
-- not conclusions -- into a durable, resumable record (an ExecPlan) before
continuing. A crash loses at most one batch. Cross-file conclusions
(**is this actually a duplicate, and what's the right target**) wait until
enough of the set is read to compare batches against each other, the same
discipline a routing-Eval cross-file duplication check already needed.

Concretely, in the source audit: an early batch found a naming-convention
exception (a file named `*_adapter` with zero I/O) and correctly held that
finding open rather than concluding the naming convention itself was
unreliable -- a later batch found the two *correctly*-named `_adapter`
files, confirming the convention was sound and the first file was an
isolated mistake, not a pattern. Concluding from the first batch alone
would have produced the wrong recommendation (loosen the naming rule)
instead of the right one (fix the one mislabeled file).

## Verifying a duplicate is safe to merge

Similarity is not evidence. Two independently-written interpreters,
wrappers, or helpers that "look like they solve the same problem" can have
already drifted on real edge cases -- superficial code review will not
reliably catch this, especially in a long, dense function.

The technique that worked:

1. Read both implementations completely, side by side, not just their
   docstrings or first few lines.
2. Identify the specific points where behavior *could* diverge -- a type
   check with a different set of accepted types, a boundary condition
   applied to `int` but not `float`, an extra feature one version grew that
   the other never had.
3. Run **both** implementations against every real input the codebase
   actually validates or exercises (real schema files, real case data, real
   consumers) and diff the results. Byte-identical output across all real
   usage is real evidence; "they look similar" is not.
4. For each specific divergence point identified in step 2, write a
   targeted adversarial test that isolates it -- even if (especially if)
   nothing in current real data would trigger it. Confirming a divergence
   is real but *unreachable in practice* (because no current schema/caller
   actually exercises that path) is a meaningfully different, and much
   safer, finding than assuming it away.
5. Only after both checks pass does the merge become a mechanical move
   rather than a guess.

This is more work than "they look the same, merge them" -- proportional to
how much a wrong merge would cost. A four-line, byte-identical helper
(example: a chunked file-hashing function) does not need this full
treatment; a recursive interpreter with several structural features does.

## Transitive-consumer search before renaming or removing

Confirming that `import module_x` still resolves, or that
`python3 -m py_compile` and a smoke-run both pass, proves the module's
*public* surface is intact. It does not prove nothing else in the
repository references a symbol by its *exact old private name* -- a
sibling file's own test suite, a debugging script, or documentation example
can call `_old_internal_name(...)` directly, and none of the above checks
will catch that until it actually runs.

The check that caught a real instance of this: after extracting and
renaming a private helper, grep the entire repository -- not just the
files being edited -- for every old private name being removed, before
declaring the extraction done. In the source audit this caught one
validator's own adversarial test calling the old name directly; a passing
static-check suite alone had not surfaced it, because that particular test
path hadn't been re-run yet at the point the renamed module was declared
complete.

This is the same principle `safe-incremental-refactoring`'s own
"Transitive-Consumer Discovery Before a Split" section already states for
moving an item other files reach through an import/path chain; this
technique is the same discipline applied specifically to a private,
unexported name during a merge-multiple-implementations-into-one refactor,
where the "moved item" is a symbol being renamed away, not a file being
relocated.

## Producing the architecture map as an artifact, not a report

A prose summary of findings is not reusable by someone who wasn't in the
room. What made this discovery durable enough to enforce as a "read
before you touch" gate:

- The confirmed layers, stated with real file examples, not an assumed or
  aspirational taxonomy.
- Each duplication cluster's exact file/function pairs and their
  before/merge status, not a vague "there's some duplication here."
- The naming convention's actual exceptions named explicitly, so a future
  reader trusts the convention's *documented* reliability rather than
  re-discovering the two exceptions from scratch.
- A visible target module name for each cluster, so "where does the next
  similar helper belong" has an answer that doesn't require re-deriving
  the survey.

Keep the map current the same way any other single-source-of-truth
document is kept current -- update it in the same change that adds or
consolidates a primitive it describes, or explicitly say why it was not
updated. A stale map that is still trusted is worse than no map, because
it actively misleads instead of leaving an obvious gap.
