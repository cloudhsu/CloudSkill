# Local Eval review bundle contract

A review ZIP should contain:

- `REVIEW_SUMMARY.md`
- `STATUS.json`
- `environment.json`
- `run.log`
- routing JSONL, summary JSON, and Markdown report
- raw Behavior JSONL, summary JSON, and Markdown report
- refined Behavior equivalents when refinement was used
- context-preflight evidence
- selected source snapshots and SHA-256 inventory
- Git commit, branch, tracked-file status, and diff statistics without credentials or full unrelated diffs

It must exclude:

- `.git/`
- unrelated `.local/` runs
- credentials, tokens, cookies, account configuration, and private keys
- raw or complete conversation transcripts
- `.DS_Store`, caches, bytecode, and temporary files
- unrelated repository source code

The bundle is private diagnostic evidence and must remain ignored by Git.
