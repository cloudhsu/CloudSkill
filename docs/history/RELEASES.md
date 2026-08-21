# Release history

Git commits and annotated tags are authoritative. This index intentionally avoids full source snapshots.

## Versioning policy

Confirmed with the user 2026-08-18. `X.Y.Z`:

- **Major (`X`)**: a breaking change — renamed/removed public identity, or a
  behavior change that is not backward compatible. Example: `v7.0.0`,
  renaming the plugin identity `cloudbox` -> `cloudbox-skills`.
- **Minor (`Y`)**: a new `active`/publicly-usable skill or capability, or a
  backward-compatible behavior extension to an existing one.
- **Patch (`Z`)**: everything else — fixes, small adjustments, an existing
  skill's evidence/lifecycle updates, or importing a new skill that stays
  `experimental` (not yet a public capability commitment).

Before this policy was written down, every `7.6.x` release (`7.6.1` through
`7.6.28`) used patch for every increment regardless of size, including at
least one addition (`7.6.28`, a new `experimental` skill import) that this
policy would still classify as patch — so no retroactive relabeling was
needed. Apply this table going forward without asking each time; escalate
only when a change's major/minor/patch classification is genuinely
ambiguous.

| Tag | Summary |
|---|---|
| `v1.0.0` | Architecture review, framework design, and code review |
| `v2.0.0` | Documentation governance, ISO/IEC 25010, process tailoring, and AI-agent lifecycle |
| `v3.0.0` | Client/Server, cross-platform native, coding-agent governance, and architect profile |
| `v4.0.0` | Source-grounded Bento/CloudBox evidence, safe refactoring, and engine architecture |
| `v5.0.0` | Documentation deduplication and dual Codex/Claude Code installation |
| `v6.0.0` | Evidence-gated Skill evolution and cross-family review panel foundation |
| `v7.0.0` | Plugin identity renamed `cloudbox` -> `cloudbox-skills` (breaking) |
| `v7.6.31` | Latest tagged release at time of writing; see `CHANGELOG.md` for every intermediate `5.x`/`6.x`/`7.x` entry |

This table intentionally lists only major-version boundaries plus the latest
tag, not every intermediate release — `CHANGELOG.md` already has a
per-version entry for all of them (`v5.5.x` through `v7.6.27`), and
duplicating that list here would create a second place to keep in sync. Check
`git tag -l 'v*' | sort -V` for the exhaustive, always-current list.

Use:

```bash
git show v4.0.0:README.md
git diff v4.0.0..v5.0.0
git switch --detach v3.0.0
```

Return to the current branch with:

```bash
git switch main
```
