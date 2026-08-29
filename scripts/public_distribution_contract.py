"""Shared helpers for the fail-closed public CloudSkill projection."""

from __future__ import annotations

from pathlib import Path
import json
import re


PUBLIC_SKILL_TABLE_BEGIN = "<!-- PUBLIC_SKILL_TABLE:BEGIN -->"
PUBLIC_SKILL_TABLE_END = "<!-- PUBLIC_SKILL_TABLE:END -->"
PUBLIC_EXPORT_PRIVATE_BEGIN = ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def distribution_skill_sets(root: Path) -> tuple[set[str], set[str]]:
    skills = load_json(root / "config" / "skill-distribution.json").get("skills", {})
    public = {name for name, tier in skills.items() if tier == "core"}
    private = set(skills) - public
    return public, private


def plugin_skill_ids(root: Path, relative: str) -> set[str]:
    payload = load_json(root / relative)
    result = set()
    for raw in payload.get("skills", []):
        path = str(raw).rstrip("/")
        result.add(Path(path).name)
    return result


def manifest_skill_ids(root: Path) -> set[str]:
    payload = load_json(root / "SKILL_MANIFEST.json")
    return {item["name"] for item in payload.get("skills", [])}


def read_skill_description(root: Path, skill_id: str) -> str:
    text = (root / ".agents" / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        raise ValueError(f"{skill_id}: invalid SKILL.md frontmatter")
    description = re.search(r"^description:\s*(.+?)\s*$", match.group(1), re.M)
    if not description:
        raise ValueError(f"{skill_id}: missing description")
    return description.group(1).strip()


def render_public_skill_table(root: Path) -> str:
    public, _ = distribution_skill_sets(root)
    codex = plugin_skill_ids(root, ".codex-plugin/plugin.json")
    if codex != public:
        missing = sorted(public - codex)
        extra = sorted(codex - public)
        raise ValueError(f"Codex plugin/public distribution drift: missing={missing}, extra={extra}")
    rows = ["| Skill | Primary use |", "|---|---|"]
    for skill_id in sorted(public):
        description = read_skill_description(root, skill_id).replace("|", "\\|")
        rows.append(f"| `{skill_id}` | {description} |")
    return "\n".join(rows)


def replace_marked_section(text: str, begin: str, end: str, replacement: str) -> str:
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError(f"expected exactly one {begin}/{end} marker pair")
    before, remainder = text.split(begin, 1)
    _, after = remainder.split(end, 1)
    return before + begin + "\n" + replacement.rstrip() + "\n" + end + after


def strip_private_blocks(text: str, *, label: str = "text") -> str:
    begin_count = text.count(PUBLIC_EXPORT_PRIVATE_BEGIN)
    end_count = text.count(PUBLIC_EXPORT_PRIVATE_END)
    if begin_count != end_count:
        raise ValueError(
            f"{label}: unbalanced public-export private markers "
            f"({begin_count} begin, {end_count} end)"
        )
    pattern = re.compile(
        re.escape(PUBLIC_EXPORT_PRIVATE_BEGIN)
        + r".*?"
        + re.escape(PUBLIC_EXPORT_PRIVATE_END)
        + r"\n?",
        re.S,
    )
    previous = None
    while previous != text:
        previous = text
        text = pattern.sub("", text)
    return text


def contains_skill_id(text: str, skill_id: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9-]){re.escape(skill_id)}(?![a-z0-9-])", text))


def owned_skill(relative: str, prefix: str) -> str | None:
    if not relative.startswith(prefix):
        return None
    remainder = relative[len(prefix):]
    return remainder.split("/", 1)[0] if "/" in remainder else None


def classify_public_export_path(
    relative: str,
    content: bytes,
    public_skills: set[str],
    private_skills: set[str],
    policy: dict,
) -> str:
    """Return an explicit export category; unknown paths remain unclassified."""
    public_exact = set(policy.get("public_exact_files", []))
    private_exact = set(policy.get("private_exact_files", []))
    private_prefixes = tuple(policy.get("private_prefixes", []))

    if relative in public_exact:
        return "public"

    canonical_owner = owned_skill(relative, ".agents/skills/")
    if canonical_owner:
        if canonical_owner in public_skills:
            return "public-core-skill"
        if canonical_owner in private_skills:
            return "private-skill"
        return "unclassified"

    gemini_owner = owned_skill(relative, "gemini-plugin/skills/")
    if gemini_owner:
        if gemini_owner in public_skills:
            return "public-gemini-skill"
        if gemini_owner in private_skills:
            return "private-gemini-skill"
        return "unclassified"

    if relative.startswith("evals/behavior/cases/") and relative.endswith(".json"):
        try:
            owner = json.loads(content).get("skill")
        except json.JSONDecodeError:
            return "unclassified"
        if owner in public_skills:
            return "public-behavior-cases"
        if owner in private_skills:
            return "private-behavior-cases"
        return "unclassified"

    if relative in private_exact or relative.startswith(private_prefixes):
        return "private"
    return "unclassified"


def text_file(path: Path) -> bool:
    return path.suffix.lower() in {
        "", ".csv", ".html", ".json", ".md", ".ps1", ".py", ".sh",
        ".txt", ".yaml", ".yml",
    }
