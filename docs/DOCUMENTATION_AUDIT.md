# Documentation duplication audit — v5.0.0

## Finding

Version 4 had useful content but too many competing entry points:

- 16 Markdown files at the repository root.
- Five profile/evidence files repeated the same domain and capability statements.
- Three standalone standards repeated workflows already present in skills and their references.
- README contained installation, profile, skill-routing, and package-map material that had separate owners.
- Full `history/v1`, `v2`, and `v3` directory snapshots duplicated content already preserved by Git commits and tags.

The duplication was mostly semantic rather than exact copy/paste. It increased maintenance risk because the same fact could be updated in one file and remain stale elsewhere.

## v5 decisions

1. Git tags replace full history snapshots.
2. `README.md` is navigation only.
3. `INSTALL.md` owns all installation guidance.
4. `AGENTS.md` owns always-on architecture behavior.
5. `CLAUDE.md` imports `AGENTS.md` instead of repeating it.
6. One profile document owns identity/capability statements.
7. Evidence is separated by source, not restated in the profile.
8. One concise governance overview links to detailed executable skills.
9. Migration notes are consolidated into `CHANGELOG.md` and the release index.
10. A document ownership map prevents new competing sources.

## Accepted duplication

Some limited repetition is deliberate:

- `AGENTS.md` contains a short role summary so agents receive essential context without loading the full profile.
- Skill descriptions repeat a short trigger statement because both Codex and Claude Code use descriptions for discovery.
- `INSTALL.md` includes both PowerShell and Bash commands because they are operationally distinct.
- Standards summarize non-negotiable rules while skills contain execution procedures.

## Control

Run:

```bash
python scripts/audit_docs.py
```

The audit reports exact long-paragraph duplication outside templates/history. Semantic duplication still requires review against `docs/README.md`.
