# CloudBox Plugin Distribution

CloudBox is the user-facing plugin brand. The GitHub repository remains `CloudSkill`, and existing skill IDs such as `using-cloudbox-skills` remain stable for compatibility.

## One canonical skill source

Both plugin manifests point to:

```text
./.agents/skills/
```

The repository does not maintain a second mutable `skills/` copy. The existing standalone installers also copy from this canonical directory.

## Codex and ChatGPT installation

From a local clone:

```powershell
codex plugin marketplace add D:\Git\CloudSkill
```

Restart or refresh the ChatGPT/Codex plugin directory, select the **CloudBox** marketplace, and install **CloudBox**. For a GitHub-hosted marketplace, add `cloudhsu/CloudSkill` instead of the local path.

The OpenAI plugin manifest uses the supplied CloudBox logo through `composerIcon` and `logo`, with `#00A2EA` as the brand color.

To configure the private Eval Inbox without installing a duplicate standalone skill copy:

```powershell
& "D:\Git\CloudSkill\scripts\install.ps1" `
  -Scope user `
  -CloudSkillRepoPath "D:\Git\CloudSkill" `
  -ConfigOnly
```

## Claude Code installation

From a local clone:

```powershell
claude plugin marketplace add D:\Git\CloudSkill
claude plugin install cloudbox-skills@cloudbox-marketplace --scope user
claude plugin list
```

Then run:

```text
/reload-plugins
```

Use the same `-ConfigOnly` setup when the Claude Code plugin should write sanitized positive or negative cases to the local Eval Inbox.

Claude Code namespaces plugin skills. For example:

```text
/cloudbox-skills:using-cloudbox-skills
/cloudbox-skills:architecture-review
/cloudbox-skills:equipment-control-architecture
```

Claude Code uses the standard `displayName`, description, version, author, and component-path fields. The CloudBox logo asset is included for cross-host branding, but the current Claude Code plugin manifest schema does not define a standard custom-logo field, so Claude UI logo rendering is not claimed.

## Standalone versus plugin installation

Use one CloudBox distribution mode at a time:

- **Plugin mode**: recommended for enable/disable controls, namespacing, marketplace updates, and coexistence with other plugins.
- **Standalone mode**: keeps the existing `.agents/skills` and `.claude/skills` installation for environments that do not support plugins.

Do not enable both the CloudBox plugin and a standalone copy of the same CloudBox skills in one host. Duplicate skill IDs make routing and attribution ambiguous.

## Coexistence with Superpowers or other workflow plugins

CloudBox can coexist with another plugin, but two routing or orchestration systems should not both govern the same decision without an explicit division of responsibility.

### CloudBox-only task

Disable the other plugin in the host UI or plugin manager, or state that the current task must use CloudBox only. The agent must not claim another plugin was disabled unless it actually changed the host setting and verified the result.

### Hybrid task

A reasonable division is:

- External workflow plugin: generic brainstorming, implementation planning, TDD, debugging, and branch-completion workflow.
- CloudBox: domain interpretation, architecture, state authority, equipment semantics, modeling, migration, quality evidence, and documentation governance.

Use only one top-level router. Select the smallest sufficient set of downstream skills and avoid duplicating planning, review, or verification steps.

## Update behavior

Both manifests carry the CloudBox release version. Bump `VERSION`, both plugin manifests, the changelog, and marketplace validation together. Re-run:

```bash
python scripts/run_all_checks.py
```

Runtime validation with the actual Codex and Claude Code plugin managers remains a separate release check.
