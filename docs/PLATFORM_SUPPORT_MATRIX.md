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
| Windows | Verified — `scripts/install.ps1`, INSTALL.md section 4 | Verified — `scripts/install.ps1`, INSTALL.md section 4 | Not yet attempted |
| macOS / Linux / WSL | Verified — `scripts/install.sh`, INSTALL.md section 5 | Verified — `scripts/install.sh`, INSTALL.md section 5 | Not yet attempted |

Install method: plugin marketplace (`codex plugin marketplace add` /
`claude plugin marketplace add`, INSTALL.md section 2) or standalone
`install.sh`/`install.ps1` (INSTALL.md sections 3-5). Both tools share the
same canonical `.agents/skills/` source; nothing platform-specific lives in
individual Skills.

**Gemini CLI**: its own documentation states `.agents/skills/` is a
supported interoperable alias path
(<https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md>),
referencing the same Agent Skills open standard CloudSkill's `SKILL.md`
frontmatter already follows. This is a documented claim, not something
CloudSkill has installed and confirmed against a real Gemini CLI session —
treat it as "likely compatible, unverified" until someone actually runs it
and this row is updated with real evidence.

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
| `portable` | No CloudSkill-repository dependency; safe as-is | agent-development-process, application-client-server-architecture, architecture-review, code-review, coding-agent-project-governance, cross-platform-engine-architecture, cross-platform-native-architecture, development-process-tailoring, document-governance, equipment-control-architecture, equipment-domain-modeling, framework-design, runtime-evaluation-engineering, safe-incremental-refactoring, semiconductor-equipment-domain-knowledge, software-quality-iso25010, using-cloudbox-skills |
| `hybrid` | Core judgment portable; some documented workflow steps invoke repository scripts and will not function in a sandbox | developing-skills |
| `cli-only` | Excluded from sandboxed packaging | local-runtime-eval-debugging |

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

- Gemini CLI compatibility is a documentation claim, not a local test.
- `hybrid`-tier Skills are packaged as-is; a user who uploads
  `developing-skills` to claude.ai will see its interaction-capture workflow
  steps in the Skill body even though those steps cannot execute there. This
  is disclosed, not hidden, but is not the same as a sandbox-native rewrite
  of those steps.
- No automated check confirms the claude.ai upload actually succeeds or that
  the uploaded Skill triggers correctly — that requires a live account with
  code execution enabled, which this repository's static validation cannot
  exercise.
