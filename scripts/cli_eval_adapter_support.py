"""Shared subprocess/identity helpers for CLI-based model Eval adapters.

Extracted from `claude_eval_adapter.py` and `codex_eval_adapter.py`, which
share a safety/isolation contract (ephemeral temp dir, explicit "do not use
tools" prompt framing, preflight before execution, provider-returned-vs-
selected model identity separation) closely enough that their infrastructure
functions were byte-identical or near-identical -- see
`docs/plans/2026-08-17-validate-scripts-internal-audit.md` Milestone 9,
cluster 2. Each adapter keeps its own CLI-specific command building, output
parsing, and error type; only the two genuinely shared primitives move here.
"""

from __future__ import annotations

import subprocess
from typing import Any


def run_cli_text_command(
    command: list[str], *, timeout: float, error_class: type[Exception]
) -> subprocess.CompletedProcess[str]:
    """Run one short-lived text-mode command -- a `--version`/auth-status
    preflight check, or a one-off setup command like `git init` for an
    isolated sandbox. Raises `error_class` -- the caller's own CLI-specific
    error type -- on a failure to execute at all; a nonzero exit code is
    left for the caller to interpret, matching each adapter's own logic."""
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
        raise error_class(f"failed to execute {' '.join(command)}: {exc}") from exc


def model_identity_metadata(
    selected_model: str | None,
    provider_returned_model: str | None,
    *,
    default_label: str,
    aliases: set[str],
) -> dict[str, Any]:
    """Separate CLI selection from provider-returned identity without alias
    guessing. `default_label` and `aliases` are the one thing that actually
    differed between the two original copies (e.g. `"claude-default"` with
    `{"default", "claude-default", "sonnet", "opus"}` vs. `"codex-default"`
    with `{"default", "codex-default"}`)."""
    selected = (selected_model or "").strip() or default_label
    returned = (provider_returned_model or "").strip() or None
    if returned is not None:
        canonical = returned
        evidence = "provider_returned"
    elif selected not in aliases:
        canonical = selected
        evidence = "explicit_selection"
    else:
        canonical = None
        evidence = None
    return {
        "selected_model": selected,
        "provider_returned_model": returned,
        "canonical_model": canonical,
        "model_identity_evidence": evidence,
    }
