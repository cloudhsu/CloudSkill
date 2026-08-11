"""Executable interpreter for CloudBox's authoritative tool-adapter contracts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

import task_continuity_runner as schema_runtime

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config/tool-adapters.json"
REGISTRY_SCHEMA_PATH = ROOT / "evals/agent/contracts/tool-adapter-registry.schema.json"
INVOCATION_SCHEMA_PATH = ROOT / "evals/agent/contracts/tool-invocation.schema.json"
RESULT_SCHEMA_PATH = ROOT / "evals/agent/contracts/tool-result.schema.json"
ACTION_SCHEMA_PATH = ROOT / "evals/agent/contracts/tool-action-state.schema.json"


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON member: {key}")
        value[key] = item
    return value


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _schema_errors(value: Any, path: Path) -> list[str]:
    try:
        schema = _load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"cannot load authoritative schema {path.name}: {exc}"]
    return schema_runtime.validate_schema_instance(value, schema)


def contract_fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_target_digest(targets: dict[str, Any]) -> str:
    payload = {"kind": targets.get("kind"), "items": targets.get("items")}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def validate_operation_targets(capability_id: str, targets: Any, registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(targets, dict) or set(targets) != {"kind", "digest", "items"}:
        return ["operation_targets must be a closed kind/digest/items object"]
    try:
        capability = next(
            capability
            for adapter in registry.get("adapters", [])
            for capability in adapter.get("capabilities", [])
            if capability.get("capability_id") == capability_id
        )
    except StopIteration:
        return [f"operation_targets reference unknown capability: {capability_id}"]
    kind = targets.get("kind")
    items = targets.get("items")
    if kind != capability.get("target_kind"):
        errors.append("operation_targets kind does not match capability policy")
    if not isinstance(items, list):
        return errors + ["operation_targets items must be an array"]
    if len(items) > capability.get("max_target_items", -1):
        errors.append("operation_targets exceed capability item bound")
    if targets.get("digest") != canonical_target_digest(targets):
        errors.append("operation_targets digest does not match canonical targets")
    canonical_items = json.loads(json.dumps(items, ensure_ascii=False, sort_keys=True))
    sort_field = "ref" if kind == "git-fetch-refs" else "relative_path" if kind == "eval-bundle-archives" else None
    ordered = sorted(canonical_items, key=lambda item: item.get(sort_field, "") if isinstance(item, dict) and sort_field else "")
    if items != ordered:
        errors.append("operation_targets items must use canonical ordering")
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"operation_targets.items[{index}] must be an object")
            continue
        key = json.dumps(item, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        if key in seen:
            errors.append(f"operation_targets.items[{index}] is duplicated")
        seen.add(key)
        if kind == "none":
            errors.append("none operation_targets cannot contain items")
        elif kind == "git-fetch-refs":
            if set(item) != {"ref", "object_id"}:
                errors.append(f"operation_targets.items[{index}] has invalid fetch fields")
            if not isinstance(item.get("ref"), str) or not re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]+", item.get("ref", "")) or ".." in item.get("ref", "").split("/"):
                errors.append(f"operation_targets.items[{index}] has invalid ref")
            if not isinstance(item.get("object_id"), str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", item.get("object_id", "")):
                errors.append(f"operation_targets.items[{index}] has invalid object_id")
        elif kind == "eval-bundle-archives":
            if set(item) != {"relative_path", "sha256", "size_bytes"}:
                errors.append(f"operation_targets.items[{index}] has invalid archive fields")
            relative = item.get("relative_path")
            path = PurePosixPath(relative) if isinstance(relative, str) else None
            if path is None or path.is_absolute() or len(path.parts) != 2 or path.parts[0] != "imports" or path.suffix != ".zip" or ".." in path.parts:
                errors.append(f"operation_targets.items[{index}] has invalid archive path")
            if not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", "")):
                errors.append(f"operation_targets.items[{index}] has invalid sha256")
            size = item.get("size_bytes")
            if not isinstance(size, int) or isinstance(size, bool) or size < 0:
                errors.append(f"operation_targets.items[{index}] has invalid size_bytes")
    return errors


def validate_registry(value: Any, schema_path: Path = REGISTRY_SCHEMA_PATH) -> list[str]:
    errors = _schema_errors(value, schema_path)
    if not isinstance(value, dict):
        return errors
    adapters = value.get("adapters")
    if not isinstance(adapters, list):
        return errors
    adapter_ids: set[str] = set()
    for adapter_index, adapter in enumerate(adapters):
        if not isinstance(adapter, dict):
            continue
        adapter_id = adapter.get("adapter_id")
        if adapter_id in adapter_ids:
            errors.append(f"duplicate adapter_id: {adapter_id}")
        elif isinstance(adapter_id, str):
            adapter_ids.add(adapter_id)
        capability_ids: set[str] = set()
        for capability_index, capability in enumerate(adapter.get("capabilities", [])):
            if not isinstance(capability, dict):
                continue
            capability_id = capability.get("capability_id")
            location = f"adapters[{adapter_index}].capabilities[{capability_index}]"
            if capability_id in capability_ids:
                errors.append(f"{location}: duplicate capability_id: {capability_id}")
            elif isinstance(capability_id, str):
                capability_ids.add(capability_id)
            risk = capability.get("risk")
            authority = capability.get("required_authority")
            if risk != "read-only" and not authority:
                errors.append(f"{location}: mutating capability requires authority")
            if risk == "remote-mutating" and not capability.get("supports_reconciliation"):
                errors.append(f"{location}: remote mutation requires reconciliation")
            argument_schema = capability.get("argument_schema")
            if isinstance(argument_schema, dict):
                if argument_schema.get("type") != "object" or argument_schema.get("additionalProperties") is not False:
                    errors.append(f"{location}: argument schema must be a closed object")
            if capability.get("target_kind") == "none" and capability.get("max_target_items") != 0:
                errors.append(f"{location}: none target policy must have zero item bound")
    return errors


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    value = _load_json(path)
    errors = validate_registry(value)
    if errors:
        raise ValueError("invalid tool adapter registry: " + "; ".join(errors))
    return value


def get_capability(registry: dict[str, Any], adapter_id: str, capability_id: str) -> dict[str, Any]:
    for adapter in registry.get("adapters", []):
        if adapter.get("adapter_id") != adapter_id:
            continue
        for capability in adapter.get("capabilities", []):
            if capability.get("capability_id") == capability_id:
                return capability
        raise ValueError(f"unknown capability_id for {adapter_id}: {capability_id}")
    raise ValueError(f"unknown adapter_id: {adapter_id}")


def get_adapter(registry: dict[str, Any], adapter_id: str) -> dict[str, Any]:
    for adapter in registry.get("adapters", []):
        if adapter.get("adapter_id") == adapter_id:
            return adapter
    raise ValueError(f"unknown adapter_id: {adapter_id}")


def validate_invocation(value: Any, registry: dict[str, Any]) -> list[str]:
    errors = _schema_errors(value, INVOCATION_SCHEMA_PATH)
    if not isinstance(value, dict):
        return errors
    forbidden = set(value) & {"command", "executable", "secret_values", "environment", "cwd"}
    if forbidden:
        errors.append("invocation contains broker-owned fields: " + ", ".join(sorted(forbidden)))
    try:
        capability = get_capability(registry, value.get("adapter_id"), value.get("capability_id"))
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    arguments = value.get("arguments")
    argument_schema = capability.get("argument_schema")
    if isinstance(argument_schema, dict):
        errors.extend(f"arguments: {error}" for error in schema_runtime.validate_schema_instance(arguments, argument_schema))
    if capability.get("risk") != "read-only" and not value.get("authority_grant_id"):
        errors.append("mutating invocation requires authority_grant_id")
    errors.extend(validate_operation_targets(value.get("capability_id"), value.get("operation_targets"), registry))
    return errors


def validate_result(value: Any) -> list[str]:
    errors = _schema_errors(value, RESULT_SCHEMA_PATH)
    if isinstance(value, dict) and isinstance(value.get("output"), dict):
        observed = hashlib.sha256(json.dumps(value["output"], sort_keys=True).encode("utf-8")).hexdigest()
        if value.get("output_hash") != observed:
            errors.append("result output_hash does not match canonical output")
    return errors


def validate_action_state(value: Any) -> list[str]:
    errors = _schema_errors(value, ACTION_SCHEMA_PATH)
    if isinstance(value, dict):
        attempt = value.get("attempt")
        maximum = value.get("max_attempts")
        if isinstance(attempt, int) and not isinstance(attempt, bool) and isinstance(maximum, int) and not isinstance(maximum, bool) and attempt > maximum:
            errors.append("action attempt exceeds max_attempts")
    return errors
