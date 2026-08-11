"""Executable interpreter for CloudBox's authoritative tool-adapter contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
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
    return errors


def validate_result(value: Any) -> list[str]:
    return _schema_errors(value, RESULT_SCHEMA_PATH)


def validate_action_state(value: Any) -> list[str]:
    errors = _schema_errors(value, ACTION_SCHEMA_PATH)
    if isinstance(value, dict):
        attempt = value.get("attempt")
        maximum = value.get("max_attempts")
        if isinstance(attempt, int) and not isinstance(attempt, bool) and isinstance(maximum, int) and not isinstance(maximum, bool) and attempt > maximum:
            errors.append("action attempt exceeds max_attempts")
    return errors
