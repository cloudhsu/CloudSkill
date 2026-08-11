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
import stat
import sys
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
from eval_bundle_contract import bundle_filename, validate_bundle_manifest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MAX_ARCHIVE_MEMBERS = 64
MAX_MEMBER_BYTES = 4 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 16 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200
MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
MAX_MEMBER_PATH_BYTES = 1024
MAX_MEMBER_COMPONENT_BYTES = 255


def retained_target(directory: Path, name: str) -> Path:
    """Choose a destination without overwriting previously retained evidence."""
    target = directory / name
    suffix = 1
    while target.exists():
        target = directory / f"{Path(name).stem}-{suffix}{Path(name).suffix}"
        suffix += 1
    return target


def validate_archive_resources(zip_path: Path, archive: zipfile.ZipFile) -> None:
    if zip_path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("compressed archive exceeds size limit")
    infos = archive.infolist()
    if len(infos) > MAX_ARCHIVE_MEMBERS:
        raise ValueError("archive has too many members")
    total = 0
    for info in infos:
        encoded_name = info.filename.encode("utf-8")
        if len(encoded_name) > MAX_MEMBER_PATH_BYTES or any(
            len(part.encode("utf-8")) > MAX_MEMBER_COMPONENT_BYTES for part in Path(info.filename).parts
        ):
            raise ValueError("archive member path exceeds length limit")
        mode = info.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if info.is_dir() or file_type not in (0, stat.S_IFREG):
            raise ValueError("archive contains a non-regular member")
        if info.file_size > MAX_MEMBER_BYTES:
            raise ValueError("archive member exceeds size limit")
        total += info.file_size
        if total > MAX_TOTAL_UNCOMPRESSED_BYTES:
            raise ValueError("archive exceeds total uncompressed size limit")
        if info.file_size and (not info.compress_size or info.file_size > info.compress_size * MAX_COMPRESSION_RATIO):
            raise ValueError("archive member exceeds compression-ratio limit")


def resolve_private_terms(inbox: Path, config_path: Path | None = None) -> list[str]:
    """Resolve terms only from a safe config that owns the requested inbox."""
    selected = config_path
    if selected is None:
        selected = find_project_config(ROOT)
        if selected is None:
            user_config = Path.home() / ".cloudskill" / "config.json"
            selected = user_config if user_config.is_file() else None
    if selected is None or not selected.is_file():
        return []
    config = load_config(selected)
    if config["_inbox_path"] != inbox.expanduser().resolve():
        raise ValueError("CloudSkill config does not own the requested Eval Inbox")
    return load_private_terms(config["_sensitive_terms_file"])


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
        inbox = Path(args.eval_inbox).expanduser().resolve()
        config_paths = []
        if args.config:
            config_paths.append(Path(args.config).expanduser().resolve())
        else:
            project_config = find_project_config(ROOT)
            if project_config is not None:
                config_paths.append(project_config)
            config_paths.append(Path.home() / ".cloudskill" / "config.json")
        for config_path in config_paths:
            if not config_path.is_file():
                continue
            try:
                terms = resolve_private_terms(inbox, config_path)
            except (OSError, ValueError, KeyError):
                continue
            return inbox, terms
        return inbox, terms
    try:
        config_path = Path(args.config).expanduser().resolve() if args.config else find_project_config(ROOT)
        if config_path is None:
            config_path = Path.home() / ".cloudskill" / "config.json"
        if config_path.is_file():
            config = load_config(config_path)
            terms = resolve_private_terms(config["_inbox_path"], config_path)
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
    if queue not in {"candidates", "manual-review", "rejected"}:
        raise ValueError("invalid candidate queue")
    serialized = json.dumps(candidate, ensure_ascii=False, indent=2) + "\n"
    local_id = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:20]
    kind = candidate.get("case_kind") if candidate.get("case_kind") in ALLOWED_KINDS else "candidate"
    inbox_root = inbox.resolve()
    queue_path = inbox / queue
    if queue_path.is_symlink():
        raise ValueError("candidate queue may not be a symlink")
    queue_root = queue_path.resolve()
    if queue_root.parent != inbox_root:
        raise ValueError("candidate queue escapes Inbox")
    target = queue_root / f"INT-imported-{local_id}-{kind}.json"
    safe_stem = target.stem
    suffix = 1
    while target.exists():
        target = queue_root / f"{safe_stem}-{suffix}.json"
        suffix += 1
    if dry_run:
        return target
    queue_root.mkdir(parents=True, exist_ok=True)
    if target.resolve().parent != queue_root:
        raise ValueError("candidate output escapes queue")
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(serialized, encoding="utf-8")
    tmp.replace(target)
    return target


def import_zip(zip_path: Path, inbox: Path, terms: list[str], seen_keys: set[str], dry_run: bool) -> dict[str, int]:
    counts = {"candidates": 0, "manual_review": 0, "rejected": 0, "duplicate": 0, "skipped": 0, "unsupported": 0}
    planned: list[tuple[str, dict[str, Any], str | None]] = []
    planned_keys: set[str] = set()
    try:
        with zipfile.ZipFile(zip_path) as archive:
            validate_archive_resources(zip_path, archive)
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
            if zip_path.name != bundle_filename(manifest):
                counts["unsupported"] = 1
                return counts
            if set(names) != {"manifest.json", *manifest["payload_hashes"].keys()}:
                raise ValueError("archive contains undeclared or missing payload members")
            for name, digest in manifest["payload_hashes"].items():
                if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                    raise ValueError("payload hash mismatch")
            candidate_names = sorted(name for name in manifest["payload_hashes"] if name.endswith(".json"))
            if len(candidate_names) != len(manifest["payload_hashes"]):
                raise ValueError("archive payload must contain only candidate JSON")
            for candidate_name in candidate_names:
                candidate = json.loads(archive.read(candidate_name))
                if not isinstance(candidate, dict) or "case_kind" not in candidate:
                    raise ValueError("candidate payload is not a candidate object")
                kind = candidate.get("case_kind")
                if kind not in ALLOWED_KINDS:
                    candidate.setdefault("sanitization", {})["import_errors"] = [f"unknown case_kind: {kind!r}"]
                    planned.append(("rejected", candidate, None))
                    counts["rejected"] += 1
                    continue
                errors = validate_candidate(candidate, kind)
                if errors:
                    candidate.setdefault("sanitization", {})["import_errors"] = errors
                    planned.append(("rejected", candidate, None))
                    counts["rejected"] += 1
                    continue
                key = content_key(candidate)
                if key in seen_keys or key in planned_keys:
                    counts["duplicate"] += 1
                    continue
                planned_keys.add(key)
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
                planned.append((queue, candidate, key))
    except (OSError, RuntimeError, zipfile.BadZipFile, ValueError, json.JSONDecodeError, UnicodeDecodeError):
        print(f"ERROR: {zip_path.name}: not a valid zip archive; leaving in imports/ for manual review")
        return {**{key: 0 for key in counts}, "skipped": 1}

    for queue, candidate, key in planned:
        write_candidate(inbox, queue, candidate, dry_run)
        if key is not None:
            seen_keys.add(key)

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
            target = retained_target(unsupported_dir, zip_path.name)
            shutil.move(str(zip_path), str(target))
            sidecar = target.with_suffix(target.suffix + ".status.json")
            sidecar.write_text(json.dumps({"bundle_id": hashlib.sha256(target.read_bytes()).hexdigest()[:16], "status": "UNSUPPORTED", "archive": target.name}, indent=2) + "\n", encoding="utf-8")
        elif not dry_run and not counts["skipped"]:
            processed_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(zip_path), str(retained_target(processed_dir, zip_path.name)))

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
