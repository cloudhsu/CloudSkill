from __future__ import annotations

from pathlib import Path
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(relative: str) -> dict:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {relative}: {exc}")
        return {}


def png_size(relative: str) -> tuple[int, int] | None:
    path = ROOT / relative
    try:
        data = path.read_bytes()
    except OSError as exc:
        fail(f"missing branding asset {relative}: {exc}")
        return None
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        fail(f"not a valid PNG header: {relative}")
        return None
    return struct.unpack(">II", data[16:24])


version_path = ROOT / "VERSION"
version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else ""
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    fail(f"invalid VERSION: {version!r}")

codex = load_json(".codex-plugin/plugin.json")
claude = load_json(".claude-plugin/plugin.json")
codex_market = load_json(".agents/plugins/marketplace.json")
claude_market = load_json(".claude-plugin/marketplace.json")
_private_plugin_path = ROOT / "private-plugin/.claude-plugin/plugin.json"
private_claude = load_json("private-plugin/.claude-plugin/plugin.json") if _private_plugin_path.exists() else {}

distribution = load_json("config/skill-distribution.json")
tiers = distribution.get("skills", {})
core_names = sorted(name for name, tier in tiers.items() if tier == "core")
evolution_names = sorted(name for name, tier in tiers.items() if tier == "evolution-pack")
expected_core_paths = sorted(f"./.agents/skills/{name}/" for name in core_names)
# The real Claude Code plugin loader forbids ".." in a plugin's skills field
# (confirmed 2026-08-15 by an actual failed `claude plugin install` --
# "Copied plugins cannot reference files outside their directory"). The
# private plugin instead uses the documented cross-plugin symlink pattern:
# private-plugin/skills/<name> -> ../../.agents/skills/<name>, referenced
# here with a forward-only path relative to the private plugin's own root.
expected_private_paths = sorted(f"./skills/{name}/" for name in evolution_names)


def as_list(value: object) -> list:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return value
    return []


for label, manifest in (("Codex", codex), ("Claude", claude)):
    if manifest.get("name") != "cloudbox-skills":
        fail(f"{label} plugin name must be cloudbox-skills")
    if manifest.get("version") != version:
        fail(f"{label} plugin version does not match VERSION")
    skills_field = as_list(manifest.get("skills"))
    for entry in skills_field:
        if ".." in Path(entry).parts:
            fail(f"{label} plugin path traversal is not allowed: {entry}")
    if sorted(skills_field) != expected_core_paths:
        fail(f"{label} plugin skills array does not match the core tier in config/skill-distribution.json")

# A filtered public checkout physically lacks the evolution-pack skill
# directories (scripts/export_public_bundle.py never copies them). Use that
# as the signal for which mode this checkout is in, so this one validator
# enforces both directions: the private repo must wire the private plugin up
# correctly, and a public checkout must show no trace of it at all.
evolution_dirs_present = [name for name in evolution_names if (ROOT / f".agents/skills/{name}").is_dir()]

if evolution_dirs_present:
    if private_claude.get("name") != "cloudbox-skills-private":
        fail("Private plugin name must be cloudbox-skills-private")
    if private_claude.get("version") != version:
        fail("Private plugin version does not match VERSION")
    priv_skills = sorted(as_list(private_claude.get("skills")))
    if priv_skills != expected_private_paths:
        fail("Private plugin skills array does not match the evolution-pack tier in config/skill-distribution.json")
    for name in evolution_names:
        link = ROOT / "private-plugin" / "skills" / name
        if not link.is_symlink():
            fail(f"private-plugin/skills/{name} must be a symlink (cross-plugin sharing requires the documented symlink pattern, not a path with '..')")
        elif not (ROOT / f".agents/skills/{name}/SKILL.md").is_file():
            fail(f"private-plugin/skills/{name} symlink target is missing SKILL.md")
else:
    if private_claude:
        fail("Public checkout must not contain private-plugin/.claude-plugin/plugin.json")
    if (ROOT / "private-plugin").exists():
        fail("Public checkout must not contain a private-plugin/ directory at all")
    if any("private" in p.get("name", "") for p in claude_market.get("plugins", [])):
        fail("Public checkout's Claude marketplace must not reference any private plugin")

if codex.get("interface", {}).get("displayName") != "CloudBox Skills":
    fail("Codex plugin displayName must be CloudBox Skills")
if codex.get("interface", {}).get("brandColor") != "#00A2EA":
    fail("Codex plugin brandColor must match CloudBox branding")
if claude.get("displayName") != "CloudBox Skills":
    fail("Claude plugin displayName must be CloudBox Skills")

for relative, expected in (("assets/cloudbox-icon.png", (128, 128)), ("assets/cloudbox-logo.png", (512, 512))):
    actual = png_size(relative)
    if actual and actual != expected:
        fail(f"unexpected PNG dimensions for {relative}: {actual}, expected {expected}")

for field, expected in (("composerIcon", "./assets/cloudbox-icon.png"), ("logo", "./assets/cloudbox-logo.png")):
    if codex.get("interface", {}).get(field) != expected:
        fail(f"Codex interface {field} mismatch")

skills_root = ROOT / ".agents/skills"
skill_dirs = sorted(path.name for path in skills_root.iterdir() if path.is_dir()) if skills_root.exists() else []
if not skill_dirs:
    fail("canonical skill source is empty")
for name in skill_dirs:
    if not (skills_root / name / "SKILL.md").is_file():
        fail(f"canonical skill missing SKILL.md: {name}")

codex_plugins = codex_market.get("plugins", [])
if len(codex_plugins) != 1 or codex_plugins[0].get("name") != "cloudbox-skills":
    fail("Codex marketplace must expose exactly one cloudbox-skills plugin")
else:
    source = codex_plugins[0].get("source", {})
    if source.get("source") != "local" or source.get("path") != "./":
        fail("Codex marketplace must point at the repository-root plugin")

claude_plugins = claude_market.get("plugins", [])
claude_plugin_names = {p.get("name"): p for p in claude_plugins}
if "cloudbox-skills" not in claude_plugin_names:
    fail("Claude marketplace must expose cloudbox-skills")
elif claude_plugin_names["cloudbox-skills"].get("source") != "./":
    fail("Claude marketplace cloudbox-skills must point at the repository-root plugin")

if evolution_dirs_present:
    if "cloudbox-skills-private" not in claude_plugin_names:
        fail("Claude marketplace must expose cloudbox-skills-private (private-repo-only add-on)")
    elif claude_plugin_names["cloudbox-skills-private"].get("source") != "./private-plugin":
        fail("Claude marketplace cloudbox-skills-private must point at ./private-plugin")
    if len(claude_plugins) != 2:
        fail(f"Claude marketplace must expose exactly cloudbox-skills and cloudbox-skills-private, found {len(claude_plugins)} entries")
elif len(claude_plugins) != 1:
    fail(f"Public checkout's Claude marketplace must expose exactly cloudbox-skills, found {len(claude_plugins)} entries")

using_yaml = (ROOT / ".agents/skills/using-cloudbox-skills/agents/openai.yaml").read_text(encoding="utf-8")
for marker in ("CloudBox 路由", "#00A2EA", "CloudBox skills"):
    if marker not in using_yaml:
        fail(f"using-cloudbox-skills OpenAI metadata missing: {marker}")

print(f"Validated CloudBox Codex and Claude plugin packaging for {len(skill_dirs)} canonical skills at version {version or 'UNKNOWN'}")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
