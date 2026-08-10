from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
MANIFEST = ROOT / "SKILL_MANIFEST.json"
ROUTING_CASES = ROOT / "evals" / "skill-routing-cases.csv"
BEHAVIOR_CASES = ROOT / "evals" / "behavior" / "cases"
POLICY = ROOT / "config" / "skill-lifecycle-policy.json"
VERSION = ROOT / "VERSION"

NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
VERSION_RE = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)")


def lifecycle_semantic_errors(payload: dict[str, Any], current_version: str) -> list[str]:
    errors: list[str] = []
    introduced = payload.get("introduced_version")
    reviewed = payload.get("last_reviewed_version")
    current_match = VERSION_RE.fullmatch(current_version)
    if current_match and introduced == "unreleased":
        errors.append("introduced_version cannot remain unreleased in a shipped repository version")
    reviewed_match = VERSION_RE.fullmatch(reviewed) if isinstance(reviewed, str) else None
    triggers = payload.get("next_review_triggers") or []
    if current_match and reviewed_match and "the skill has not been reviewed for two feature releases" in triggers:
        current_major, current_minor = int(current_match.group(1)), int(current_match.group(2))
        reviewed_major, reviewed_minor = int(reviewed_match.group(1)), int(reviewed_match.group(2))
        # A major boundary does not reveal how many intervening feature
        # releases occurred. Only enforce the distance that this pair of
        # semantic versions can prove without inventing release history.
        if current_major == reviewed_major and current_minor - reviewed_minor >= 2:
            errors.append("last_reviewed_version is at least two feature releases behind")
    return errors


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_policy() -> dict[str, Any]:
    payload = load_json(POLICY)
    if payload.get("schema_version") != 1:
        raise SystemExit(f"unsupported lifecycle policy schema: {payload.get('schema_version')!r}")
    return payload


def skill_names() -> list[str]:
    names = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
    if MANIFEST.is_file():
        payload = load_json(MANIFEST)
        names.update(item["name"] for item in payload.get("skills", []))
    return sorted(names)


def routing_evidence() -> dict[str, dict[str, list[str]]]:
    result: dict[str, dict[str, list[str]]] = {}
    if not ROUTING_CASES.is_file():
        return result
    with ROUTING_CASES.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            skill = (row.get("expected_skill") or "").strip()
            cid = (row.get("id") or "").strip()
            if not skill or not cid:
                continue
            bucket = result.setdefault(skill, {"positive": [], "negative": []})
            target = "positive" if (row.get("should_trigger") or "").strip().lower() == "true" else "negative"
            bucket[target].append(cid)
    for value in result.values():
        value["positive"].sort()
        value["negative"].sort()
    return result


def behavior_evidence() -> dict[str, dict[str, list[str]]]:
    result: dict[str, dict[str, list[str]]] = {}
    for path in sorted(BEHAVIOR_CASES.glob("*.json")):
        payload = load_json(path)
        file_skill = payload.get("skill")
        if not isinstance(file_skill, str):
            continue
        bucket = result.setdefault(file_skill, {"ids": [], "types": []})
        for item in payload.get("cases", []):
            if not isinstance(item, dict):
                continue
            cid = item.get("id")
            typ = item.get("type")
            if isinstance(cid, str):
                bucket["ids"].append(cid)
            if isinstance(typ, str):
                bucket["types"].append(typ)
    for value in result.values():
        value["ids"] = sorted(set(value["ids"]))
        value["types"] = sorted(set(value["types"]))
    return result


def lifecycle_payload(
    skill: str,
    *,
    policy: dict[str, Any],
    routing: dict[str, dict[str, list[str]]],
    behavior: dict[str, dict[str, list[str]]],
    existing: dict[str, Any] | None,
    default_stage: str,
) -> dict[str, Any]:
    current_version = VERSION.read_text(encoding="utf-8").strip() if VERSION.is_file() else "unknown"
    existing = existing or {}
    return {
        "schema_version": 1,
        "skill": skill,
        "stage": existing.get("stage", default_stage),
        "introduced_version": existing.get("introduced_version", "unknown"),
        "last_reviewed_version": existing.get("last_reviewed_version", current_version),
        "routing_case_ids": sorted(
            (routing.get(skill) or {}).get("positive", [])
            + (routing.get(skill) or {}).get("negative", [])
        ),
        "positive_routing_case_ids": (routing.get(skill) or {}).get("positive", []),
        "negative_routing_case_ids": (routing.get(skill) or {}).get("negative", []),
        "behavior_case_ids": (behavior.get(skill) or {}).get("ids", []),
        "behavior_case_types": (behavior.get(skill) or {}).get("types", []),
        "next_review_triggers": existing.get(
            "next_review_triggers", policy.get("review_triggers", [])
        ),
        "replacement_skill": existing.get("replacement_skill"),
        "notes": existing.get(
            "notes",
            "Baseline lifecycle evidence generated from committed routing and behavior cases.",
        ),
    }


def refresh_all(default_stage: str = "active") -> list[Path]:
    policy = load_policy()
    routing = routing_evidence()
    behavior = behavior_evidence()
    written: list[Path] = []
    valid_stages = set(policy.get("stages", []))
    if default_stage not in valid_stages:
        raise SystemExit(f"invalid default stage: {default_stage}")
    for skill in skill_names():
        path = SKILLS / skill / "lifecycle.json"
        existing = load_json(path) if path.is_file() else None
        payload = lifecycle_payload(
            skill,
            policy=policy,
            routing=routing,
            behavior=behavior,
            existing=existing,
            default_stage=default_stage,
        )
        write_json(path, payload)
        written.append(path)
    return written


def audit(check: bool = False) -> list[str]:
    policy = load_policy()
    routing = routing_evidence()
    behavior = behavior_evidence()
    valid_stages = set(policy.get("stages", []))
    required_types = set(policy.get("required_behavior_types", []))
    errors: list[str] = []
    rows: list[tuple[str, str, int, int, str]] = []
    current_version: str | None = None
    if VERSION.is_file():
        current_version = VERSION.read_text(encoding="utf-8").strip()
    else:
        errors.append(f"missing VERSION file: {VERSION}")

    for skill in skill_names():
        path = SKILLS / skill / "lifecycle.json"
        if not path.is_file():
            errors.append(f"{skill}: missing lifecycle.json; run python scripts/manage_skill.py refresh --all")
            continue
        try:
            payload = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{skill}: invalid lifecycle.json: {exc}")
            continue
        if payload.get("schema_version") != 1:
            errors.append(f"{skill}: lifecycle schema_version must be 1")
        if payload.get("skill") != skill:
            errors.append(f"{skill}: lifecycle skill name mismatch")
        if current_version is not None:
            errors.extend(f"{skill}: {error}" for error in lifecycle_semantic_errors(payload, current_version))
        stage = payload.get("stage")
        if stage not in valid_stages:
            errors.append(f"{skill}: invalid lifecycle stage {stage!r}")

        expected = lifecycle_payload(
            skill,
            policy=policy,
            routing=routing,
            behavior=behavior,
            existing=payload,
            default_stage="active",
        )
        for field in (
            "routing_case_ids",
            "positive_routing_case_ids",
            "negative_routing_case_ids",
            "behavior_case_ids",
            "behavior_case_types",
        ):
            if payload.get(field) != expected.get(field):
                errors.append(
                    f"{skill}: stale {field}; run python scripts/manage_skill.py refresh --all"
                )

        actual_types = set(payload.get("behavior_case_types") or [])
        missing_types = required_types - actual_types
        if missing_types:
            errors.append(f"{skill}: missing behavior case types {sorted(missing_types)}")
        if not payload.get("positive_routing_case_ids"):
            errors.append(f"{skill}: no positive routing case")

        if stage == "stable":
            if not payload.get("negative_routing_case_ids"):
                errors.append(f"{skill}: stable skill requires a negative routing case")
            if missing_types:
                errors.append(f"{skill}: stable skill lacks required behavior coverage")
        if stage == "deprecated" and not payload.get("replacement_skill"):
            errors.append(f"{skill}: deprecated skill requires replacement_skill")

        rows.append(
            (
                skill,
                str(stage),
                len(payload.get("positive_routing_case_ids") or []),
                len(payload.get("negative_routing_case_ids") or []),
                ",".join(payload.get("behavior_case_types") or []),
            )
        )

    print("Skill lifecycle audit")
    for skill, stage, positive, negative, types in rows:
        print(
            f"- {skill}: stage={stage} routing=+{positive}/-{negative} behavior={types or 'none'}"
        )
    for error in errors:
        print(f"ERROR: {error}")
    if check and errors:
        raise SystemExit(1)
    return errors


def scaffold(args: argparse.Namespace) -> None:
    name = args.name.strip()
    if not NAME_RE.fullmatch(name):
        raise SystemExit("name must use lowercase kebab-case")
    if not args.description.startswith("Use when"):
        raise SystemExit("description must begin with 'Use when'")
    folder = SKILLS / name
    if folder.exists():
        raise SystemExit(f"skill already exists: {folder}")

    folder.mkdir(parents=True)
    (folder / "agents").mkdir()
    (folder / "references").mkdir()
    (folder / "assets").mkdir()

    skill_text = f"""---
name: {name}
description: {args.description}
---

# {args.display_name}

## Core principle

TODO: state the decision principle this skill owns.

## Trigger conditions

- TODO

## Non-trigger conditions

- TODO

## Required workflow

1. TODO

## Required output

1. TODO

## Common mistakes

- TODO
"""
    (folder / "SKILL.md").write_text(skill_text, encoding="utf-8")
    openai = (
        'interface:\n'
        f'  display_name: "{args.display_name}"\n'
        f'  short_description: "{args.short_description}"\n'
        f'  default_prompt: "Use ${name} to complete this task."\n'
    )
    (folder / "agents" / "openai.yaml").write_text(openai, encoding="utf-8")

    policy = load_policy()
    current_version = VERSION.read_text(encoding="utf-8").strip() if VERSION.is_file() else "unreleased"
    lifecycle = {
        "schema_version": 1,
        "skill": name,
        "stage": "draft",
        "introduced_version": "unreleased",
        "last_reviewed_version": current_version,
        "routing_case_ids": [],
        "positive_routing_case_ids": [],
        "negative_routing_case_ids": [],
        "behavior_case_ids": [],
        "behavior_case_types": [],
        "next_review_triggers": policy.get("review_triggers", []),
        "replacement_skill": None,
        "notes": "Draft scaffold. Add RED evidence and replace all TODO markers before release.",
    }
    write_json(folder / "lifecycle.json", lifecycle)

    behavior_path = BEHAVIOR_CASES / f"{name}.json"
    behavior_payload = {
        "skill": name,
        "cases": [
            {
                "id": f"{args.case_prefix}-BEH-001",
                "skill": name,
                "type": "recognition",
                "prompt": "TODO: recognition case",
                "expected_routing": True,
                "expected_alternative_skill": None,
                "required_behaviors": ["TODO"],
                "forbidden_behaviors": ["TODO"],
                "required_artifacts": [],
                "baseline_expected_failure": ["TODO"],
                "review_notes": "Draft scaffold; replace all TODO values.",
            },
            {
                "id": f"{args.case_prefix}-BEH-002",
                "skill": name,
                "type": "application",
                "prompt": "TODO: application case",
                "expected_routing": True,
                "expected_alternative_skill": None,
                "required_behaviors": ["TODO"],
                "forbidden_behaviors": ["TODO"],
                "required_artifacts": [],
                "baseline_expected_failure": ["TODO"],
                "review_notes": "Draft scaffold; replace all TODO values.",
            },
            {
                "id": f"{args.case_prefix}-BEH-003",
                "skill": name,
                "type": "counterexample",
                "prompt": "TODO: counterexample",
                "expected_routing": False,
                "expected_alternative_skill": None,
                "required_behaviors": ["TODO"],
                "forbidden_behaviors": ["TODO"],
                "required_artifacts": [],
                "baseline_expected_failure": ["TODO"],
                "review_notes": "Draft scaffold; replace all TODO values.",
            },
        ],
    }
    write_json(behavior_path, behavior_payload)

    print(f"Created draft skill: {folder.relative_to(ROOT)}")
    print(f"Created behavior scaffold: {behavior_path.relative_to(ROOT)}")
    print("Next: replace TODOs, add positive/negative routing rows, establish RED evidence, then run:")
    print("  python scripts/manage_skill.py refresh --all")
    print("  python scripts/manage_skill.py audit --check")
    print("  python scripts/run_all_checks.py")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create, refresh, and audit standardized CloudSkill lifecycles.")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="Create a draft standardized skill scaffold.")
    new.add_argument("--name", required=True)
    new.add_argument("--description", required=True)
    new.add_argument("--display-name", required=True)
    new.add_argument("--short-description", required=True)
    new.add_argument("--case-prefix", required=True)

    refresh = sub.add_parser("refresh", help="Refresh lifecycle evidence from committed routing and behavior cases.")
    refresh.add_argument("--all", action="store_true", required=True)
    refresh.add_argument("--default-stage", default="active")

    audit_parser = sub.add_parser("audit", help="Audit lifecycle records.")
    audit_parser.add_argument("--check", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "new":
        scaffold(args)
        return 0
    if args.command == "refresh":
        written = refresh_all(args.default_stage)
        print(f"Refreshed {len(written)} lifecycle records.")
        return 0
    if args.command == "audit":
        errors = audit(check=args.check)
        return 1 if errors else 0
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
