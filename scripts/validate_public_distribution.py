"""Validate the exported public artifact as a closed, least-disclosure package."""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import re
import stat
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_distribution_contract import (  # noqa: E402
    PUBLIC_SKILL_TABLE_BEGIN,
    PUBLIC_SKILL_TABLE_END,
    contains_skill_id,
    distribution_skill_sets,
    load_json,
    manifest_skill_ids,
    plugin_skill_ids,
    render_public_skill_table,
    text_file,
)


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MANIFESTS = (".codex-plugin/plugin.json", ".claude-plugin/plugin.json")
OPERATIONAL_DOCS = ("AGENTS.md", "README.md", "INSTALL.md", "docs/CLOUDBOX_PLUGIN.md")
PROHIBITED_PATH_PREFIXES = (
    "private-plugin/",
    "private-gemini-plugin/",
    "public-plugin/",
    "evals/runtime/",
)
PROHIBITED_PATHS = {".github/workflows/runtime-eval.yml"}
IMPLEMENTATION_SCAN_EXCLUSIONS = {
    "scripts/validate_public_distribution.py",
    "scripts/public_distribution_contract.py",
}
FILE_REFERENCE_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:scripts|docs|config|evals)/[A-Za-z0-9_./-]+"
    r"\.(?:json|md|ps1|py|sh|txt|yaml|yml))"
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#|mailto:)([^)]+)\)")


def source_modes(root: Path, ref: str) -> dict[str, int]:
    if ref == "WORKTREE":
        tracked = subprocess.run(
            ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
        ).stdout
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
        modes = {}
        for raw in (tracked + untracked).split(b"\0"):
            if not raw:
                continue
            relative = raw.decode("utf-8")
            path = root / relative
            if path.is_symlink():
                modes[relative] = 0o120000
            elif path.is_file():
                modes[relative] = 0o100755 if path.stat().st_mode & stat.S_IXUSR else 0o100644
        return modes
    result = subprocess.run(
        ["git", "ls-tree", "-r", "-z", ref],
        cwd=root,
        capture_output=True,
        check=True,
    )
    modes: dict[str, int] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        raw_mode = metadata.split(b" ", 1)[0]
        modes[raw_path.decode("utf-8")] = int(raw_mode, 8)
    return modes


def artifact_skill_dirs(root: Path) -> set[str]:
    skills_root = root / ".agents" / "skills"
    if not skills_root.is_dir():
        return set()
    return {path.name for path in skills_root.iterdir() if path.is_dir()}


def readme_table_skill_ids(root: Path) -> set[str]:
    text = (root / "README.md").read_text(encoding="utf-8")
    if text.count(PUBLIC_SKILL_TABLE_BEGIN) != 1 or text.count(PUBLIC_SKILL_TABLE_END) != 1:
        raise ValueError("README must contain exactly one generated public Skill table marker pair")
    section = text.split(PUBLIC_SKILL_TABLE_BEGIN, 1)[1].split(PUBLIC_SKILL_TABLE_END, 1)[0]
    return set(re.findall(r"^\| `([a-z0-9-]+)` \|", section, re.M))


def enforced_surface_paths(root: Path) -> list[Path]:
    result: list[Path] = []
    for relative in OPERATIONAL_DOCS:
        path = root / relative
        if path.is_file():
            result.append(path)
    for skills_root in (root / ".agents" / "skills", root / "gemini-plugin" / "skills"):
        if skills_root.is_dir():
            result.extend(path for path in skills_root.rglob("*") if path.is_file() and text_file(path))
    for folder in (root / ".github" / "workflows", root / "evals" / "behavior"):
        if folder.is_dir():
            result.extend(path for path in folder.rglob("*") if path.is_file() and text_file(path))
    result.extend(root / relative for relative in PLUGIN_MANIFESTS if (root / relative).is_file())
    return sorted(set(result))


def all_text_paths(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(root).parts
        and text_file(path)
        and path.relative_to(root).as_posix() not in IMPLEMENTATION_SCAN_EXCLUSIONS
    )


def validate(root: Path, source_root: Path, source_ref: str, *, check_modes: bool) -> list[str]:
    errors: list[str] = []
    required = {
        "README.md",
        "INSTALL.md",
        "AGENTS.md",
        "SKILL_MANIFEST.json",
        "config/skill-distribution.json",
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
    }
    for relative in sorted(required):
        if not (root / relative).is_file():
            errors.append(f"missing required public artifact: {relative}")
    if errors:
        return errors

    expected_public, source_private = distribution_skill_sets(source_root)
    artifact_public, artifact_noncore = distribution_skill_sets(root)
    if artifact_noncore:
        errors.append(f"public distribution metadata contains non-core Skills: {sorted(artifact_noncore)}")
    if artifact_public != expected_public:
        errors.append(
            "public distribution Skill set drift: "
            f"missing={sorted(expected_public - artifact_public)}, "
            f"extra={sorted(artifact_public - expected_public)}"
        )

    sets = {
        "Skill directories": artifact_skill_dirs(root),
        "SKILL_MANIFEST.json": manifest_skill_ids(root),
    }
    for relative in PLUGIN_MANIFESTS:
        sets[relative] = plugin_skill_ids(root, relative)
    try:
        sets["README generated table"] = readme_table_skill_ids(root)
        expected_table = render_public_skill_table(root)
        readme = (root / "README.md").read_text(encoding="utf-8")
        actual_table = readme.split(PUBLIC_SKILL_TABLE_BEGIN, 1)[1].split(PUBLIC_SKILL_TABLE_END, 1)[0].strip()
        if actual_table != expected_table:
            errors.append("README generated public Skill table content is stale")
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    for label, actual in sets.items():
        if actual != expected_public:
            errors.append(
                f"{label} does not equal public distribution: "
                f"missing={sorted(expected_public - actual)}, extra={sorted(actual - expected_public)}"
            )

    for relative in PROHIBITED_PATHS:
        if (root / relative).exists():
            errors.append(f"private/broken public artifact is present: {relative}")
    for prefix in PROHIBITED_PATH_PREFIXES:
        base = root / prefix.rstrip("/")
        if base.exists() and any(base.rglob("*")):
            errors.append(f"private-only public path is present: {prefix}")
    for path in enforced_surface_paths(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for skill_id in sorted(source_private):
            if contains_skill_id(text, skill_id):
                errors.append(f"{relative}: references absent/private Skill ID {skill_id}")

    prohibited_patterns = {
        "local absolute user path": re.compile(r"(?<![A-Za-z0-9])/(?:Users|home)/[A-Za-z0-9._-]+/"),
        "private source repository URL": re.compile(r"github\.com/cloudhsu/cloudbox-skills", re.I),
        "Eval candidate identity": re.compile(r"\b(?:candidate_id|INT-\d{8}-[A-Za-z0-9-]+)\b"),
        "private tier metadata": re.compile(r"\bprivate-(?:art|equipment|game|meta|operation)\b"),
    }
    for path in all_text_paths(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in prohibited_patterns.items():
            if pattern.search(text):
                errors.append(f"{relative}: contains prohibited {label}")

    for relative in OPERATIONAL_DOCS:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in FILE_REFERENCE_RE.finditer(text):
            target = match.group(1).rstrip(".,:;)")
            if not (root / target).exists():
                errors.append(f"{relative}: references missing file {target}")
        for match in MARKDOWN_LINK_RE.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if not target:
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"{relative}: contains broken relative link {match.group(1)}")

    for relative in PLUGIN_MANIFESTS:
        payload = load_json(root / relative)
        for raw in payload.get("skills", []):
            target = (root / str(raw)).resolve()
            if not target.is_dir():
                errors.append(f"{relative}: missing declared Skill path {raw}")

    if check_modes:
        try:
            modes = source_modes(source_root, source_ref)
        except (OSError, subprocess.CalledProcessError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"cannot inspect source Git modes: {exc}")
        else:
            for path in root.rglob("*"):
                if not path.is_file() or ".git" in path.relative_to(root).parts:
                    continue
                relative = path.relative_to(root).as_posix()
                source_mode = modes.get(relative)
                if source_mode not in {0o100644, 0o100755}:
                    continue
                expected_exec = source_mode == 0o100755
                actual_exec = bool(path.stat().st_mode & stat.S_IXUSR)
                if actual_exec != expected_exec:
                    errors.append(
                        f"{relative}: executable mode drift "
                        f"(source={'100755' if expected_exec else '100644'}, "
                        f"artifact={'executable' if actual_exec else 'non-executable'})"
                    )
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="Public artifact root")
    parser.add_argument("--source-root", type=Path, default=None, help="Full source checkout")
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--skip-mode-check", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    source_root = (args.source_root or root).resolve()
    errors = validate(root, source_root, args.source_ref, check_modes=not args.skip_mode_check)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Public distribution closure: FAIL ({len(errors)} unique findings)")
        return 1
    print(f"Public distribution closure: PASS ({len(artifact_skill_dirs(root))} Skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
