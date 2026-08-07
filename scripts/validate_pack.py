from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"

errors = []
warnings = []
manifest = []
names = set()

for folder in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
    skill_file = folder / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"{folder}: missing SKILL.md")
        continue

    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(f"{skill_file}: invalid YAML frontmatter block")
        continue

    front = match.group(1)
    name_match = re.search(r"^name:\s*(.+?)\s*$", front, re.M)
    desc_match = re.search(r"^description:\s*(.+?)\s*$", front, re.M)

    if not name_match or not desc_match:
        errors.append(f"{skill_file}: name and description are required")
        continue

    name = name_match.group(1).strip()
    description = desc_match.group(1).strip()

    if name != folder.name:
        errors.append(f"{skill_file}: name '{name}' must equal folder '{folder.name}'")
    if name in names:
        errors.append(f"duplicate skill name: {name}")
    names.add(name)

    if len(description) > 360:
        warnings.append(f"{name}: description is long ({len(description)} chars)")
    if len(description) < 40:
        warnings.append(f"{name}: description may be too vague ({len(description)} chars)")

    ui = folder / "agents" / "openai.yaml"
    if not ui.exists():
        warnings.append(f"{name}: missing optional agents/openai.yaml")

    manifest.append({
        "name": name,
        "description": description,
        "path": str(skill_file.relative_to(ROOT)),
        "file_count": sum(1 for p in folder.rglob("*") if p.is_file()),
    })

agents = ROOT / "AGENTS.md"
if not agents.exists():
    errors.append("missing global AGENTS.md")
else:
    size = agents.stat().st_size
    if size > 32768:
        warnings.append(f"AGENTS.md is {size} bytes; Codex project guidance defaults may truncate combined files")

required = [
    "ARCHITECT_PROFILE.md",
    "PRACTICAL_ARCHITECTURE_EVIDENCE.md",
    "PLANS.md",
    "DOCUMENT_STANDARD.md",
    "AGENT_DEVELOPMENT_STANDARD.md",
    "CODING_AGENT_PROJECT_STANDARD.md",
    "evals/skill-routing-cases.csv",
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"missing required pack file: {rel}")

manifest_path = ROOT / "SKILL_MANIFEST.json"
manifest_path.write_text(json.dumps({
    "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
    "skills": manifest,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Validated {len(manifest)} skills")
for warning in warnings:
    print(f"WARNING: {warning}")
for error in errors:
    print(f"ERROR: {error}")

sys.exit(1 if errors else 0)
