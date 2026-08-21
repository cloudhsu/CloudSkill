"""Shared file-hashing helper.

Extracted from `grade_behavior_evals.py` and `run_local_eval_review.py`,
which each independently defined a byte-identical chunked SHA-256 helper
-- see `docs/plans/2026-08-17-validate-scripts-internal-audit.md`
Milestone 9, cluster 4.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
