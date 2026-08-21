# CloudSkill platform and surface support matrix

This is the authoritative record of which platform/interface combinations
CloudSkill actually supports, and how each one is verified. `install.sh` /
`install.ps1` implement the CLI rows; `config/skill-portability.json` +
`scripts/package_surface_skills.py` implement the sandboxed-surface rows.
Do not infer support for a combination not listed here.

## CLI surfaces

Full local filesystem/subprocess access. Every Skill (including
`cli-only`-tier ones) works identically.

| Platform | Codex CLI | Claude Code CLI | Gemini CLI |
|---|---|---|---|
| Windows | Verified — `scripts/install.ps1`, INSTALL.md section 4 | Verified — `scripts/install.ps1`, INSTALL.md section 4 | Package checks pass; live CLI NOT RUN |
| macOS / Linux / WSL | Verified — `scripts/install.sh`, INSTALL.md section 5 | Verified — `scripts/install.sh`, INSTALL.md section 5 | Package and isolated-copy checks pass; live CLI NOT RUN |

Install method: plugin marketplace (`codex plugin marketplace add` /
`claude plugin marketplace add`, INSTALL.md section 2) or standalone
`install.sh`/`install.ps1` (INSTALL.md sections 3-5). Both tools share the
same canonical `.agents/skills/` source; nothing platform-specific lives in
individual Skills.

**Gemini CLI**: `gemini-plugin/` and `private-gemini-plugin/` contain official
`gemini-extension.json` manifests and generated regular-file Skill projections.
Repository checks verify distribution-tier membership, byte parity, absence of
symlinks, and isolated copying. Live `gemini extensions install` and
`/skills list` remain `NOT RUN` because this workstation has no Gemini CLI.

## Sandboxed surfaces (claude.ai web, Claude Desktop, Claude API Skills)

No filesystem/subprocess access to this repository. Skills upload
one-at-a-time as a zip (Customize/Settings -> Skills -> Upload); Anthropic
requires the skill folder itself to sit at the zip's root
(`<skill-name>/SKILL.md`), and states custom Skills do **not** sync between
claude.ai, the API, and Claude Code — each surface needs its own upload
(<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>).

Only `portable` and `hybrid`-tier Skills (per
`config/skill-portability.json`) are eligible; `cli-only` Skills assume
repository access a sandbox does not have and are excluded by default.

Package and verify:

```bash
python3 scripts/package_surface_skills.py
# writes .local/surface-packages/<skill-name>.zip for every portable/hybrid Skill
```

| Tier | Meaning | Skills |
|---|---|---|
| `portable` | No CloudSkill-repository dependency; safe as-is | about-me, agent-development-process, application-client-server-architecture, architecture-review, cluster-tool-simulator-development, codebase-architecture-discovery, code-review, coding-agent-project-governance, cloudbox-game-migration, cross-platform-engine-architecture, cross-platform-native-architecture, development-process-tailoring, document-governance, equipment-control-architecture, equipment-domain-modeling, framework-design, game-art-pipeline, game-asset-resolution-audit, game-audio-design, game-design-systems, game-marketing-and-monetization, game-narrative-design, game-quality-and-release-gates, gameplay-core-modernization, indie-game-product-evolution, legacy-game-product-archaeology, native-ios-game-rewrite, project-management-sync, runtime-evaluation-engineering, safe-incremental-refactoring, semiconductor-equipment-domain-knowledge, software-quality-iso25010, teach-while-building, tray-descum-simulator-development, using-cloudbox-skills, wafer-bonder-debonder-development, wph-equipment-simulator-development |
| `hybrid` | Core judgment portable; some documented workflow steps invoke repository scripts and will not function in a sandbox | developing-skills |
| `cli-only` | Excluded from sandboxed packaging | local-runtime-eval-debugging, developing-eval |

`scripts/validate_skill_portability.py` (part of `run_all_checks.py`) proves
this table stays accurate two ways: it re-scans every `portable`-tier
Skill's own files for CloudSkill-repository-relative references and fails
if any are found (so a Skill can't drift into depending on repository
tooling while still claiming to be sandbox-safe), and it actually runs the
packaging script against a temp directory and checks each produced zip's
internal structure matches Anthropic's documented requirement.

**Not yet done**: no zip produced by `package_surface_skills.py` has
actually been uploaded to claude.ai/Desktop and exercised. The structural
check proves the zip *shape* is correct; it does not prove the Skill
*behaves* correctly once claude.ai has loaded it in its sandboxed VM
(different network access, no local package installation — see the
"Runtime environment constraints" section of Anthropic's docs). Treat a
produced zip as ready to try, not as confirmed working.

## Known unknowns

- Gemini CLI package compatibility has static and isolated-copy evidence, but
  live CLI installation and Skill discovery are still untested.
- `hybrid`-tier Skills are packaged as-is; a user who uploads
  `developing-skills` to claude.ai will see release/CI steps (e.g. `gh`
  commands, `scripts/manage_skill.py`) in the Skill body even though those
  steps cannot execute there. This is disclosed, not hidden, but is not the
  same as a sandbox-native rewrite of those steps. The interaction-capture
  workflow itself moved to `developing-eval` (`cli-only`, excluded from
  sandboxed packaging entirely) as of 2026-08-15.
- No automated check confirms the claude.ai upload actually succeeds or that
  the uploaded Skill triggers correctly — that requires a live account with
  code execution enabled, which this repository's static validation cannot
  exercise.
