from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

SOURCE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def load_source_registry(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != "1.0" or not isinstance(value.get("sources"), list):
        raise ValueError("invalid evolution source registry")
    ids = set()
    for source in value["sources"]:
        sid = source.get("source_id")
        if not isinstance(sid, str) or not SOURCE_ID.fullmatch(sid) or sid in ids:
            raise ValueError("invalid or duplicate source_id")
        ids.add(sid)
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", str(source.get("url_secret", ""))):
            raise ValueError("url_secret must be an environment secret name")
        for scoped in source.get("paths", []):
            if Path(scoped).is_absolute() or ".." in Path(scoped).parts:
                raise ValueError("source path escapes scope")
    return value


def resolve_secret_reference(name: str, env: dict[str, str]) -> str:
    value = env.get(name)
    if not value:
        raise ValueError(f"required secret reference {name} is unavailable")
    return value


def _git(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("Git source operation failed; connectivity details redacted")
    return result.stdout.strip()


def inspect_remote(source: dict[str, Any], env: dict[str, str]) -> tuple[str, str]:
    url = resolve_secret_reference(source["url_secret"], env)
    ref = source.get("ref", "HEAD")
    output = _git(["ls-remote", url, ref])
    if not output:
        raise RuntimeError("Git source ref was not found")
    return url, output.split()[0]


def sync_source(source_id: str, registry: dict[str, Any], exchange: Path, env: dict[str, str]) -> dict[str, Any]:
    source = next((item for item in registry["sources"] if item["source_id"] == source_id), None)
    if source is None:
        raise ValueError("unknown source_id")
    url, commit = inspect_remote(source, env)
    root = exchange / "sources" / source_id
    state_path = root / "state" / "checkpoint.json"
    if state_path.is_file() and json.loads(state_path.read_text(encoding="utf-8")).get("commit") == commit:
        return {"status": "NO_CHANGE", "source_id": source_id, "model_calls": 0, "commit_fingerprint": commit[:12]}
    with tempfile.TemporaryDirectory(prefix="cloudskill-source-") as tmp_name:
        checkout = Path(tmp_name) / "source"
        _git(["clone", "--quiet", "--no-checkout", url, str(checkout)])
        _git(["checkout", "--quiet", commit], cwd=checkout)
        paths = source.get("paths") or ["."]
        inventory: list[tuple[str, bytes]] = []
        for scoped in paths:
            base = (checkout / scoped).resolve()
            if checkout.resolve() not in (base, *base.parents):
                raise ValueError("resolved source path escapes checkout")
            if base.is_file(): inventory.append((str(Path(scoped)), base.read_bytes()))
            elif base.is_dir(): inventory.extend((str(path.relative_to(checkout)), path.read_bytes()) for path in sorted(base.rglob("*")) if path.is_file())
        content = hashlib.sha256()
        for relative_path, payload in inventory:
            content.update(relative_path.encode("utf-8"))
            content.update(b"\0")
            content.update(hashlib.sha256(payload).digest())
        digest = content.hexdigest()
    # Stable identity makes every partial-write permutation recoverable: a retry
    # repairs the same candidate/provenance paths before advancing checkpoint.
    operation_id = hashlib.sha256(f"{source_id}\0{commit}\0{digest}".encode()).hexdigest()
    candidate = {"candidate_id": f"SRC-{operation_id[:12]}", "source_id": source_id, "source_commit": commit, "content_fingerprint": digest, "confidence": "inferred", "status": "REVIEW_PENDING", "model_calls": 0}
    provenance = {"operation_id": operation_id, "source_id": source_id, "commit": commit, "content_fingerprint": digest, "candidate_id": candidate["candidate_id"]}
    for folder, name, value in (("candidates", candidate["candidate_id"] + ".json", candidate), ("provenance", operation_id + ".json", provenance)):
        target = root / folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        tmp.replace(target)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"commit": commit, "operation_id": operation_id}, indent=2) + "\n", encoding="utf-8")
    tmp.replace(state_path)
    return {"status": "STORED", "source_id": source_id, "model_calls": 0, "commit_fingerprint": commit[:12], "candidate_id": candidate["candidate_id"]}
