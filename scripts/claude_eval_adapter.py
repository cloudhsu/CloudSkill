from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class ClaudeCLIError(RuntimeError):
    """Raised when the Claude Code CLI cannot complete an Eval request."""


def claude_executable() -> str:
    configured = os.environ.get("CLOUDSKILL_CLAUDE")
    if configured:
        path = Path(configured).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        raise ClaudeCLIError(f"CLOUDSKILL_CLAUDE is not executable: {path}")
    found = shutil.which("claude")
    if not found:
        raise ClaudeCLIError(
            "Claude Code CLI was not found. Install it, run `claude auth login`, then retry."
        )
    return found


def _run_text(command: list[str], *, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ClaudeCLIError(f"failed to execute {' '.join(command)}: {exc}") from exc


def claude_preflight(timeout: float = 30.0) -> dict[str, Any]:
    executable = claude_executable()
    version = _run_text([executable, "--version"], timeout=timeout)
    if version.returncode:
        raise ClaudeCLIError(
            "Claude Code CLI version check failed: "
            + (version.stderr or version.stdout).strip()[:1000]
        )
    status = _run_text([executable, "auth", "status"], timeout=timeout)
    if status.returncode:
        raise ClaudeCLIError(
            "Claude Code CLI is not authenticated. Run `claude auth login`, complete the "
            "sign-in flow, then retry."
        )
    return {
        "executable": executable,
        "version": (version.stdout or version.stderr).strip(),
        "authenticated": True,
        "authentication_detail_recorded": False,
    }


def _extract_result_text(stdout: str) -> tuple[str, dict[str, Any]]:
    """
    Parse `claude -p --output-format json` stdout.

    The documented shape is one JSON object per completed turn with a `result`
    string field plus usage/cost metadata. This parser is defensive: an
    unexpected shape raises ClaudeCLIError instead of silently guessing, so a
    format change surfaces as an infrastructure failure rather than a
    fabricated Behavior/Routing answer. This adapter has not yet been
    exercised against a live `claude` process in this repository; the first
    `./cloudskill-eval-claude` smoke run is the point where this parsing is
    actually confirmed, not assumed.
    """

    stripped = stdout.strip()
    if not stripped:
        raise ClaudeCLIError("Claude Code CLI completed without stdout")
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ClaudeCLIError(
            f"Claude Code CLI --output-format json did not return valid JSON: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise ClaudeCLIError("Claude Code CLI JSON output was not an object")
    if payload.get("is_error"):
        detail = payload.get("result") or payload.get("error") or "unknown error"
        raise ClaudeCLIError(f"Claude Code CLI reported an error result: {detail}")
    result = payload.get("result")
    if not isinstance(result, str) or not result.strip():
        raise ClaudeCLIError(
            "Claude Code CLI JSON output has no non-empty 'result' string field; "
            f"received keys={sorted(payload.keys())}"
        )
    return result.strip(), payload


def call_claude_cli(
    *,
    model: str | None,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any] | None,
    timeout: float,
) -> tuple[str, dict[str, Any]]:
    """
    Execute one isolated, non-interactive Claude Code CLI request.

    Runs from a fresh empty temporary directory with --safe-mode (no CLAUDE.md,
    Skills, plugins, hooks, or MCP auto-loading) and --tools "" (no built-in
    tool access), so the model sees only the supplied Eval prompt, not this
    repository's own CloudBox skills or files. --permission-mode acceptEdits
    avoids the non-interactive session stalling/erroring on a permission
    prompt it cannot answer; the temporary directory has nothing real to
    protect, so an auto-accepted edit there is harmless. Confirmed against a
    real run: without an explicit "do not use tools" framing in the prompt
    itself, the model occasionally attempted a tool call anyway (observed
    stop_reason="tool_use", subtype="error_max_structured_output_retries")
    even with --tools "" already blocking the call -- the wasted retry
    attempts against a disabled tool were what exhausted the structured-output
    retry budget, not the schema itself.
    """

    info = claude_preflight(timeout=min(timeout, 30.0))
    executable = str(info["executable"])

    framed_prompt = (
        "This is a controlled evaluation request. Do not inspect the workspace, "
        "run shell commands, or use any tool. Answer only from the supplied "
        "authoritative context.\n\n" + user_prompt.rstrip() + "\n"
    )

    with tempfile.TemporaryDirectory(prefix="cloudskill-claude-eval-") as temp:
        root = Path(temp)

        command = [
            executable,
            "-p",
            "--output-format",
            "json",
            "--safe-mode",
            "--tools",
            "",
            "--permission-mode",
            "acceptEdits",
            "--no-session-persistence",
            "--strict-mcp-config",
            "--system-prompt",
            system_prompt,
        ]

        normalized_model = (model or "").strip()
        if normalized_model and normalized_model not in {"default", "claude-default"}:
            command.extend(["--model", normalized_model])

        if schema is not None:
            command.extend(["--json-schema", json.dumps(schema, ensure_ascii=False)])

        try:
            process = subprocess.run(
                command,
                input=framed_prompt,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                cwd=str(root),
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ClaudeCLIError(f"Claude Code CLI request timed out after {timeout} seconds") from exc
        except OSError as exc:
            raise ClaudeCLIError(f"failed to start Claude Code CLI: {exc}") from exc

        if process.returncode:
            detail = (process.stderr or process.stdout).strip()
            raise ClaudeCLIError(
                f"Claude Code CLI exited with {process.returncode}: {detail[-3000:]}"
            )

        final_text, payload = _extract_result_text(process.stdout)

        metadata = {
            "model_returned": normalized_model or "claude-default",
            "response_id": payload.get("session_id"),
            "request_id": None,
            "done_reason": "completed",
            "usage": payload.get("usage") or {},
            "claude": {
                "version": info["version"],
                "safe_mode": True,
                "tools_disabled": True,
                "permission_mode": "acceptEdits",
                "no_session_persistence": True,
                "strict_mcp_config": True,
                "num_turns": payload.get("num_turns"),
                "total_cost_usd": payload.get("total_cost_usd"),
                "duration_ms": payload.get("duration_ms"),
            },
        }
        return final_text, metadata
