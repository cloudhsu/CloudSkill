from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class CodexCLIError(RuntimeError):
    """Raised when the Codex CLI cannot complete an Eval request."""


def codex_executable() -> str:
    configured = os.environ.get("CLOUDSKILL_CODEX")
    if configured:
        path = Path(configured).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        raise CodexCLIError(f"CLOUDSKILL_CODEX is not executable: {path}")
    found = shutil.which("codex")
    if not found:
        raise CodexCLIError(
            "Codex CLI was not found. Install it, run `codex login`, then retry."
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
        raise CodexCLIError(f"failed to execute {' '.join(command)}: {exc}") from exc


def codex_preflight(timeout: float = 30.0) -> dict[str, Any]:
    executable = codex_executable()
    version = _run_text([executable, "--version"], timeout=timeout)
    if version.returncode:
        raise CodexCLIError(
            "Codex CLI version check failed: "
            + (version.stderr or version.stdout).strip()[:1000]
        )
    login = _run_text([executable, "login", "status"], timeout=timeout)
    if login.returncode:
        raise CodexCLIError(
            "Codex CLI is not authenticated. Run `codex login`, complete the browser "
            "flow, then retry."
        )
    return {
        "executable": executable,
        "version": (version.stdout or version.stderr).strip(),
        "authenticated": True,
        "authentication_detail_recorded": False,
    }


def _parse_jsonl_events(text: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {
        "thread_id": None,
        "usage": {},
        "event_count": 0,
    }
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        events.append(event)
        event_type = event.get("type")
        if event_type == "thread.started":
            metadata["thread_id"] = event.get("thread_id")
        elif event_type == "turn.completed":
            usage = event.get("usage")
            if isinstance(usage, dict):
                metadata["usage"] = usage
    metadata["event_count"] = len(events)
    return events, metadata


def _last_agent_message(events: list[dict[str, Any]]) -> str | None:
    for event in reversed(events):
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "agent_message":
            continue
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    return None


def call_codex_cli(
    *,
    model: str | None,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any] | None,
    timeout: float,
) -> tuple[str, dict[str, Any]]:
    """
    Execute one isolated, non-interactive Codex request.

    The temporary working directory is an empty Git repository so the model sees
    only the supplied Eval prompt, not extra CloudSkill repository files.
    """
    info = codex_preflight(timeout=min(timeout, 30.0))
    executable = str(info["executable"])
    prompt = (
        "This is a controlled evaluation request. Do not inspect the workspace, "
        "run shell commands, or use external tools. Answer only from the supplied "
        "authoritative context.\n\n"
        "<system-context>\n"
        + system_prompt.rstrip()
        + "\n</system-context>\n\n"
        "<user-request>\n"
        + user_prompt.rstrip()
        + "\n</user-request>\n"
    )

    with tempfile.TemporaryDirectory(prefix="cloudskill-codex-eval-") as temp:
        root = Path(temp)
        init = _run_text(["git", "init", "-q", str(root)], timeout=30.0)
        if init.returncode:
            raise CodexCLIError(
                "failed to create isolated Git repository for Codex Eval: "
                + (init.stderr or init.stdout).strip()[:1000]
            )

        output_path = root / "final-message.txt"
        command = [
            executable,
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--cd",
            str(root),
            "--ignore-user-config",
            "--ignore-rules",
            "--json",
            "--output-last-message",
            str(output_path),
        ]

        normalized_model = (model or "").strip()
        if normalized_model and normalized_model not in {"default", "codex-default"}:
            command.extend(["--model", normalized_model])

        if schema is not None:
            schema_path = root / "output-schema.json"
            schema_path.write_text(
                json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            command.extend(["--output-schema", str(schema_path)])

        command.append("-")

        try:
            process = subprocess.run(
                command,
                input=prompt,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise CodexCLIError(f"Codex request timed out after {timeout} seconds") from exc
        except OSError as exc:
            raise CodexCLIError(f"failed to start Codex CLI: {exc}") from exc

        events, event_meta = _parse_jsonl_events(process.stdout)
        if process.returncode:
            detail = (process.stderr or process.stdout).strip()
            raise CodexCLIError(
                f"Codex CLI exited with {process.returncode}: {detail[-3000:]}"
            )

        if output_path.is_file():
            final_text = output_path.read_text(encoding="utf-8").strip()
        else:
            final_text = _last_agent_message(events) or ""
        if not final_text:
            raise CodexCLIError("Codex CLI completed without a final message")

        metadata = {
            "model_returned": normalized_model or "codex-default",
            "response_id": event_meta.get("thread_id"),
            "request_id": None,
            "done_reason": "completed",
            "usage": event_meta.get("usage") or {},
            "codex": {
                "version": info["version"],
                "event_count": event_meta.get("event_count", 0),
                "sandbox": "read-only",
                "ephemeral": True,
                "isolated_git_repository": True,
                "user_config_ignored": True,
                "rules_ignored": True,
            },
        }
        return final_text, metadata
