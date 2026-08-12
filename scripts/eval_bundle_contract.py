from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

BUNDLE_FORMAT_VERSION = "2.0"
EXPORTER_VERSION = "2.0"
SUPPORTED_BUNDLE_FORMATS = {BUNDLE_FORMAT_VERSION}
SUPPORTED_CANDIDATE_SCHEMA_VERSIONS = {"1.0"}
SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
LOWER_COMPONENT = re.compile(r"^[a-z0-9][a-z0-9-]*$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def normalize_filename_component(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-_")
    if not normalized or not SAFE_COMPONENT.fullmatch(normalized):
        raise ValueError("filename component is empty or unsafe")
    return normalized


def build_bundle_manifest(*, cloudbox_version: str, candidate_schema_version: str,
                          host: str, agent_name: str, export_project_name: str,
                          payload_hashes: dict[str, str], now: datetime | None = None,
                          bundle_id: str | None = None) -> dict[str, Any]:
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest = {
        "bundle_format_version": BUNDLE_FORMAT_VERSION,
        "cloudbox_version": cloudbox_version,
        "exporter_version": EXPORTER_VERSION,
        "candidate_schema_version": candidate_schema_version,
        "host": normalize_filename_component(host).replace("_", "-").lower(),
        "agent_name": normalize_filename_component(agent_name).replace("_", "-").lower(),
        "export_project_name": normalize_filename_component(export_project_name),
        "created_at_utc": stamp,
        "bundle_id": bundle_id or uuid.uuid4().hex,
        "payload_hashes": dict(sorted(payload_hashes.items())),
    }
    errors = validate_bundle_manifest(manifest)
    if errors:
        raise ValueError("; ".join(errors))
    return manifest


def validate_bundle_manifest(value: dict[str, Any]) -> list[str]:
    required = {"bundle_format_version", "cloudbox_version", "exporter_version", "candidate_schema_version", "host", "agent_name", "export_project_name", "created_at_utc", "bundle_id", "payload_hashes"}
    errors = [f"missing field: {key}" for key in sorted(required - set(value))]
    if set(value) - required:
        errors.append("unexpected fields: " + ", ".join(sorted(set(value) - required)))
    if value.get("bundle_format_version") not in SUPPORTED_BUNDLE_FORMATS:
        errors.append("unsupported bundle format")
    if value.get("exporter_version") != EXPORTER_VERSION:
        errors.append("unsupported exporter version")
    if value.get("candidate_schema_version") not in SUPPORTED_CANDIDATE_SCHEMA_VERSIONS:
        errors.append("unsupported candidate schema version")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(value.get("cloudbox_version", ""))):
        errors.append("invalid CloudBox version")
    for key in ("host", "agent_name"):
        if not LOWER_COMPONENT.fullmatch(str(value.get(key, ""))):
            errors.append(f"unsafe {key}")
    if not SAFE_COMPONENT.fullmatch(str(value.get("export_project_name", ""))):
        errors.append("unsafe export_project_name")
    if not re.fullmatch(r"[0-9]{8}T[0-9]{6}Z", str(value.get("created_at_utc", ""))):
        errors.append("invalid UTC timestamp")
    if not re.fullmatch(r"[0-9a-f]{32}", str(value.get("bundle_id", ""))):
        errors.append("invalid bundle ID")
    hashes = value.get("payload_hashes")
    if not isinstance(hashes, dict) or any(not HEX64.fullmatch(str(v)) for v in hashes.values()):
        errors.append("invalid payload hashes")
    text = repr(value).lower()
    if any(marker in text for marker in ("https://", "http://", "token=", "password=", "/users/", "c:\\")):
        errors.append("manifest contains connectivity or private-path data")
    return errors


def bundle_filename(manifest: dict[str, Any]) -> str:
    errors = validate_bundle_manifest(manifest)
    if errors:
        raise ValueError("; ".join(errors))
    return "-".join((manifest["export_project_name"], manifest["host"], manifest["agent_name"], manifest["created_at_utc"], manifest["bundle_id"][:8])) + ".zip"
