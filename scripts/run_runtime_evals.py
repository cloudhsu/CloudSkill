from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from behavior_output_contract import (
    BEHAVIOR_MIN_FINAL_CHARACTERS,
    BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT,
    BEHAVIOR_OUTPUT_CONTRACT_ID,
    extract_final_value,
)

from runtime_eval_common import (
    BEHAVIOR_DELIVERABLE_SCHEMA,
    CONTEXT_MODES,
    DEFAULT_CASES,
    DEFAULT_SCHEMA,
    MANIFEST,
    ROOT,
    VERSION_FILE,
    ContextBudgetError,
    assert_router_context,
    build_routing_prompt,
    build_selected_skills_prompt,
    load_cases,
    load_manifest,
    load_schema,
    skill_ids,
    validate_decision_shape,
)

from codex_eval_adapter import call_codex_cli, codex_preflight
from claude_eval_adapter import call_claude_cli, claude_preflight
from providers_contract import PROVIDER_IDS

OPENAI_API_URL = "https://api.openai.com/v1/responses"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute CloudBox Routing Evals or two-stage selected-skill Behavior Evals."
    )
    parser.add_argument(
        "--provider",
        choices=(*PROVIDER_IDS, "openai"),
        default="ollama",
        help=(
            "Model runtime: ollama (local, no API key), codex (Codex CLI/GPT), "
            "claude (Claude Code CLI), or the legacy direct-API openai path."
        ),
    )
    parser.add_argument(
        "--model",
        default="qwen3:4b",
        help="Ollama model name or exact OpenAI model name. Default: qwen3:4b.",
    )
    parser.add_argument(
        "--codex-model",
        default="",
        help="Optional Codex CLI model override. Empty uses the authenticated Codex default.",
    )
    parser.add_argument(
        "--claude-model",
        default="",
        help=(
            "Optional Claude Code CLI model override (alias like 'opus'/'sonnet' or a full "
            "model name). Empty uses the CLI's configured default."
        ),
    )
    parser.add_argument(
        "--eval-kind",
        choices=("routing", "behavior"),
        default="routing",
        help="routing performs one routing call; behavior routes first and then executes selected SKILL.md files.",
    )
    parser.add_argument(
        "--context-mode",
        choices=CONTEXT_MODES,
        help="none, manifest, router, or selected-skills. Defaults to router for routing and selected-skills for behavior.",
    )
    parser.add_argument(
        "--allow-context-baseline",
        action="store_true",
        help="Allow executable none/manifest diagnostic baselines. Without this flag Ollama refuses a run that omits using-cloudbox-skills/SKILL.md.",
    )
    parser.add_argument(
        "--context-reserve-tokens",
        type=int,
        default=320,
        help="Tokens reserved for model output and runtime overhead when checking the input context budget.",
    )
    parser.add_argument(
        "--selected-reference-mode",
        choices=("none", "declared"),
        default="declared",
        help="For behavior mode, load no references or references explicitly named by selected SKILL.md files.",
    )
    parser.add_argument(
        "--contract-repair",
        choices=("none", "deterministic"),
        default="deterministic",
        help=(
            "Repair only mechanical routing-contract relations after model output. "
            "The deterministic mode never adds a missing supporting skill or changes primary_skill."
        ),
    )
    parser.add_argument("--repeat", type=int, default=1, help="Attempts per case.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--case-id", action="append", default=[], help="Run only selected case IDs.")
    parser.add_argument("--output", type=Path, help="JSONL output path.")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--max-output-tokens", type=int, default=320)
    parser.add_argument("--behavior-max-output-tokens", type=int, default=1200)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--num-ctx", type=int, default=4096, help="Ollama context length.")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--skip-model-check",
        action="store_true",
        help="Skip the Ollama /api/tags installed-model check.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and validate actual request prompts without calling a model.",
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Include complete system and user prompts in --dry-run JSON output.",
    )
    parser.add_argument(
        "--prompt-output",
        type=Path,
        help="Write each dry-run request payload to this directory for exact prompt inspection.",
    )
    return parser.parse_args()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_output(provider: str, model: str, eval_kind: str, context_mode: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in model)
    return (
        ROOT
        / ".local"
        / "runtime-evals"
        / f"{stamp}-{provider}-{safe_model}-{eval_kind}-{context_mode}.jsonl"
    )


def parse_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start < 0 or end <= start:
            raise RuntimeError(f"model output is not JSON: {candidate[:500]}")
        value = json.loads(candidate[start : end + 1])
    if not isinstance(value, dict):
        raise RuntimeError("model output JSON is not an object")
    return value


def extract_final_deliverable(text: str) -> tuple[str, bool]:
    value, extracted, _contract = extract_final_value(
        text,
        minimum_characters=BEHAVIOR_MIN_FINAL_CHARACTERS,
        allow_legacy_terminal=True,
    )
    return value, extracted

def request_json(
    *,
    url: str,
    body: dict[str, Any] | None,
    timeout: float,
    max_retries: int,
    headers: dict[str, str] | None = None,
    method: str = "POST",
) -> tuple[dict[str, Any], dict[str, str]]:
    encoded = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    retryable = {408, 409, 429, 500, 502, 503, 504}
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        request_headers = {
            "Accept": "application/json",
            "User-Agent": "CloudBox-Runtime-Eval/5.6.0",
        }
        if encoded is not None:
            request_headers["Content-Type"] = "application/json"
        if headers:
            request_headers.update(headers)
        request = urllib.request.Request(
            url,
            data=encoded,
            method=method,
            headers=request_headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return payload, {key.lower(): value for key, value in response.headers.items()}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {exc.code} from {url}: {detail[:1000]}")
            if exc.code not in retryable or attempt >= max_retries:
                raise last_error
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt >= max_retries:
                raise RuntimeError(f"request failed for {url}: {exc}") from exc
        time.sleep(min(2**attempt, 8))
    raise RuntimeError(f"request failed for {url}: {last_error}")


def normalize_ollama_url(value: str) -> str:
    return value.rstrip("/")


def ollama_installed_models(base_url: str, timeout: float) -> set[str]:
    payload, _ = request_json(
        url=f"{normalize_ollama_url(base_url)}/api/tags",
        body=None,
        timeout=timeout,
        max_retries=0,
        method="GET",
    )
    names: set[str] = set()
    for item in payload.get("models", []):
        for key in ("name", "model"):
            value = item.get(key)
            if isinstance(value, str) and value:
                names.add(value)
    return names


def ollama_user_prompt(user_prompt: str) -> str:
    """Prepend the Qwen3 thinking-mode directive. Ollama-only: do not reuse for
    another provider's call path -- Claude Code CLI parses a leading "/word" in
    piped input as a slash command, not literal prompt text."""
    return "/no_think\n\n" + user_prompt


def call_ollama(
    *,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any] | None,
    timeout: float,
    max_retries: int,
    num_ctx: int,
    max_output_tokens: int,
    temperature: float,
    seed: int,
) -> tuple[dict[str, Any] | str, str, dict[str, Any]]:
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ollama_user_prompt(user_prompt)},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": max_output_tokens,
            "seed": seed,
        },
    }
    if schema is not None:
        body["format"] = schema
    payload, _ = request_json(
        url=f"{normalize_ollama_url(base_url)}/api/chat",
        body=body,
        timeout=timeout,
        max_retries=max_retries,
    )
    message = payload.get("message") or {}
    text = message.get("content")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("Ollama response contains no message.content")
    actual: dict[str, Any] | str = parse_json_object(text) if schema is not None else text
    usage = {
        "prompt_tokens": payload.get("prompt_eval_count"),
        "output_tokens": payload.get("eval_count"),
        "total_duration_ns": payload.get("total_duration"),
        "load_duration_ns": payload.get("load_duration"),
        "prompt_eval_duration_ns": payload.get("prompt_eval_duration"),
        "eval_duration_ns": payload.get("eval_duration"),
    }
    metadata = {
        "model_returned": payload.get("model") or model,
        "response_id": None,
        "request_id": None,
        "done_reason": payload.get("done_reason"),
        "usage": {key: value for key, value in usage.items() if value is not None},
    }
    return actual, text, metadata


def response_text(payload: dict[str, Any]) -> str:
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                return content.get("text", "")
            if content.get("type") == "refusal":
                raise RuntimeError(f'model refusal: {content.get("refusal", "")}'.strip())
    raise RuntimeError("Responses API payload contains no output_text")


def call_openai(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any] | None,
    timeout: float,
    max_retries: int,
    max_output_tokens: int,
    client_request_id: str,
) -> tuple[dict[str, Any] | str, str, dict[str, Any]]:
    body: dict[str, Any] = {
        "model": model,
        "instructions": system_prompt,
        "input": user_prompt,
        "store": False,
        "max_output_tokens": max_output_tokens,
    }
    if schema is not None:
        body["text"] = {
            "format": {
                "type": "json_schema",
                "name": "cloudbox_routing_decision",
                "description": "Smallest sufficient downstream CloudBox skill routing decision.",
                "strict": True,
                "schema": schema,
            }
        }
    payload, headers = request_json(
        url=OPENAI_API_URL,
        body=body,
        timeout=timeout,
        max_retries=max_retries,
        headers={
            "Authorization": f"Bearer {api_key}",
            "X-Client-Request-Id": client_request_id,
        },
    )
    text = response_text(payload)
    actual: dict[str, Any] | str = parse_json_object(text) if schema is not None else text
    metadata = {
        "model_returned": payload.get("model"),
        "response_id": payload.get("id"),
        "request_id": headers.get("x-request-id"),
        "done_reason": None,
        "usage": payload.get("usage") or {},
    }
    return actual, text, metadata


def resolve_model_label(args: argparse.Namespace) -> str:
    """Return the model identifier to record/label output with, per provider."""
    if args.provider == "codex":
        return args.codex_model or "codex-default"
    if args.provider == "claude":
        return args.claude_model or "claude-default"
    return args.model


def call_model(
    *,
    args: argparse.Namespace,
    api_key: str | None,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any] | None,
    max_output_tokens: int,
    client_request_id: str,
) -> tuple[dict[str, Any] | str, str, dict[str, Any]]:
    if args.provider == "ollama":
        return call_ollama(
            base_url=args.ollama_url,
            model=args.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            timeout=args.timeout,
            max_retries=args.max_retries,
            num_ctx=args.num_ctx,
            max_output_tokens=max_output_tokens,
            temperature=args.temperature,
            seed=args.seed,
        )
    if args.provider == "codex":
        text, metadata = call_codex_cli(
            model=args.codex_model or None,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            timeout=args.timeout,
        )
        actual: dict[str, Any] | str = parse_json_object(text) if schema is not None else text
        return actual, text, metadata
    if args.provider == "claude":
        text, metadata = call_claude_cli(
            model=args.claude_model or None,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            timeout=args.timeout,
        )
        actual = parse_json_object(text) if schema is not None else text
        return actual, text, metadata
    if args.provider == "openai":
        assert api_key is not None
        return call_openai(
            api_key=api_key,
            model=args.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            timeout=args.timeout,
            max_retries=args.max_retries,
            max_output_tokens=max_output_tokens,
            client_request_id=client_request_id,
        )
    raise SystemExit(f"unsupported --provider: {args.provider}")


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def deterministic_contract_repair(
    decision: dict[str, Any], valid_skills: set[str]
) -> tuple[dict[str, Any], list[str]]:
    """Repair mechanical JSON relations without changing the model's routing classification."""

    repaired = json.loads(json.dumps(decision, ensure_ascii=False))
    changes: list[str] = []
    if set(repaired) != {
        "primary_skill",
        "supporting_skills",
        "rejected_skills",
        "execution_order",
        "reason",
        "confidence",
    }:
        return repaired, changes

    primary = repaired.get("primary_skill")
    supporting = repaired.get("supporting_skills")
    rejected = repaired.get("rejected_skills")
    order = repaired.get("execution_order")
    if primary is not None and not isinstance(primary, str):
        return repaired, changes
    if not all(
        isinstance(value, list) and all(isinstance(item, str) for item in value)
        for value in (supporting, rejected, order)
    ):
        return repaired, changes
    all_ids = ([primary] if isinstance(primary, str) else []) + supporting + rejected + order
    if any(item not in valid_skills for item in all_ids):
        return repaired, changes

    new_supporting = _dedupe_strings(supporting)
    if isinstance(primary, str):
        new_supporting = [item for item in new_supporting if item != primary]
    new_supporting = [item for item in new_supporting if item != "using-cloudbox-skills"]
    if new_supporting != supporting:
        changes.append("normalized supporting_skills duplicates/overlap/router inclusion")
        repaired["supporting_skills"] = new_supporting

    selected = ([primary] if isinstance(primary, str) else []) + new_supporting
    selected_set = set(selected)
    new_rejected = [item for item in _dedupe_strings(rejected) if item not in selected_set]
    if new_rejected != rejected:
        changes.append("removed selected-skill overlap from rejected_skills")
        repaired["rejected_skills"] = new_rejected

    if primary is None:
        new_order: list[str] = []
    else:
        # Preserve any model-provided selected order, then append missing selected IDs.
        new_order = [item for item in _dedupe_strings(order) if item in selected_set]
        for item in selected:
            if item not in new_order:
                new_order.append(item)
    if new_order != order:
        changes.append("reconciled execution_order with the selected skill set")
        repaired["execution_order"] = new_order

    return repaired, changes


def resolve_context_mode(args: argparse.Namespace) -> str:
    if args.context_mode:
        return args.context_mode
    return "selected-skills" if args.eval_kind == "behavior" else "router"


def validate_mode(args: argparse.Namespace, context_mode: str) -> None:
    if args.eval_kind == "routing" and context_mode == "selected-skills":
        raise SystemExit("--context-mode selected-skills requires --eval-kind behavior")
    if args.eval_kind == "behavior" and context_mode != "selected-skills":
        raise SystemExit("--eval-kind behavior requires --context-mode selected-skills")
    if args.context_reserve_tokens < 1 or args.context_reserve_tokens >= args.num_ctx:
        raise SystemExit("--context-reserve-tokens must be positive and smaller than --num-ctx")
    if args.max_output_tokens < 1 or args.behavior_max_output_tokens < 1:
        raise SystemExit("output token limits must be positive")
    if args.provider == "ollama" and not args.dry_run:
        omits_router = args.eval_kind == "routing" and context_mode in {"none", "manifest"}
        if omits_router and not args.allow_context_baseline:
            raise SystemExit(
                "Refusing invalid Ollama score: using-cloudbox-skills/SKILL.md is not loaded in "
                f"--context-mode {context_mode}. Use --context-mode router, or add "
                "--allow-context-baseline only for an explicitly labeled diagnostic comparison."
            )


def select_cases(suite: dict[str, Any], requested_ids: list[str]) -> list[dict[str, Any]]:
    cases = suite["cases"]
    if requested_ids:
        requested = set(requested_ids)
        cases = [case for case in cases if case["id"] in requested]
        missing = sorted(requested - {case["id"] for case in cases})
        if missing:
            raise SystemExit(f"unknown --case-id values: {missing}")
    if not cases:
        raise SystemExit("no cases selected")
    return cases


def build_routing_bundle(
    *,
    args: argparse.Namespace,
    manifest: dict[str, Any],
    schema: dict[str, Any],
    case: dict[str, Any],
    context_mode: str,
) -> dict[str, Any]:
    routing_mode = "router" if context_mode == "selected-skills" else context_mode
    bundle = build_routing_prompt(
        manifest=manifest,
        schema=schema,
        case=case,
        context_mode=routing_mode,
        num_ctx=args.num_ctx,
        reserve_output_tokens=max(args.context_reserve_tokens, args.max_output_tokens),
        manifest_path=MANIFEST,
        schema_path=args.schema,
        cases_path=args.cases,
    )
    if routing_mode == "router":
        assert_router_context(bundle)
    return bundle


def prompt_request_payload(
    *,
    args: argparse.Namespace,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any] | None,
    max_output_tokens: int,
) -> dict[str, Any]:
    if args.provider == "ollama":
        payload: dict[str, Any] = {
            "model": args.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ollama_user_prompt(user_prompt)},
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": args.temperature,
                "num_ctx": args.num_ctx,
                "num_predict": max_output_tokens,
                "seed": args.seed,
            },
        }
        if schema is not None:
            payload["format"] = schema
        return payload
    if args.provider == "codex":
        return {
            "provider": "codex",
            "model": args.codex_model or "codex-default",
            "sandbox": "read-only",
            "ephemeral": True,
            "isolated_git_repository": True,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "output_schema": schema,
            "max_output_tokens_advisory": max_output_tokens,
        }
    if args.provider == "claude":
        return {
            "provider": "claude",
            "model": args.claude_model or "claude-default",
            "safe_mode": True,
            "tools_disabled": True,
            "no_session_persistence": True,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "json_schema": schema,
            "max_output_tokens_advisory": max_output_tokens,
        }
    payload = {
        "model": args.model,
        "instructions": system_prompt,
        "input": user_prompt,
        "store": False,
        "max_output_tokens": max_output_tokens,
    }
    if schema is not None:
        payload["text"] = {"format": {"type": "json_schema", "schema": schema}}
    return payload


def write_prompt_file(directory: Path, name: str, payload: dict[str, Any]) -> str:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.prompt.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path)


def dry_run_plan(
    *,
    args: argparse.Namespace,
    manifest: dict[str, Any],
    schema: dict[str, Any],
    suite: dict[str, Any],
    cases: list[dict[str, Any]],
    version: str,
    context_mode: str,
    output: Path,
) -> dict[str, Any]:
    case_plans = []
    for case in cases:
        bundle = build_routing_bundle(
            args=args,
            manifest=manifest,
            schema=schema,
            case=case,
            context_mode=context_mode,
        )
        request_payload = prompt_request_payload(
            args=args,
            system_prompt=bundle["system_prompt"],
            user_prompt=bundle["user_prompt"],
            schema=schema,
            max_output_tokens=args.max_output_tokens,
        )
        case_plan: dict[str, Any] = {
            "case_id": case["id"],
            "routing_context": bundle["context"],
            "behavior_context": {
                "status": "deferred until router returns actual primary/supporting skills"
            }
            if args.eval_kind == "behavior"
            else None,
        }
        if args.show_prompt:
            case_plan["routing_request"] = request_payload
        if args.prompt_output:
            case_plan["routing_prompt_file"] = write_prompt_file(
                args.prompt_output,
                f'{case["id"]}-routing-router' if context_mode == "selected-skills" else f'{case["id"]}-routing-{context_mode}',
                request_payload,
            )
        case_plans.append(case_plan)
    return {
        "cloudbox_version": version,
        "suite": suite["suite"],
        "provider": args.provider,
        "model": resolve_model_label(args),
        "eval_kind": args.eval_kind,
        "context_mode": context_mode,
        "contract_repair": args.contract_repair,
        "case_count": len(cases),
        "repeat": args.repeat,
        "request_count": len(cases) * args.repeat,
        "output": str(output),
        "case_ids": [case["id"] for case in cases],
        "ollama": {
            "url": normalize_ollama_url(args.ollama_url),
            "num_ctx": args.num_ctx,
            "temperature": args.temperature,
            "seed": args.seed,
            "thinking": False,
        }
        if args.provider == "ollama"
        else None,
        "openai": {"store": False, "structured_output": True}
        if args.provider == "openai"
        else None,
        "codex": {
            "model": args.codex_model or "codex-default",
            "sandbox": "read-only",
            "ephemeral": True,
            "isolated_git_repository": True,
            "structured_output": True,
        }
        if args.provider == "codex"
        else None,
        "claude": {
            "model": args.claude_model or "claude-default",
            "safe_mode": True,
            "tools_disabled": True,
            "no_session_persistence": True,
            "structured_output": True,
        }
        if args.provider == "claude"
        else None,
        "cases": case_plans,
    }


def main() -> int:
    args = parse_args()
    if args.repeat < 1:
        raise SystemExit("--repeat must be at least 1")
    if args.num_ctx < 1024:
        raise SystemExit("--num-ctx must be at least 1024")

    context_mode = resolve_context_mode(args)
    validate_mode(args, context_mode)

    manifest = load_manifest(MANIFEST)
    suite = load_cases(args.cases)
    schema = load_schema(args.schema)
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    cases = select_cases(suite, args.case_id)
    valid_skills = skill_ids(manifest)
    model_label = resolve_model_label(args)
    output = args.output or default_output(args.provider, model_label, args.eval_kind, context_mode)

    preflight_bundles: dict[str, dict[str, Any]] = {}
    try:
        for case in cases:
            preflight_bundles[case["id"]] = build_routing_bundle(
                args=args,
                manifest=manifest,
                schema=schema,
                case=case,
                context_mode=context_mode,
            )
    except ContextBudgetError as exc:
        print(json.dumps({"error": str(exc), "context": exc.evidence}, ensure_ascii=False, indent=2))
        return 2
    except Exception as exc:
        raise SystemExit(f"Runtime Eval context preflight failed: {exc}") from exc

    try:
        if args.dry_run:
            plan = dry_run_plan(
                args=args,
                manifest=manifest,
                schema=schema,
                suite=suite,
                cases=cases,
                version=version,
                context_mode=context_mode,
                output=output,
            )
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return 0
    except ContextBudgetError as exc:
        print(json.dumps({"error": str(exc), "context": exc.evidence}, ensure_ascii=False, indent=2))
        return 2

    api_key: str | None = None
    if args.provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY is not set; use --provider ollama, codex, or claude for execution without a raw API key")
    elif args.provider == "codex":
        if not args.skip_model_check:
            try:
                codex_preflight(timeout=min(args.timeout, 30.0))
            except Exception as exc:
                raise SystemExit(str(exc)) from exc
    elif args.provider == "claude":
        if not args.skip_model_check:
            try:
                claude_preflight(timeout=min(args.timeout, 30.0))
            except Exception as exc:
                raise SystemExit(str(exc)) from exc
    elif not args.skip_model_check:
        try:
            installed = ollama_installed_models(args.ollama_url, min(args.timeout, 30.0))
        except Exception as exc:
            raise SystemExit(
                f"Cannot connect to Ollama at {normalize_ollama_url(args.ollama_url)}: {exc}\n"
                "Start the Ollama app or run `ollama serve`, then retry."
            ) from exc
        if args.model not in installed:
            available = ", ".join(sorted(installed)) or "none"
            raise SystemExit(
                f"Ollama model {args.model!r} is not installed. Installed models: {available}\n"
                f"Run: ollama pull {args.model}"
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    failures = 0
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for case in cases:
            for attempt in range(1, args.repeat + 1):
                client_request_id = str(uuid.uuid4())
                started = time.perf_counter()
                record: dict[str, Any] = {
                    "schema_version": 3,
                    "run_id": str(uuid.uuid4()),
                    "timestamp_utc": now_utc(),
                    "cloudbox_version": version,
                    "suite": suite["suite"],
                    "case_id": case["id"],
                    "attempt": attempt,
                    "provider": args.provider,
                    "model_requested": resolve_model_label(args),
                    "eval_kind": args.eval_kind,
                    "context_mode": context_mode,
                    "diagnostic_baseline": context_mode in {"none", "manifest"},
                    "client_request_id": client_request_id,
                    "request_id": None,
                    "response_id": None,
                    "model_returned": None,
                    "done_reason": None,
                    "latency_ms": None,
                    "usage": {},
                    "context": None,
                    "initial_actual": None,
                    "actual": None,
                    "raw_output": None,
                    "contract_repair": {
                        "mode": args.contract_repair,
                        "applied": False,
                        "changes": [],
                        "initial_errors": [],
                        "final_errors": [],
                    },
                    "behavior_output": None,
                    "behavior_output_raw": None,
                    "behavior_final_extracted": False,
                    "behavior_status": None,
                    "behavior_usage": {},
                    "error": None,
                }
                try:
                    routing_bundle = preflight_bundles[case["id"]]
                    routing_context = routing_bundle["context"]
                    actual_value, raw_output, metadata = call_model(
                        args=args,
                        api_key=api_key,
                        system_prompt=routing_bundle["system_prompt"],
                        user_prompt=routing_bundle["user_prompt"],
                        schema=schema,
                        max_output_tokens=args.max_output_tokens,
                        client_request_id=client_request_id,
                    )
                    if not isinstance(actual_value, dict):
                        raise RuntimeError("routing model did not return a JSON object")
                    record["initial_actual"] = actual_value
                    initial_errors = validate_decision_shape(actual_value, valid_skills)
                    effective_value = actual_value
                    repair_changes: list[str] = []
                    if args.contract_repair == "deterministic" and initial_errors:
                        effective_value, repair_changes = deterministic_contract_repair(
                            actual_value, valid_skills
                        )
                    final_errors = validate_decision_shape(effective_value, valid_skills)
                    record["contract_repair"] = {
                        "mode": args.contract_repair,
                        "applied": bool(repair_changes),
                        "changes": repair_changes,
                        "initial_errors": initial_errors,
                        "final_errors": final_errors,
                    }
                    record["actual"] = effective_value
                    record["raw_output"] = raw_output
                    record.update(metadata)
                    if args.eval_kind == "routing":
                        record["context"] = routing_context
                    else:
                        if final_errors:
                            raise RuntimeError(
                                "behavior stage refused because routing decision remains invalid after contract repair: "
                                + "; ".join(final_errors)
                            )
                        behavior_bundle = build_selected_skills_prompt(
                            manifest=manifest,
                            case=case,
                            decision=effective_value,
                            num_ctx=args.num_ctx,
                            reserve_output_tokens=max(args.context_reserve_tokens, args.behavior_max_output_tokens),
                            include_declared_references=args.selected_reference_mode == "declared",
                            cases_path=args.cases,
                        )
                        if behavior_bundle is None:
                            record["behavior_status"] = "no-skill"
                            record["context"] = {
                                "mode": "selected-skills",
                                "routing": routing_context,
                                "behavior": {
                                    "mode": "selected-skills",
                                    "loaded_files": [],
                                    "prompt_characters": 0,
                                    "estimated_tokens": 0,
                                    "truncated": False,
                                    "status": "no downstream skill selected; second model call skipped",
                                },
                            }
                        else:
                            behavior_request_id = str(uuid.uuid4())
                            behavior_value, behavior_raw, behavior_metadata = call_model(
                                args=args,
                                api_key=api_key,
                                system_prompt=behavior_bundle["system_prompt"],
                                user_prompt=behavior_bundle["user_prompt"],
                                schema=BEHAVIOR_DELIVERABLE_SCHEMA,
                                max_output_tokens=args.behavior_max_output_tokens,
                                client_request_id=behavior_request_id,
                            )
                            if not isinstance(behavior_value, dict):
                                raise RuntimeError("behavior model did not return a structured object")
                            behavior_final = behavior_value.get("final")
                            if not isinstance(behavior_final, str) or len(behavior_final.strip()) < BEHAVIOR_MIN_FINAL_CHARACTERS:
                                raise RuntimeError("behavior model returned an invalid final deliverable")
                            record["behavior_output_raw"] = behavior_raw
                            record["behavior_output"] = behavior_final.strip()
                            record["behavior_final_extracted"] = True
                            record["behavior_output_contract"] = BEHAVIOR_OUTPUT_CONTRACT_ID
                            record["behavior_output_contract_fingerprint"] = BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT
                            record["behavior_status"] = "completed"
                            record["behavior_usage"] = behavior_metadata.get("usage") or {}
                            record["context"] = {
                                "mode": "selected-skills",
                                "routing": routing_context,
                                "behavior": behavior_bundle["context"],
                            }
                except ContextBudgetError as exc:
                    failures += 1
                    record["context"] = exc.evidence
                    record["error"] = {
                        "type": type(exc).__name__,
                        "message": str(exc),
                    }
                except Exception as exc:  # Keep one failed record per requested attempt.
                    failures += 1
                    record["error"] = {"type": type(exc).__name__, "message": str(exc)}
                record["latency_ms"] = round((time.perf_counter() - started) * 1000)
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                status = "ERROR" if record["error"] else "OK"
                behavior = f' behavior={record["behavior_status"]}' if args.eval_kind == "behavior" else ""
                print(
                    f'{case["id"]} attempt={attempt} provider={args.provider} '
                    f'mode={context_mode} {status}{behavior} latency_ms={record["latency_ms"]}',
                    flush=True,
                )

    print(f"Wrote {len(cases) * args.repeat} records to {output}")
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
