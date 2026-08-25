from __future__ import annotations

"""Optionally install any bundled hooks from already-installed Skills into a
consumer project's own Claude Code / Codex CLI / Gemini CLI configuration.

A Skill is content -- SKILL.md -- read into context. It has no mechanism of
its own to write host-level files. A hook is the opposite: host-level,
deterministic, project-local automation (a script plus a settings.json/
hooks.json wiring entry) that runs outside the model's control. This script
is the bridge between the two: a Skill MAY optionally bundle one or more
hooks under `hooks/<hook-name>/{script.sh,manifest.json}`; this script scans
for those, and for each one offers -- it never silently forces -- to copy
the script and safely merge its wiring into the target project.

"Safely merge" specifically means: read the existing config file if present,
add only this hook's entry to the relevant event/matcher, and leave every
other key, matcher, and hook entry in that file untouched. Never overwrite
the whole file. This mirrors install.sh's existing BEGIN/END-marker approach
for AGENTS.md/CLAUDE.md, adapted for JSON instead of markdown.

This is deliberately a separate, optional script, not merged into
install.sh's own flow -- a hook can actively block a future commit if
something is misconfigured, which is a materially different risk than
copying Skill content or writing a passive local Eval-capture config, so it
gets its own explicit opt-in step rather than inheriting install.sh's
create-by-default posture for the local config.

2026-08-24 IMPORTANT PRECONDITION, not previously documented anywhere in
this script -- a correctly-installed hook can still silently never fire,
for a reason this script cannot detect or warn about at install time:

- Claude Code loads a project's .claude/settings.json (hooks included)
  ONLY from the directory the session was actually launched in, and does
  NOT re-scan or inherit it from a parent directory, nor pick up a
  subdirectory's own settings.json after a later `cd` during the session
  (confirmed against Claude Code's own docs, code.claude.com/docs/en/
  large-codebases.md). A user whose habit is "start the agent in a parent
  folder that holds several sibling repos, then cd into the one being
  worked on" will have every hook installed by this script into any of
  those sibling repos silently never fire, session after session, with
  no error -- discovered in cloudbox-skills' own case only by noticing a
  hook's own unconditional-write side-effect file (a journal entry that
  should exist after a real `git push`) was simply never created.
- Codex CLI resolves .codex/hooks.json differently: it walks up from the
  actual OS working directory *at the moment the `codex` process itself
  is started* to find a .git directory and treats that as project root
  (developers.openai.com/codex/hooks) -- so a plain `cd repo && codex`
  does pick up that repo's hooks, unlike Claude Code's fixed-at-session-
  start behavior. The two providers are NOT interchangeable on this
  point; do not assume verifying one confirms the other.

Net effect: after running this script, the person installing hooks needs
to be told explicitly how they actually launch each provider day to day,
not just that the files were written -- "installed" and "will ever
execute" are two different claims for Claude Code project-scoped hooks
in particular.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

PROVIDERS = ("claude", "codex", "gemini")


def find_bundled_hooks(cloudskill_repo: Path) -> list[dict[str, Any]]:
    """Return every hooks/<name>/manifest.json found under any Skill."""
    found: list[dict[str, Any]] = []
    skills_dir = cloudskill_repo / ".agents" / "skills"
    if not skills_dir.is_dir():
        return found
    for skill_dir in sorted(skills_dir.iterdir()):
        hooks_dir = skill_dir / "hooks"
        if not hooks_dir.is_dir():
            continue
        for hook_dir in sorted(hooks_dir.iterdir()):
            manifest_path = hook_dir / "manifest.json"
            if not manifest_path.is_file():
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["_skill_dir"] = skill_dir
            manifest["_hook_dir"] = hook_dir
            found.append(manifest)
    return found


def skill_is_installed(
    skill_name: str, project_path: Path, *, user_home: Path | None = None
) -> bool:
    """A Skill counts as installed if its own folder exists anywhere this
    installer's copy_skills step would have placed it (project or user
    scope, either tool), or inside an installed Codex plugin cache.

    Codex plugins are user-scoped and keep regular-file Skill projections
    under ``~/.codex/plugins/cache/<marketplace>/<plugin>/<version>``. A
    project can therefore have a Skill available to Codex without having a
    project-local ``.agents`` or ``.claude`` copy; hook installation must
    recognize that supported installation shape too.
    """
    home = user_home or Path.home()
    candidates = [
        project_path / ".agents" / "skills" / skill_name,
        project_path / ".claude" / "skills" / skill_name,
        home / ".agents" / "skills" / skill_name,
        home / ".claude" / "skills" / skill_name,
    ]
    if any(c.is_dir() for c in candidates):
        return True

    codex_cache = home / ".codex" / "plugins" / "cache"
    if not codex_cache.is_dir():
        return False

    for plugin_root in codex_cache.glob("*/*/*"):
        codex_skill_roots = (
            plugin_root / ".agents" / "skills",
            plugin_root / "codex-skills",
        )
        if any((skill_root / skill_name).is_dir() for skill_root in codex_skill_roots):
            return True
    return False


def hook_command(
    provider: str,
    skill_name: str,
    hook_name: str,
    *,
    windows: bool = False,
    script_name: str | None = None,
) -> str:
    """Return the provider command for one installed hook.

    Hook manifests remain portable by carrying the canonical POSIX script and
    an optional Windows-native script.  The installer chooses the native
    entry point on Windows instead of relying on whichever ``bash`` happens
    to be first on PATH (which may be the WSL launcher rather than Git Bash).
    """
    selected_script = script_name or ("script.ps1" if windows else "script.sh")
    hook_path = f".{provider}/hooks/{skill_name}/{hook_name}/{selected_script}"
    if windows:
        return f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File {hook_path}"
    return f"bash {hook_path}"


def merge_hook_entry(
    config: dict[str, Any],
    event: str,
    matcher: str | None,
    command: str,
    legacy_commands: set[str] | None = None,
) -> bool:
    """Mutate `config` in place, adding one hook command under the given
    event/matcher. Returns True if it changed anything, False if an entry
    with this exact command already existed (idempotent re-run).

    ``legacy_commands`` contains older platform-specific commands for this
    same hook.  An exact legacy command is migrated in place so a Windows
    reinstall does not leave the old ``bash`` command alongside the native
    PowerShell command.

    matcher=None means a non-tool event (Stop / AfterAgent and similar):
    real Claude Code / Codex CLI / Gemini CLI schemas for these events omit
    the "matcher" key entirely rather than using an empty string, so this
    matches/creates an entry that has no "matcher" key at all, not one with
    matcher == ""."""
    hooks = config.setdefault("hooks", {})
    event_list = hooks.setdefault(event, [])
    for entry in event_list:
        entry_matcher = entry.get("matcher") if "matcher" in entry else None
        if entry_matcher == matcher:
            for existing in entry.get("hooks", []):
                if existing.get("command") == command:
                    return False
            if legacy_commands:
                for existing in entry.get("hooks", []):
                    if existing.get("command") in legacy_commands:
                        existing["command"] = command
                        return True
            entry.setdefault("hooks", []).append({"type": "command", "command": command, "timeout": 15})
            return True
    new_entry: dict[str, Any] = {}
    if matcher is not None:
        new_entry["matcher"] = matcher
    new_entry["hooks"] = [{"type": "command", "command": command, "timeout": 15}]
    event_list.append(new_entry)
    return True


def install_one_hook(
    manifest: dict[str, Any], project_path: Path, providers: list[str], dry_run: bool
) -> list[str]:
    skill_name = manifest["owner_skill"]
    hook_name = manifest["name"]
    hook_dir: Path = manifest["_hook_dir"]
    actions: list[str] = []

    for provider in providers:
        provider_cfg = manifest["providers"].get(provider)
        if provider_cfg is None:
            continue
        config_file = project_path / provider_cfg["config_file"]
        windows = sys.platform == "win32"
        script_name = manifest.get("windows_script") if windows else manifest["script"]
        if windows and not script_name:
            actions.append(
                f"{provider}: unsupported on Windows; manifest has no windows_script, so no Bash fallback was installed"
            )
            continue

        script_source = hook_dir / script_name
        command = hook_command(
            provider,
            skill_name,
            hook_name,
            windows=windows,
            script_name=script_name,
        )
        legacy_commands = {
            hook_command(provider, skill_name, hook_name, windows=False),
        }

        config: dict[str, Any] = {}
        if config_file.is_file():
            try:
                config = json.loads(config_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"Refusing to touch {config_file}: existing file is not valid JSON ({exc}). "
                    "Fix it manually first, or wire this hook in by hand -- see the manifest."
                )

        changed = merge_hook_entry(
            config,
            provider_cfg["event"],
            provider_cfg.get("matcher"),
            command,
            legacy_commands=legacy_commands,
        )
        script_target = project_path / f".{provider}" / "hooks" / skill_name / hook_name / script_name

        if dry_run:
            if changed or not script_target.is_file():
                actions.append(f"[dry-run] would install {provider}: {config_file} + {script_target}")
            else:
                actions.append(f"[dry-run] {provider}: already installed, no change")
            continue

        if changed or not script_target.is_file():
            script_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(script_source, script_target)
            script_target.chmod(0o755)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
            action = "installed" if changed else "repaired"
            actions.append(f"{action} {provider}: {config_file} (+{script_target})")
        else:
            actions.append(f"{provider}: already installed, no change")

    return actions


def prompt_yes_no(question: str, default_yes: bool) -> bool:
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        # Non-interactive: never silently install a hook that can block
        # future work. Require an explicit --yes on scripted/CI runs.
        return False
    suffix = "[Y/n]" if default_yes else "[y/N]"
    reply = input(f"{question} {suffix} ").strip().lower()
    if not reply:
        return default_yes
    return reply in ("y", "yes")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-path", type=Path, default=Path.cwd(), help="Consumer project to install hooks into.")
    parser.add_argument("--cloudskill-repo-path", type=Path, default=None, help="CloudSkill repo (defaults to this script's own repo).")
    parser.add_argument("--providers", nargs="+", choices=PROVIDERS, default=list(PROVIDERS))
    parser.add_argument("--yes", action="store_true", help="Install every offered hook without prompting (for scripted/CI use).")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be installed without writing anything.")
    args = parser.parse_args()

    repo = args.cloudskill_repo_path or Path(__file__).resolve().parents[1]
    project_path = args.project_path.resolve()

    bundled = find_bundled_hooks(repo)
    if not bundled:
        print("No Skill in this CloudSkill checkout bundles an optional hook yet.")
        return 0

    offered = [m for m in bundled if skill_is_installed(m["owner_skill"], project_path)]
    if not offered:
        print("No installed Skill in this project bundles an optional hook.")
        return 0

    for manifest in offered:
        skill_name = manifest["owner_skill"]
        hook_name = manifest["name"]
        print(f"\n[{skill_name}/{hook_name}]")
        print(f"  {manifest['description']}")
        if args.dry_run:
            for line in install_one_hook(manifest, project_path, args.providers, dry_run=True):
                print(f"  {line}")
            continue
        proceed = args.yes or prompt_yes_no("  Install this hook into this project?", default_yes=True)
        if not proceed:
            print("  Skipped.")
            continue
        for line in install_one_hook(manifest, project_path, args.providers, dry_run=False):
            print(f"  {line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
