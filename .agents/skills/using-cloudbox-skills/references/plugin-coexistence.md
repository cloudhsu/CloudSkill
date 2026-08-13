# Plugin Coexistence

## Decision boundary

Plugin installation and enablement are host configuration. Skill routing is task behavior. Do not confuse a prompt-level instruction to ignore another workflow with proof that the plugin was disabled in Codex, ChatGPT, or Claude Code.

## CloudBox-only mode

Use when the user wants CloudBox to be the sole optional workflow system for the task.

- Select CloudBox skills through `using-cloudbox-skills`.
- Do not invoke another plugin's router, planning lifecycle, or review lifecycle.
- Preserve higher-level system, security, repository, and user instructions.
- Report host-level plugin state as unknown unless it was actually inspected or changed.

## Hybrid mode

Define ownership before composing skills:

- Generic development workflow may own brainstorming, plans, TDD, debugging discipline, and branch completion.
- CloudBox owns domain knowledge, architecture boundaries, state authority, equipment semantics, modeling, safe migration, quality evidence, and controlled documentation.

Use one router first, then explicitly invoke the other system only for its non-overlapping responsibility. Avoid two competing mandatory workflows around the same step.

## Distribution collision

CloudBox may be installed as a plugin or as standalone skills. Do not load both copies in the same host. A duplicate `using-cloudbox-skills` or other skill ID can cause ambiguous routing, duplicate context, and unclear Eval attribution.

## Evidence

Record separately:

- Which plugins were installed or enabled, when observable.
- Which skills were explicitly invoked.
- Which skills were inferred from output only.
- Which plugin or skill behavior was not observed.

Never infer a successful enable, disable, reload, or update solely from the user's request.
