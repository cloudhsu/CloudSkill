"""Shared adapter for the authoritative Runtime Eval provider registry.

The JSON contract at evals/runtime/contracts/providers.json is authoritative.
Every module that dispatches on `--provider` must import provider IDs from
here instead of hand-copying a literal tuple. See
scripts/validate_providers_contract.py for the drift check across consumers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_CONTRACT_PATH = ROOT / "evals" / "runtime" / "contracts" / "providers.json"


def _load_contract() -> dict[str, Any]:
    return json.loads(PROVIDERS_CONTRACT_PATH.read_text(encoding="utf-8"))


_CONTRACT: dict[str, Any] = _load_contract()
PROVIDERS: dict[str, Any] = _CONTRACT["providers"]
PROVIDER_IDS: tuple[str, ...] = tuple(PROVIDERS.keys())
LOCAL_PROVIDER_IDS: tuple[str, ...] = tuple(
    provider_id for provider_id, info in PROVIDERS.items() if info.get("family") == "local"
)
HOSTED_AGENT_PROVIDER_IDS: tuple[str, ...] = tuple(
    provider_id for provider_id, info in PROVIDERS.items() if info.get("family") == "hosted-agent"
)
REQUIRED_CONSUMER_PATHS: tuple[str, ...] = tuple(_CONTRACT.get("required_consumer_paths", ()))


def get_provider(provider_id: str) -> dict[str, Any]:
    try:
        return PROVIDERS[provider_id]
    except KeyError as exc:
        raise KeyError(f"unknown Runtime Eval provider id: {provider_id!r}; known={PROVIDER_IDS}") from exc


def default_model(provider_id: str) -> str:
    return str(get_provider(provider_id).get("default_model", ""))


def refinement_default(provider_id: str) -> str:
    """Return 'auto' (attempt refinement when the raw answer needs it) or 'skip'."""
    return str(get_provider(provider_id).get("refinement_default", "auto"))


def is_hosted_agent(provider_id: str) -> bool:
    return provider_id in HOSTED_AGENT_PROVIDER_IDS
