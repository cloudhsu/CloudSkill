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

for label, manifest in (("Codex", codex), ("Claude", claude)):
    if manifest.get("name") != "cloudbox-skills":
        fail(f"{label} plugin name must be cloudbox-skills")
    if manifest.get("version") != version:
        fail(f"{label} plugin version does not match VERSION")
    if manifest.get("skills") != "./.agents/skills/":
        fail(f"{label} plugin must point to canonical ./.agents/skills/")
    skills_path = manifest.get("skills", "")
    if ".." in Path(skills_path).parts:
        fail(f"{label} plugin path traversal is not allowed")

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
if len(claude_plugins) != 1 or claude_plugins[0].get("name") != "cloudbox-skills":
    fail("Claude marketplace must expose exactly one cloudbox-skills plugin")
elif claude_plugins[0].get("source") != "./":
    fail("Claude marketplace must point at the repository-root plugin")

using_yaml = (ROOT / ".agents/skills/using-cloudbox-skills/agents/openai.yaml").read_text(encoding="utf-8")
for marker in ("CloudBox 路由", "#00A2EA", "CloudBox skills"):
    if marker not in using_yaml:
        fail(f"using-cloudbox-skills OpenAI metadata missing: {marker}")

print(f"Validated CloudBox Codex and Claude plugin packaging for {len(skill_dirs)} canonical skills at version {version or 'UNKNOWN'}")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
