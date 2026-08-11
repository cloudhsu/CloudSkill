"""Merge exported interaction Eval candidate zips into the local Eval Inbox.

Counterpart to `.agents/skills/developing-skills/assets/export_eval_candidate.py`,
which a disconnected/external session uses to package candidates as a zip
when it cannot reach this repository's Eval Inbox directly. The user copies
that zip into `<eval_inbox>/imports/` (default: `.local/eval-inbox/imports/`
in this repository) on the machine that hosts CloudSkill; this script
extracts each zip, re-validates every candidate with the same rules as
`capture_eval_candidate.py`, re-scans it against this machine's own private
`sensitive-terms.local.txt`, de-duplicates against what is already in the
Inbox, and files each candidate into `candidates/`, `manual-review/`, or
`rejected/`. Processed zips move to `imports/processed/` -- never deleted, so
an import can be re-examined or re-run without losing the source archive.

This tool never modifies formal `evals/`, Skill files, or Git state. Turning
imported candidates into formal Evals is a separate, explicit
`developing-skills` batch-review step (see INSTALL.md section 9 / AGENTS.md
"Interaction-derived Eval capture").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_eval_candidate import (  # noqa: E402
    ALLOWED_KINDS,
    find_project_config,
    load_config,
    load_private_terms,
    scan_sensitive,
    validate_candidate,
)
from eval_bundle_contract import validate_bundle_manifest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge exported interaction Eval candidate zips into the local Eval Inbox."
    )
    parser.add_argument("--config", help="Explicit config JSON path. Defaults to project/user config discovery.")
    parser.add_argument(
        "--eval-inbox",
        help="Explicit Eval Inbox path, overriding config discovery. Defaults to .local/eval-inbox in this repository.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report what would be imported without writing anything.")
    return parser.parse_args()


def resolve_inbox(args: argparse.Namespace) -> tuple[Path, list[str]]:
    terms: list[str] = []
    if args.eval_inbox:
        return Path(args.eval_inbox).expanduser().resolve(), terms
    try:
        config_path = Path(args.config).expanduser().resolve() if args.config else find_project_config(ROOT)
        if config_path is None:
            config_path = Path.home() / ".cloudskill" / "config.json"
        if config_path.is_file():
            config = load_config(config_path)
            terms = load_private_terms(config["_sensitive_terms_file"])
            return config["_inbox_path"], terms
    except (OSError, ValueError, KeyError):
        pass
    return (ROOT / ".local" / "eval-inbox").resolve(), terms


def content_key(candidate: dict[str, Any]) -> str:
    stripped = {
        key: value
        for key, value in candidate.items()
        if key not in {"candidate_id", "captured_at", "capture_config", "sanitization"}
    }
    payload = json.dumps(stripped, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def existing_content_keys(inbox: Path) -> set[str]:
    keys: set[str] = set()
    for folder in ("candidates", "manual-review", "rejected"):
        directory = inbox / folder
        if not directory.is_dir():
            continue
        for path in directory.glob("*.json"):
            try:
                candidate = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(candidate, dict):
                keys.add(content_key(candidate))
    return keys


def write_candidate(inbox: Path, queue: str, candidate: dict[str, Any], dry_run: bool) -> Path:
    candidate_id = candidate.get("candidate_id") or "INT-imported"
    kind = candidate.get("case_kind", "candidate")
    target = inbox / queue / f"{candidate_id}-{kind}.json"
    suffix = 1
    while target.exists():
        target = inbox / queue / f"{candidate_id}-{kind}-{suffix}.json"
        suffix += 1
    if dry_run:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(candidate, ensure_ascii=False, indent=2) + "\n"
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(serialized, encoding="utf-8")
    tmp.replace(target)
    return target


def import_zip(zip_path: Path, inbox: Path, terms: list[str], seen_keys: set[str], dry_run: bool) -> dict[str, int]:
    counts = {"candidates": 0, "manual_review": 0, "rejected": 0, "duplicate": 0, "skipped": 0, "unsupported": 0}
    with tempfile.TemporaryDirectory(prefix="cloudskill-import-") as tmp_name:
        tmp = Path(tmp_name)
        try:
            with zipfile.ZipFile(zip_path) as archive:
                names = archive.namelist()
                if "manifest.json" not in names:
                    counts["unsupported"] = 1
                    return counts
                if len(names) != len(set(names)) or any(Path(name).is_absolute() or ".." in Path(name).parts for name in names):
                    raise ValueError("unsafe or duplicate archive member")
                manifest = json.loads(archive.read("manifest.json"))
                if not isinstance(manifest, dict) or validate_bundle_manifest(manifest):
                    counts["unsupported"] = 1
                    return counts
                if set(names) != {"manifest.json", *manifest["payload_hashes"].keys()}:
                    raise ValueError("archive contains undeclared or missing payload members")
                for name, digest in manifest["payload_hashes"].items():
                    if name not in names or hashlib.sha256(archive.read(name)).hexdigest() != digest:
                        raise ValueError("payload hash mismatch")
                archive.extractall(tmp)
        except (zipfile.BadZipFile, ValueError, json.JSONDecodeError):
            print(f"ERROR: {zip_path.name}: not a valid zip archive; leaving in imports/ for manual review")
            counts["skipped"] += 1
            return counts

        for candidate_path in sorted(tmp.rglob("*.json")):
            if candidate_path.name == "manifest.json":
                continue
            try:
                candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                counts["skipped"] += 1
                continue
            if not isinstance(candidate, dict) or "case_kind" not in candidate:
                counts["skipped"] += 1
                continue

            kind = candidate.get("case_kind")
            if kind not in ALLOWED_KINDS:
                candidate.setdefault("sanitization", {})["import_errors"] = [f"unknown case_kind: {kind!r}"]
                write_candidate(inbox, "rejected", candidate, dry_run)
                counts["rejected"] += 1
                continue

            errors = validate_candidate(candidate, kind)
            if errors:
                candidate.setdefault("sanitization", {})["import_errors"] = errors
                write_candidate(inbox, "rejected", candidate, dry_run)
                counts["rejected"] += 1
                continue

            key = content_key(candidate)
            if key in seen_keys:
                counts["duplicate"] += 1
                continue
            seen_keys.add(key)

            findings = scan_sensitive(candidate, terms)
            sanitization = candidate.setdefault("sanitization", {})
            already_flagged = sanitization.get("status") == "MANUAL_REQUIRED"
            if findings or already_flagged or not terms:
                sanitization["status"] = "MANUAL_REQUIRED"
                if findings:
                    sanitization["import_reconfirmed_findings"] = findings
                queue = "manual-review"
                counts["manual_review"] += 1
            else:
                sanitization["status"] = "PASS"
                queue = "candidates"
                counts["candidates"] += 1
            write_candidate(inbox, queue, candidate, dry_run)

    return counts


def import_archives(inbox: Path, terms: list[str], dry_run: bool) -> dict[str, int]:
    """Import pending archives while preserving the manual CLI semantics."""
    imports_dir = inbox / "imports"
    processed_dir = imports_dir / "processed"
    unsupported_dir = imports_dir / "unsupported"
    if not dry_run:
        for folder in ("candidates", "manual-review", "rejected", "imports", "imports/processed", "imports/unsupported"):
            (inbox / folder).mkdir(parents=True, exist_ok=True)

    zips = sorted(p for p in imports_dir.glob("*.zip") if p.is_file()) if imports_dir.is_dir() else []
    if not zips:
        print(f"No import archives found in {imports_dir}")
        return {"archives": 0, "candidates": 0, "manual_review": 0, "rejected": 0, "duplicate": 0, "skipped": 0, "unsupported": 0}
    if not terms:
        print(
            "WARNING: no private sensitive-terms file resolved; every imported candidate "
            "will be conservatively routed to manual-review/ regardless of its exported status."
        )

    seen_keys = existing_content_keys(inbox)
    totals = {"candidates": 0, "manual_review": 0, "rejected": 0, "duplicate": 0, "skipped": 0, "unsupported": 0}
    for zip_path in zips:
        counts = import_zip(zip_path, inbox, terms, seen_keys, dry_run)
        for key, value in counts.items():
            totals[key] += value
        print(
            f"{zip_path.name}: candidates={counts['candidates']} manual_review={counts['manual_review']} "
            f"rejected={counts['rejected']} duplicate={counts['duplicate']} skipped={counts['skipped']} unsupported={counts['unsupported']}"
        )
        if not dry_run and counts["unsupported"]:
            unsupported_dir.mkdir(parents=True, exist_ok=True)
            target = unsupported_dir / zip_path.name
            shutil.move(str(zip_path), str(target))
            sidecar = target.with_suffix(target.suffix + ".status.json")
            sidecar.write_text(json.dumps({"bundle_id": hashlib.sha256(target.read_bytes()).hexdigest()[:16], "status": "UNSUPPORTED", "archive": target.name}, indent=2) + "\n", encoding="utf-8")
        elif not dry_run and not counts["skipped"]:
            processed_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(zip_path), str(processed_dir / zip_path.name))

    print(
        f"TOTAL: {len(zips)} archive(s); candidates={totals['candidates']} "
        f"manual_review={totals['manual_review']} rejected={totals['rejected']} "
        f"duplicate={totals['duplicate']} skipped={totals['skipped']} unsupported={totals['unsupported']}"
    )
    if dry_run:
        print("DRY RUN: no files were written or moved.")
    return {"archives": len(zips), **totals}


def main() -> int:
    args = parse_args()
    inbox, terms = resolve_inbox(args)
    import_archives(inbox, terms, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
