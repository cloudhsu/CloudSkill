from __future__ import annotations

from pathlib import Path
import hashlib
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
gemini = load_json("gemini-plugin/gemini-extension.json")
codex_market = load_json(".agents/plugins/marketplace.json")
claude_market = load_json(".claude-plugin/marketplace.json")
_private_plugin_path = ROOT / "private-plugin/.claude-plugin/plugin.json"
private_claude = load_json("private-plugin/.claude-plugin/plugin.json") if _private_plugin_path.exists() else {}
_private_codex_plugin_path = ROOT / "private-plugin/.codex-plugin/plugin.json"
private_codex = load_json("private-plugin/.codex-plugin/plugin.json") if _private_codex_plugin_path.exists() else {}
_private_gemini_path = ROOT / "private-gemini-plugin/gemini-extension.json"
private_gemini = load_json("private-gemini-plugin/gemini-extension.json") if _private_gemini_path.exists() else {}

distribution = load_json("config/skill-distribution.json")
tiers = distribution.get("skills", {})
core_names = sorted(name for name, tier in tiers.items() if tier == "core")
evolution_names = sorted(name for name, tier in tiers.items() if tier != "core")  # any non-core tier is private (private-meta/private-game/private-operation/private-art/...)
expected_core_paths = sorted(f"./.agents/skills/{name}/" for name in core_names)
# The real Claude Code plugin loader forbids ".." in a plugin's skills field
# (confirmed 2026-08-15 by an actual failed `claude plugin install` --
# "Copied plugins cannot reference files outside their directory"). The
# private plugin instead uses the documented cross-plugin symlink pattern:
# private-plugin/skills/<name> -> ../../.agents/skills/<name>, referenced
# here with a forward-only path relative to the private plugin's own root.
expected_private_paths = sorted(f"./skills/{name}/" for name in evolution_names)
expected_private_codex_paths = sorted(f"./codex-skills/{name}/" for name in evolution_names)


def as_list(value: object) -> list:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return value
    return []


def relative_files(root: Path) -> list[Path]:
    return sorted(
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    )


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(relative): hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in relative_files(root)
    }


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

if gemini.get("name") != "cloudbox-skills" or gemini.get("version") != version:
    fail("Gemini extension name/version must match CloudBox and VERSION")
if set(gemini) - {"name", "version", "description"}:
    fail("Gemini extension manifest contains unsupported fields")
gemini_skills = ROOT / "gemini-plugin" / "skills"
gemini_names = sorted(path.name for path in gemini_skills.iterdir() if path.is_dir()) if gemini_skills.is_dir() else []
if gemini_names != core_names:
    fail("Gemini extension skills do not match the core tier")
for name in core_names:
    if tree_hashes(ROOT / ".agents" / "skills" / name) != tree_hashes(gemini_skills / name):
        fail(f"gemini-plugin/skills/{name} is stale")

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
        fail("Private plugin skills array does not match the private (non-core) tiers in config/skill-distribution.json")
    for name in evolution_names:
        link = ROOT / "private-plugin" / "skills" / name
        if not link.is_symlink():
            fail(f"private-plugin/skills/{name} must be a symlink (cross-plugin sharing requires the documented symlink pattern, not a path with '..')")
        elif not (ROOT / f".agents/skills/{name}/SKILL.md").is_file():
            fail(f"private-plugin/skills/{name} symlink target is missing SKILL.md")

    if private_codex.get("name") != "cloudbox-skills-private":
        fail("Private Codex plugin name must be cloudbox-skills-private")
    if private_codex.get("version") != version:
        fail("Private Codex plugin version does not match VERSION")
    if sorted(as_list(private_codex.get("skills"))) != expected_private_codex_paths:
        fail("Private Codex plugin skills array does not match the private (non-core) tiers in config/skill-distribution.json")
    for name in evolution_names:
        canonical = ROOT / ".agents" / "skills" / name
        packaged = ROOT / "private-plugin" / "codex-skills" / name
        if not packaged.is_dir():
            fail(f"private-plugin/codex-skills/{name} is missing; run scripts/sync_private_codex_plugin.py")
        elif tree_hashes(canonical) != tree_hashes(packaged):
            fail(f"private-plugin/codex-skills/{name} is stale; run scripts/sync_private_codex_plugin.py")
    if private_gemini.get("name") != "cloudbox-skills-private" or private_gemini.get("version") != version:
        fail("Private Gemini extension name/version must match CloudBox private and VERSION")
    private_gemini_skills = ROOT / "private-gemini-plugin" / "skills"
    private_gemini_names = sorted(path.name for path in private_gemini_skills.iterdir() if path.is_dir()) if private_gemini_skills.is_dir() else []
    if private_gemini_names != evolution_names:
        fail("Private Gemini extension skills do not match the private tiers")
    for name in evolution_names:
        if tree_hashes(ROOT / ".agents" / "skills" / name) != tree_hashes(private_gemini_skills / name):
            fail(f"private-gemini-plugin/skills/{name} is stale")
else:
    if private_claude:
        fail("Public checkout must not contain private-plugin/.claude-plugin/plugin.json")
    if private_codex:
        fail("Public checkout must not contain private-plugin/.codex-plugin/plugin.json")
    if (ROOT / "private-plugin").exists():
        fail("Public checkout must not contain a private-plugin/ directory at all")
    if private_gemini or (ROOT / "private-gemini-plugin").exists():
        fail("Public checkout must not contain a private-gemini-plugin/ directory")
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
codex_plugin_names = {p.get("name"): p for p in codex_plugins}
if evolution_dirs_present:
    if set(codex_plugin_names) != {"cloudbox-skills", "cloudbox-skills-private"}:
        fail("Private Codex marketplace must expose exactly cloudbox-skills and cloudbox-skills-private")
else:
    if set(codex_plugin_names) != {"cloudbox-skills"}:
        fail("Public Codex marketplace must expose exactly one cloudbox-skills plugin")
if "cloudbox-skills" not in codex_plugin_names:
    fail("Codex marketplace must expose cloudbox-skills")
else:
    source = codex_plugin_names["cloudbox-skills"].get("source", {})
    if source.get("source") != "local" or source.get("path") != "./":
        fail("Codex marketplace must point at the repository-root plugin")
if evolution_dirs_present and "cloudbox-skills-private" in codex_plugin_names:
    private_source = codex_plugin_names["cloudbox-skills-private"].get("source", {})
    if private_source.get("source") != "local" or private_source.get("path") != "./private-plugin":
        fail("Codex marketplace cloudbox-skills-private must point at ./private-plugin")

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

print(f"Validated CloudBox Codex, Claude, and Gemini plugin packaging for {len(skill_dirs)} canonical skills at version {version or 'UNKNOWN'}")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
