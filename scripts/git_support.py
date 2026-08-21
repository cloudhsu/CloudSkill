"""Shared low-level `git` subprocess wrapper.

Extracted from `sync_eval_exchange.py::run_git` and
`run_local_eval_review.py::git_output` -- two independent wrappers with
the same spirit (run one `git` subprocess call, do not leak connectivity or
path detail into whatever surfaces the failure) but three different exact
failure behaviors -- see `docs/plans/2026-08-17-validate-scripts-internal-audit.md`
Milestone 9, cluster 3.

This module intentionally never raises and never decides how a caller should
react to failure: callers had genuinely different needs (hard failure via a
raised exception, vs. best-effort diagnostic text that must never crash the
caller) and preserving each is the point of extracting only the actual
duplicated part -- the subprocess invocation and exception containment -- not
each caller's own error-handling policy.

One disclosed, deliberate behavior change from the original three copies:
this module always decodes subprocess output with `encoding="utf-8",
errors="replace"` (one of the three original callers already did this; the
other two used bare `text=True`, which raises `UnicodeDecodeError` on
non-UTF-8 bytes instead of substituting a replacement character). This is a
strict safety upgrade for those two callers, not a functional change for
well-formed git output, which is UTF-8 in every case actually exercised by
this repo's callers.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NamedTuple


class GitResult(NamedTuple):
    ok: bool
    stdout: str
    stderr: str
    returncode: int | None  # None only when git itself could not be started/timed out


def run_git_command(
    args: list[str], *, cwd: Path | None = None, timeout: float | None = None
) -> GitResult:
    """Run one `git` subprocess call. Never raises for a nonzero exit, a
    missing `git` executable, or a timeout -- callers decide whether and how
    to fail. Returns raw, unstripped stdout/stderr so a caller that needs
    exact original formatting is unaffected."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return GitResult(ok=False, stdout="", stderr="", returncode=None)
    return GitResult(
        ok=result.returncode == 0,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
    )
