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

from runtime_eval_common import (
    DEFAULT_CASES,
    DEFAULT_SCHEMA,
    MANIFEST,
    ROOT,
    VERSION_FILE,
    load_cases,
    load_manifest,
    load_schema,
)

OPENAI_API_URL = "https://api.openai.com/v1/responses"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute CloudBox routing Canary Evals with Ollama or the OpenAI Responses API."
    )
    parser.add_argument(
        "--provider",
        choices=("ollama", "openai"),
        default="ollama",
        help="Model runtime. Ollama is local and requires no API key.",
    )
    parser.add_argument(
        "--model",
        default="qwen3:4b",
        help="Ollama model name or exact OpenAI model name. Default: qwen3:4b.",
    )
    parser.add_argument("--repeat", type=int, default=1, help="Attempts per case.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--case-id", action="append", default=[], help="Run only selected case IDs.")
    parser.add_argument("--output", type=Path, help="JSONL output path.")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--max-output-tokens", type=int, default=2000)
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
        help="Validate and print the request plan without calling a model.",
    )
    return parser.parse_args()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_output(provider: str, model: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in model)
    return ROOT / ".local" / "runtime-evals" / f"{stamp}-{provider}-{safe_model}.jsonl"


def build_instructions(manifest: dict[str, Any]) -> str:
    catalog = "\n".join(
        f'- {item["name"]}: {item["description"]}' for item in manifest["skills"]
    )
    return f"""You are the CloudBox routing evaluator. Select the smallest sufficient downstream CloudBox skill set for the user task.

Rules:
- Return one JSON object only. Do not add Markdown fences or explanatory text outside JSON.
- primary_skill owns the requested deliverable or final decision.
- supporting_skills contains only skills that materially change the work.
- execution_order contains every selected skill exactly once and may start with a supporting skill.
- rejected_skills contains plausible alternatives intentionally excluded.
- using-cloudskill is the router and must not be selected downstream unless the task is specifically about router design or routing policy.
- Prompt language is never a routing condition.
- For translation, simple rewriting, trivial calculation, or inspection-only work, return primary_skill=null with empty supporting_skills and execution_order.
- Do not answer the engineering task. Only route it.
- confidence must be high, medium, or low.
- Use only exact skill IDs from this catalog:
{catalog}
"""


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
        request_headers = {"Accept": "application/json", "User-Agent": "CloudBox-Runtime-Eval/5.6.0"}
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


def call_ollama(
    *,
    base_url: str,
    model: str,
    instructions: str,
    prompt: str,
    schema: dict[str, Any],
    timeout: float,
    max_retries: int,
    num_ctx: int,
    temperature: float,
    seed: int,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": schema,
        "think": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "seed": seed,
        },
    }
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
    actual = parse_json_object(text)
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
    instructions: str,
    prompt: str,
    schema: dict[str, Any],
    timeout: float,
    max_retries: int,
    max_output_tokens: int,
    client_request_id: str,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    format_config = {
        "type": "json_schema",
        "name": "cloudbox_routing_decision",
        "description": "Smallest sufficient downstream CloudBox skill routing decision.",
        "strict": True,
        "schema": schema,
    }
    body = {
        "model": model,
        "instructions": instructions,
        "input": prompt,
        "store": False,
        "max_output_tokens": max_output_tokens,
        "text": {"format": format_config},
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
    actual = parse_json_object(text)
    metadata = {
        "model_returned": payload.get("model"),
        "response_id": payload.get("id"),
        "request_id": headers.get("x-request-id"),
        "done_reason": None,
        "usage": payload.get("usage") or {},
    }
    return actual, text, metadata


def main() -> int:
    args = parse_args()
    if args.repeat < 1:
        raise SystemExit("--repeat must be at least 1")
    if args.max_output_tokens < 1:
        raise SystemExit("--max-output-tokens must be positive")
    if args.num_ctx < 1024:
        raise SystemExit("--num-ctx must be at least 1024")

    manifest = load_manifest(MANIFEST)
    suite = load_cases(args.cases)
    schema = load_schema(args.schema)
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    cases = suite["cases"]
    if args.case_id:
        requested = set(args.case_id)
        cases = [case for case in cases if case["id"] in requested]
        missing = sorted(requested - {case["id"] for case in cases})
        if missing:
            raise SystemExit(f"unknown --case-id values: {missing}")
    if not cases:
        raise SystemExit("no cases selected")

    output = args.output or default_output(args.provider, args.model)
    instructions = build_instructions(manifest)

    if args.dry_run:
        plan = {
            "cloudbox_version": version,
            "suite": suite["suite"],
            "provider": args.provider,
            "model": args.model,
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
        }
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    api_key: str | None = None
    if args.provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY is not set; use --provider ollama for local execution")
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
                    "schema_version": 1,
                    "run_id": str(uuid.uuid4()),
                    "timestamp_utc": now_utc(),
                    "cloudbox_version": version,
                    "suite": suite["suite"],
                    "case_id": case["id"],
                    "attempt": attempt,
                    "provider": args.provider,
                    "model_requested": args.model,
                    "client_request_id": client_request_id,
                    "request_id": None,
                    "response_id": None,
                    "model_returned": None,
                    "done_reason": None,
                    "latency_ms": None,
                    "usage": {},
                    "actual": None,
                    "raw_output": None,
                    "error": None,
                }
                try:
                    if args.provider == "ollama":
                        actual, raw_output, metadata = call_ollama(
                            base_url=args.ollama_url,
                            model=args.model,
                            instructions=instructions,
                            prompt=case["prompt"],
                            schema=schema,
                            timeout=args.timeout,
                            max_retries=args.max_retries,
                            num_ctx=args.num_ctx,
                            temperature=args.temperature,
                            seed=args.seed,
                        )
                    else:
                        assert api_key is not None
                        actual, raw_output, metadata = call_openai(
                            api_key=api_key,
                            model=args.model,
                            instructions=instructions,
                            prompt=case["prompt"],
                            schema=schema,
                            timeout=args.timeout,
                            max_retries=args.max_retries,
                            max_output_tokens=args.max_output_tokens,
                            client_request_id=client_request_id,
                        )
                    record["actual"] = actual
                    record["raw_output"] = raw_output
                    record.update(metadata)
                except Exception as exc:  # Keep one failed record per requested attempt.
                    failures += 1
                    record["error"] = {"type": type(exc).__name__, "message": str(exc)}
                record["latency_ms"] = round((time.perf_counter() - started) * 1000)
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                status = "ERROR" if record["error"] else "OK"
                print(
                    f'{case["id"]} attempt={attempt} provider={args.provider} '
                    f'{status} latency_ms={record["latency_ms"]}',
                    flush=True,
                )

    print(f"Wrote {len(cases) * args.repeat} records to {output}")
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
