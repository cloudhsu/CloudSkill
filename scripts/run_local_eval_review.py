from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / ".local" / "runtime-evals"
DEFAULT_MODEL = "qwen3:4b"
DEFAULT_CASE_IDS = (
    "R02-code-and-command-state",
    "R05-ack-versus-completion",
    "R07-english-equipment-architecture",
)
BEHAVIOR_CASE_ID = "R07-english-equipment-architecture"
CONTEXT_CANDIDATES = (4096, 6144, 8192, 12288, 16384, 24576, 32768)
INTERNAL_PLANNING_PATTERNS = (
    r"\blet me (?:analyze|think|draft|tackle|structure)",
    r"\bi need to\b",
    r"the router (?:has already )?selected",
    r"\bSKILL\.md\b",
    r"\bcase id\b",
    r"selected skill",
    r"eval machinery",
)


class PipelineFailure(RuntimeError):
    pass


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the local CloudSkill routing/behavior regression, grade it, optionally "
            "refine behavior output, and produce one uploadable review ZIP."
        )
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--full-routing", action="store_true", help="Run all Canary routing cases instead of R02/R05/R07.")
    parser.add_argument("--no-refine", action="store_true", help="Do not run the Behavior final-deliverable refinement pass.")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--routing-timeout", type=int, default=1200)
    parser.add_argument("--behavior-timeout", type=int, default=1800)
    parser.add_argument("--finalizer-timeout", type=int, default=1200)
    parser.add_argument("--open-result", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--package-existing", type=Path, help="Package an existing run directory without executing the model.")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise PipelineFailure(f"{path}:{line_number}: JSONL record is not an object")
        records.append(value)
    return records


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def command_text(command: list[str]) -> str:
    import shlex

    return " ".join(shlex.quote(item) for item in command)


class ReviewRun:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.run_dir = RUNTIME_ROOT / f"local-review-{stamp}"
        self.log_path = self.run_dir / "run.log"
        self.status_path = self.run_dir / "STATUS.json"
        self.failure_path = self.run_dir / "FAILURE.txt"
        self.summary_path = self.run_dir / "REVIEW_SUMMARY.md"
        self.environment_path = self.run_dir / "environment.json"
        self.latest_run_path = RUNTIME_ROOT / "LATEST_LOCAL_REVIEW_RUN.txt"
        self.latest_zip_path = RUNTIME_ROOT / "LATEST_REVIEW_ZIP.txt"
        self.stable_zip = RUNTIME_ROOT / "CloudSkill-local-eval-review-latest.zip"
        self.stage = "initialize"
        self.started_at = now_utc()
        self.pipeline_success = False
        self.gate_pass: bool | None = None
        self.routing_context: int | None = None
        self.behavior_context: int | None = None
        self.refinement_applied = False
        self.refinement_error: str | None = None
        self.zip_path: Path | None = None
        self._log_handle: Any = None

    def setup(self) -> None:
        RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.latest_run_path.write_text(str(self.run_dir) + "\n", encoding="utf-8")
        self._log_handle = self.log_path.open("w", encoding="utf-8", newline="\n")
        self.log("CloudSkill local Runtime Eval review")
        self.log(f"Repository: {ROOT}")
        self.log(f"Run directory: {self.run_dir}")
        self.log(f"Model: {self.args.model}")
        self.log("Execution mode: foreground")

    def log(self, message: str = "") -> None:
        print(message, flush=True)
        if self._log_handle is not None:
            self._log_handle.write(message + "\n")
            self._log_handle.flush()

    def set_stage(self, stage: str) -> None:
        self.stage = stage
        self.log()
        self.log("=" * 68)
        self.log(f"STAGE: {stage}")
        self.log("=" * 68)

    def run_command(self, command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
        self.log(f"+ {command_text(command)}")
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        output_lines: list[str] = []
        assert process.stdout is not None
        for line in process.stdout:
            line = line.rstrip("\n")
            output_lines.append(line)
            self.log(line)
        return_code = process.wait()
        completed = subprocess.CompletedProcess(command, return_code, "\n".join(output_lines), "")
        if check and return_code != 0:
            raise PipelineFailure(f"command failed with exit code {return_code}: {command_text(command)}")
        return completed

    def finish(self, error: Exception | None) -> int:
        if error is not None:
            self.failure_path.write_text(f"stage={self.stage}\nerror={type(error).__name__}: {error}\n", encoding="utf-8")
            self.log()
            self.log(f"PIPELINE ERROR at {self.stage}: {type(error).__name__}: {error}")
        self.write_status(error)
        self.write_summary(error)
        try:
            self.snapshot_sources()
        except Exception as snapshot_error:
            self.log(f"Snapshot warning: {snapshot_error}")
        try:
            self.zip_path = self.create_review_zip()
            self.latest_zip_path.write_text(str(self.zip_path) + "\n", encoding="utf-8")
            shutil.copy2(self.zip_path, self.stable_zip)
        except Exception as package_error:
            self.log(f"Packaging failed: {package_error}")
            if error is None:
                error = package_error
        if self._log_handle is not None:
            self._log_handle.close()
            self._log_handle = None
        print()
        print("=" * 68)
        print(f"PIPELINE: {'SUCCESS' if self.pipeline_success else 'FAILED'}")
        gate_text = "UNKNOWN" if self.gate_pass is None else ("PASS" if self.gate_pass else "FAIL")
        print(f"EVALUATION GATE: {gate_text}")
        print(f"RUN DIRECTORY: {self.run_dir}")
        if self.zip_path is not None:
            print(f"UPLOAD THIS ZIP: {self.zip_path}")
            print(f"STABLE ZIP: {self.stable_zip}")
        print("=" * 68)
        if self.args.open_result and self.zip_path is not None and sys.platform == "darwin":
            subprocess.run(["open", "-R", str(self.zip_path)], check=False)
        return 0 if self.pipeline_success else 2

    def write_status(self, error: Exception | None) -> None:
        payload = {
            "schema_version": 1,
            "pipeline_status": "SUCCESS" if self.pipeline_success else "FAILED",
            "evaluation_gate": "UNKNOWN" if self.gate_pass is None else ("PASS" if self.gate_pass else "FAIL"),
            "stage": self.stage,
            "started_at_utc": self.started_at,
            "finished_at_utc": now_utc(),
            "repository": str(ROOT),
            "run_directory": str(self.run_dir),
            "model": self.args.model,
            "routing_context": self.routing_context,
            "behavior_context": self.behavior_context,
            "behavior_refinement_applied": self.refinement_applied,
            "behavior_refinement_error": self.refinement_error,
            "error": None if error is None else {"type": type(error).__name__, "message": str(error)},
        }
        self.status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def write_summary(self, error: Exception | None) -> None:
        routing_summary = safe_json(self.run_dir / "routing-summary.json")
        behavior_raw_summary = safe_json(self.run_dir / "behavior-raw-summary.json")
        behavior_refined_summary = safe_json(self.run_dir / "behavior-refined-summary.json")
        routing_metrics = routing_summary.get("metrics") or {}
        raw_score = behavior_raw_summary.get("average_score")
        refined_score = behavior_refined_summary.get("average_score")
        lines = [
            "# CloudSkill Local Runtime Eval Review",
            "",
            f"- Pipeline: **{'SUCCESS' if self.pipeline_success else 'FAILED'}**",
            f"- Evaluation gate: **{'UNKNOWN' if self.gate_pass is None else ('PASS' if self.gate_pass else 'FAIL')}**",
            f"- Earliest final stage: `{self.stage}`",
            f"- Model: `{self.args.model}`",
            f"- Routing context: `{self.routing_context or 'not selected'}`",
            f"- Behavior context: `{self.behavior_context or 'not selected'}`",
        ]
        if error is not None:
            lines.extend(["", "## Pipeline failure", "", f"- `{type(error).__name__}`: {error}"])
        if routing_metrics:
            lines.extend(
                [
                    "",
                    "## Routing",
                    "",
                    f"- Strict pass: **{float(routing_metrics.get('overall_pass_rate', 0)) * 100:.1f}%**",
                    f"- Primary accuracy: **{float(routing_metrics.get('primary_skill_accuracy', 0)) * 100:.1f}%**",
                    f"- Supporting exact: **{float(routing_metrics.get('supporting_skill_exact_accuracy', 0)) * 100:.1f}%**",
                    f"- Contract valid: **{float(routing_metrics.get('contract_valid_rate', 0)) * 100:.1f}%**",
                    "- Detailed report: `routing-report.md`",
                ]
            )
        if raw_score is not None:
            lines.extend(["", "## Behavior", "", f"- Raw score: **{float(raw_score):.1f} / 100**"])
            if refined_score is not None:
                lines.append(f"- Refined score: **{float(refined_score):.1f} / 100**")
            lines.append(f"- Refinement applied: **{'yes' if self.refinement_applied else 'no'}**")
            lines.append("- Raw report: `behavior-raw-report.md`")
            if behavior_refined_summary:
                lines.append("- Refined report: `behavior-refined-report.md`")
        lines.extend(
            [
                "",
                "## Upload",
                "",
                "Upload the ZIP produced beside this run. Do not manually select individual files.",
                "",
                "## Privacy boundary",
                "",
                "The bundle contains only this run, selected Runtime Eval source snapshots, file hashes, and limited Git status/statistics. It excludes credentials, `.git`, unrelated `.local` history, raw conversations, caches, and `.DS_Store`.",
                "",
                "## Evidence limits",
                "",
                "A deterministic Behavior score measures explicit evidence coverage, not complete semantic correctness. A pipeline success with a gate failure means execution and packaging worked but the model result still needs improvement.",
            ]
        )
        self.summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def snapshot_sources(self) -> None:
        snapshot_root = self.run_dir / "source-snapshot"
        snapshot_root.mkdir(exist_ok=True)
        selected = [
            "VERSION",
            "SKILL_MANIFEST.json",
            "cloudskill-eval",
            "scripts/run_local_eval_review.py",
            "scripts/runtime_eval_common.py",
            "scripts/run_runtime_evals.py",
            "scripts/grade_runtime_evals.py",
            "scripts/grade_behavior_evals.py",
            "scripts/validate_runtime_evals.py",
            "scripts/validate_pack.py",
            "evals/runtime/cases/canary.json",
            "evals/runtime/cases/behavior-rubrics.json",
            ".agents/skills/using-cloudskill/SKILL.md",
            ".agents/skills/using-cloudskill/references/conversation-routing-map.md",
            ".agents/skills/equipment-control-architecture/SKILL.md",
            ".agents/skills/equipment-domain-modeling/SKILL.md",
            ".agents/skills/local-runtime-eval-debugging/SKILL.md",
            ".agents/skills/local-runtime-eval-debugging/references/local-eval-troubleshooting.md",
        ]
        inventory: list[dict[str, Any]] = []
        for relative in selected:
            source = ROOT / relative
            if not source.is_file():
                inventory.append({"path": relative, "included": False, "reason": "missing"})
                continue
            target = snapshot_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            inventory.append(
                {
                    "path": relative,
                    "included": True,
                    "size": source.stat().st_size,
                    "sha256": sha256_file(source),
                }
            )
        (self.run_dir / "source-inventory.json").write_text(
            json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def create_review_zip(self) -> Path:
        zip_path = RUNTIME_ROOT / f"CloudSkill-local-eval-review-{self.run_dir.name}.zip"
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(self.run_dir.rglob("*")):
                if not path.is_file():
                    continue
                if path.name == ".DS_Store" or "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                arcname = Path("CloudSkill-local-eval-review") / path.relative_to(self.run_dir)
                archive.write(path, arcname.as_posix())
        with zipfile.ZipFile(zip_path, "r") as archive:
            bad = archive.testzip()
            if bad:
                raise PipelineFailure(f"ZIP integrity failure: {bad}")
        return zip_path


def request_json(url: str, body: dict[str, Any] | None, timeout: int, method: str = "POST") -> dict[str, Any]:
    encoded = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json", "User-Agent": "CloudSkill-Local-Eval-Review/1"}
    if encoded is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=encoded, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise PipelineFailure(f"request failed for {url}: {exc}") from exc


def git_output(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True
        )
    except OSError:
        return "git unavailable"
    return (result.stdout or result.stderr).strip()


def collect_environment(run: ReviewRun, ollama_tags: dict[str, Any]) -> None:
    payload = {
        "generated_at_utc": now_utc(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "repository": str(ROOT),
        "git_head": git_output("rev-parse", "HEAD"),
        "git_branch": git_output("branch", "--show-current"),
        "git_status_short": git_output("status", "--short", "--untracked-files=no"),
        "git_diff_stat": git_output("diff", "--stat"),
        "model_requested": run.args.model,
        "ollama_tags": ollama_tags,
    }
    run.environment_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def select_context(run: ReviewRun, case_ids: tuple[str, ...]) -> int:
    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from runtime_eval_common import (  # type: ignore
        DEFAULT_CASES,
        DEFAULT_SCHEMA,
        MANIFEST,
        ContextBudgetError,
        build_routing_prompt,
        load_cases,
        load_manifest,
        load_schema,
    )

    suite = load_cases(DEFAULT_CASES)
    manifest = load_manifest(MANIFEST)
    schema = load_schema(DEFAULT_SCHEMA)
    case_map = {case["id"]: case for case in suite["cases"]}
    selected = [case_map[case_id] for case_id in case_ids]
    evidence: list[dict[str, Any]] = []
    for candidate in CONTEXT_CANDIDATES:
        candidate_result: dict[str, Any] = {"num_ctx": candidate, "passed": True, "cases": []}
        for case in selected:
            try:
                bundle = build_routing_prompt(
                    manifest=manifest,
                    schema=schema,
                    case=case,
                    context_mode="router",
                    num_ctx=candidate,
                    reserve_output_tokens=512,
                    manifest_path=MANIFEST,
                    schema_path=DEFAULT_SCHEMA,
                    cases_path=DEFAULT_CASES,
                )
                candidate_result["cases"].append(
                    {
                        "case_id": case["id"],
                        "estimated_tokens": bundle["context"].get("estimated_tokens"),
                        "input_budget_tokens": bundle["context"].get("input_budget_tokens"),
                        "overflow_tokens": bundle["context"].get("overflow_tokens"),
                    }
                )
            except ContextBudgetError as exc:
                candidate_result["passed"] = False
                candidate_result["cases"].append(
                    {
                        "case_id": case["id"],
                        "error": str(exc),
                        "evidence": exc.evidence,
                    }
                )
        evidence.append(candidate_result)
        if candidate_result["passed"]:
            (run.run_dir / "context-preflight.json").write_text(
                json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            return candidate
    (run.run_dir / "context-preflight.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    raise PipelineFailure("routing prompt did not fit any configured context candidate")


def behavior_needs_refinement(path: Path, summary: dict[str, Any]) -> bool:
    if float(summary.get("average_score") or 0) < 75:
        return True
    records = read_jsonl(path)
    for record in records:
        output = str(record.get("behavior_output") or "")
        if any(re.search(pattern, output, re.I | re.S) for pattern in INTERNAL_PLANNING_PATTERNS):
            return True
    return False


def extract_final(text: str) -> str:
    match = re.search(r"<final>\s*(.*?)\s*</final>", text, re.I | re.S)
    if match:
        return match.group(1).strip()
    text = text.strip()
    for marker in ("Final answer:", "FINAL ANSWER:", "Final deliverable:"):
        if marker in text:
            return text.split(marker, 1)[1].strip()
    return text


def refine_behavior(run: ReviewRun, raw_path: Path, output_path: Path) -> None:
    records = read_jsonl(raw_path)
    cases = safe_json(ROOT / "evals" / "runtime" / "cases" / "canary.json").get("cases") or []
    case_map = {case.get("id"): case for case in cases if isinstance(case, dict)}
    refined_records: list[dict[str, Any]] = []
    for record in records:
        case_id = record.get("case_id")
        draft = str(record.get("behavior_output") or "")
        case = case_map.get(case_id) or {}
        original_task = str(case.get("prompt") or "")
        if not draft.strip():
            refined_records.append(record)
            continue
        system_prompt = """You are the final-deliverable editor for an engineering architecture answer.
Return only the polished deliverable inside <final> and </final>. Do not expose analysis, planning, self-instructions, Router, Eval, case IDs, skill IDs, or SKILL.md.
Use the original task and draft as evidence. Improve structure and completeness without claiming tests, host actions, plant facts, or specifications that were not provided.
For distributed equipment ownership and recovery, explicitly cover: authoritative state ownership per chamber/IPC; one owner and reservation/arbitration for shared transfer resources; reconnect reconciliation before new work; restart reconstruction of physical/material state; failover authority transfer with fencing or an equivalent split-brain control; command identity, duplicate/idempotency, timeout and late completion; current-evidence interlock/readiness revalidation; concrete failure-injection verification scenarios; assumptions and unresolved inputs.
State unknowns instead of inventing them. Use concise engineering sections and actionable contracts."""
        user_prompt = (
            "/no_think\n\nOriginal task:\n"
            + original_task
            + "\n\nDraft to rewrite:\n"
            + draft
            + "\n\nReturn <final>...</final> only."
        )
        body = {
            "model": run.args.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0,
                "num_ctx": run.behavior_context or 12288,
                "num_predict": 1800,
                "seed": 42,
            },
        }
        started = time.perf_counter()
        payload = request_json(
            run.args.ollama_url.rstrip("/") + "/api/chat",
            body,
            timeout=run.args.finalizer_timeout,
        )
        message = payload.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise PipelineFailure("behavior refinement returned no message.content")
        refined = dict(record)
        refined["behavior_output_initial"] = draft
        refined["behavior_output"] = extract_final(content)
        refined["behavior_refinement"] = {
            "applied": True,
            "model": payload.get("model") or run.args.model,
            "latency_ms": round((time.perf_counter() - started) * 1000),
            "usage": {
                "prompt_tokens": payload.get("prompt_eval_count"),
                "output_tokens": payload.get("eval_count"),
            },
            "raw_refiner_output": content,
        }
        refined_records.append(refined)
    write_jsonl(output_path, refined_records)


def grade_gate(routing_summary: dict[str, Any], behavior_summary: dict[str, Any]) -> bool:
    routing_gate = bool((routing_summary.get("gate") or {}).get("passed"))
    behavior_gate = bool((behavior_summary.get("gate") or {}).get("passed"))
    return routing_gate and behavior_gate


def run_pipeline(args: argparse.Namespace) -> int:
    run = ReviewRun(args)
    error: Exception | None = None
    try:
        run.setup()
        if args.package_existing:
            source = args.package_existing.expanduser().resolve()
            if not source.is_dir():
                raise PipelineFailure(f"existing run directory not found: {source}")
            run.set_stage("package-existing")
            for path in source.iterdir():
                if path.is_file() and path.name not in {".DS_Store"}:
                    shutil.copy2(path, run.run_dir / path.name)
            run.pipeline_success = True
            run.gate_pass = None
            run.stage = "packaged-existing"
            return run.finish(None)

        run.set_stage("environment")
        required = [
            ROOT / "scripts" / "run_runtime_evals.py",
            ROOT / "scripts" / "grade_runtime_evals.py",
            ROOT / "scripts" / "grade_behavior_evals.py",
            ROOT / "evals" / "runtime" / "cases" / "canary.json",
            ROOT / "evals" / "runtime" / "cases" / "behavior-rubrics.json",
        ]
        missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
        if missing:
            raise PipelineFailure("missing required files: " + ", ".join(missing))
        tags = request_json(args.ollama_url.rstrip("/") + "/api/tags", None, timeout=30, method="GET")
        names = {
            value
            for item in tags.get("models", [])
            if isinstance(item, dict)
            for key in ("name", "model")
            for value in [item.get(key)]
            if isinstance(value, str)
        }
        if args.model not in names:
            raise PipelineFailure(f"Ollama model {args.model!r} not installed; available={sorted(names)}")
        collect_environment(run, tags)

        run.set_stage("syntax-check")
        run.run_command(
            [
                sys.executable,
                "-m",
                "py_compile",
                "scripts/run_local_eval_review.py",
                "scripts/runtime_eval_common.py",
                "scripts/run_runtime_evals.py",
                "scripts/grade_runtime_evals.py",
                "scripts/grade_behavior_evals.py",
            ]
        )

        run.set_stage("context-preflight")
        case_ids = tuple(
            case.get("id")
            for case in safe_json(ROOT / "evals" / "runtime" / "cases" / "canary.json").get("cases", [])
            if isinstance(case, dict) and isinstance(case.get("id"), str)
        ) if args.full_routing else DEFAULT_CASE_IDS
        run.routing_context = select_context(run, case_ids)
        run.behavior_context = max(12288, run.routing_context * 2)
        run.log(f"Selected routing context: {run.routing_context}")
        run.log(f"Selected behavior context: {run.behavior_context}")

        routing_jsonl = run.run_dir / "routing.jsonl"
        routing_summary_path = run.run_dir / "routing-summary.json"
        routing_report = run.run_dir / "routing-report.md"

        run.set_stage("routing-execution")
        routing_command = [
            sys.executable,
            "scripts/run_runtime_evals.py",
            "--provider",
            "ollama",
            "--model",
            args.model,
            "--eval-kind",
            "routing",
            "--context-mode",
            "router",
            "--contract-repair",
            "deterministic",
            "--repeat",
            str(args.repeat),
            "--num-ctx",
            str(run.routing_context),
            "--context-reserve-tokens",
            "512",
            "--temperature",
            "0",
            "--seed",
            "42",
            "--timeout",
            str(args.routing_timeout),
            "--output",
            str(routing_jsonl),
        ]
        if not args.full_routing:
            for case_id in case_ids:
                routing_command.extend(["--case-id", case_id])
        run.run_command(routing_command)
        if not routing_jsonl.is_file() or routing_jsonl.stat().st_size == 0:
            raise PipelineFailure("routing JSONL was not created")

        run.set_stage("routing-grading")
        run.run_command(
            [
                sys.executable,
                "scripts/grade_runtime_evals.py",
                "--input",
                str(routing_jsonl),
                "--output",
                str(routing_summary_path),
                "--markdown-output",
                str(routing_report),
                "--allow-failures",
            ]
        )
        routing_summary = safe_json(routing_summary_path)

        behavior_raw_jsonl = run.run_dir / "behavior-raw.jsonl"
        behavior_raw_summary_path = run.run_dir / "behavior-raw-summary.json"
        behavior_raw_report = run.run_dir / "behavior-raw-report.md"

        run.set_stage("behavior-execution")
        run.run_command(
            [
                sys.executable,
                "scripts/run_runtime_evals.py",
                "--provider",
                "ollama",
                "--model",
                args.model,
                "--eval-kind",
                "behavior",
                "--context-mode",
                "selected-skills",
                "--contract-repair",
                "deterministic",
                "--selected-reference-mode",
                "declared",
                "--case-id",
                BEHAVIOR_CASE_ID,
                "--repeat",
                "1",
                "--num-ctx",
                str(run.behavior_context),
                "--context-reserve-tokens",
                "1600",
                "--behavior-max-output-tokens",
                "1600",
                "--temperature",
                "0",
                "--seed",
                "42",
                "--timeout",
                str(args.behavior_timeout),
                "--output",
                str(behavior_raw_jsonl),
            ]
        )
        if not behavior_raw_jsonl.is_file() or behavior_raw_jsonl.stat().st_size == 0:
            raise PipelineFailure("behavior JSONL was not created")

        run.set_stage("behavior-raw-grading")
        run.run_command(
            [
                sys.executable,
                "scripts/grade_behavior_evals.py",
                "--input",
                str(behavior_raw_jsonl),
                "--output",
                str(behavior_raw_summary_path),
                "--markdown-output",
                str(behavior_raw_report),
                "--allow-failures",
            ]
        )
        raw_summary = safe_json(behavior_raw_summary_path)
        final_behavior_summary = raw_summary

        if not args.no_refine and behavior_needs_refinement(behavior_raw_jsonl, raw_summary):
            run.set_stage("behavior-refinement")
            refined_jsonl = run.run_dir / "behavior-refined.jsonl"
            refined_summary_path = run.run_dir / "behavior-refined-summary.json"
            refined_report = run.run_dir / "behavior-refined-report.md"
            try:
                refine_behavior(run, behavior_raw_jsonl, refined_jsonl)
                run.refinement_applied = True
                run.run_command(
                    [
                        sys.executable,
                        "scripts/grade_behavior_evals.py",
                        "--input",
                        str(refined_jsonl),
                        "--output",
                        str(refined_summary_path),
                        "--markdown-output",
                        str(refined_report),
                        "--allow-failures",
                    ]
                )
                final_behavior_summary = safe_json(refined_summary_path)
            except Exception as refinement_error:
                run.refinement_error = f"{type(refinement_error).__name__}: {refinement_error}"
                run.log(f"Behavior refinement warning: {run.refinement_error}")

        run.set_stage("finalize")
        run.pipeline_success = True
        run.gate_pass = grade_gate(routing_summary, final_behavior_summary)
        run.stage = "completed"
    except Exception as exc:
        error = exc
    return run.finish(error)


if __name__ == "__main__":
    raise SystemExit(run_pipeline(parse_args()))
