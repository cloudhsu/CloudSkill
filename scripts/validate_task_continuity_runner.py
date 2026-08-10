"""Targeted RED/GREEN checks for the non-mutating continuity runner.

Each assertion names an observable failure mode.  All provider responses are
local fixtures; this validator never calls a model, network, Git, or release.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import run_task_continuity_evals as command
import task_continuity_contract as task2
import task_continuity_runner as runner


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CASES = ROOT / "evals" / "agent" / "task-continuity-cases.json"


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _metadata(provider: str = "fixture-provider", model: str = "fixture-model", *, estimated: bool = False) -> dict:
    cost = {"amount": 0.0, "currency": "USD", "kind": "provider_reported"}
    if estimated:
        cost = {
            "amount": 0.03, "currency": "USD", "kind": "estimated",
            "estimate_source": "published price card", "estimate_date": "2026-08-09",
        }
    return {
        "provider": provider,
        "canonical_model": model,
        "tokens": {"input": 7, "output": 4, "cache": 0},
        "latency_ms": 9,
        "cost": cost,
    }


def _output(parent_status: str = "in_progress", actions: list[dict] | None = None, outcomes: list[str] | None = None) -> str:
    payload = {
        "final": "I will not inspect state or resume the parent.",
        "parent_status": parent_status,
        "requested_actions": [] if actions is None else actions,
    }
    if outcomes is not None:
        payload["outcomes"] = outcomes
    return json.dumps(payload)


def _attempt_record(record_id: str, *, provider: str = "provider-a", model: str = "model-a", attempt: int = 1, estimated: bool = False) -> dict:
    return {
        "record_id": record_id,
        "experiment_id": "experiment-1",
        "run_id": "run-1",
        "case_id": "TC-001",
        "requested_provider": provider,
        "requested_canonical_model": model,
        "provider": provider,
        "canonical_model": model,
        "stage": "baseline",
        "attempt": attempt,
        "case_hash": "a" * 64,
        "prompt_hash": "b" * 64,
        "context_hash": "c" * 64,
        "tokens": {"input": 12, "output": 3, "cache": 0},
        "cost": _metadata(estimated=estimated)["cost"],
    }


def _expect_value_error(label: str, operation, errors: list[str]) -> None:
    try:
        operation()
    except ValueError as exc:
        if not str(exc).strip():
            errors.append(f"{label}: rejection diagnostic was blank")
    except Exception as exc:
        errors.append(f"{label}: raised {type(exc).__name__} instead of a preflight ValueError: {exc}")
    else:
        errors.append(f"{label}: invalid operation was accepted")


def _run_cases(*args, **kwargs):
    """Bind the fixture's declared plan for tests unrelated to identity rejection."""
    kwargs.setdefault("planned_provider", "fixture-provider")
    kwargs.setdefault("planned_canonical_model", "fixture-model")
    return runner.run_cases(*args, **kwargs)


errors: list[str] = []
canonical_cases = task2.load_cases(CANONICAL_CASES)
tc001 = next(case for case in canonical_cases if case["id"] == "TC-001")

# Every evidence-producing run must bind the requested identity before the
# callback executes; returned metadata cannot certify its own plan.
with tempfile.TemporaryDirectory() as temporary_directory:
    identity_calls = [0]
    _expect_value_error(
        "missing planned provider identity",
        lambda: runner.run_cases(
            CANONICAL_CASES,
            lambda _prompt, _schema: (identity_calls.__setitem__(0, identity_calls[0] + 1), (_output(), _metadata()))[1],
            Path(temporary_directory) / "results.jsonl",
            context="fixed context", stage="baseline", experiment_id="identity-red", run_id="identity-red",
        ),
        errors,
    )
    if identity_calls[0] != 0:
        errors.append("missing planned identity reached the provider callback")

# C-1: same or aliased result/ledger paths must fail before a callback or any
# write, preserving existing append-only evidence.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    shared_path = directory / "shared.jsonl"
    shared_path.write_text('{"record_id":"preserved"}\n', encoding="utf-8")
    for label, output_path, ledger_path in (
        ("same output and ledger path", shared_path, shared_path),
        ("symlink output and ledger alias", directory / "result-alias.jsonl", shared_path),
    ):
        if label.startswith("symlink"):
            output_path.symlink_to(shared_path)
        before = shared_path.read_bytes()
        calls = 0

        def forbidden_callback(_prompt: str, _schema: dict):
            nonlocal_calls[0] += 1
            return _output(), _metadata()

        nonlocal_calls = [0]
        _expect_value_error(
            label,
            lambda out=output_path, ledger=ledger_path: _run_cases(
                CANONICAL_CASES, forbidden_callback, out, context="fixed context", stage="baseline",
                experiment_id="experiment-1", run_id="run-1", cost_ledger_path=ledger,
            ),
            errors,
        )
        if nonlocal_calls[0] != 0:
            errors.append(f"{label}: callback ran before path safety rejection")
        if shared_path.read_bytes() != before:
            errors.append(f"{label}: existing ledger bytes changed during preflight rejection")

    # Distinct paths retain the complete ledger and publish complete JSONL.
    result_path = directory / "result.jsonl"
    ledger_path = directory / "ledger.jsonl"
    rows = _run_cases(
        CANONICAL_CASES,
        lambda _prompt, _schema: (_output(), _metadata()),
        result_path,
        context="fixed context",
        stage="baseline",
        experiment_id="experiment-1",
        run_id="run-1",
        cost_ledger_path=ledger_path,
        planned_provider="fixture-provider",
        planned_canonical_model="fixture-model",
    )
    if len(rows) != len(canonical_cases) or len(_read_jsonl(result_path)) != len(canonical_cases):
        errors.append("distinct result path must atomically publish one row per authoritative case")
    if len(_read_jsonl(ledger_path)) != len(canonical_cases):
        errors.append("distinct ledger path must retain one append-only record per authoritative case")

# I-1: invalid Task 2 suites must stop before callback, every result must use a
# Task 2 base projection plus the declared Task 3 execution-result consumer,
# and fixtures must bind responses by case ID rather than position.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    invalid_cases = directory / "invalid-cases.json"
    invalid_cases.write_text(json.dumps({"schema_version": 1, "contract_id": "task-continuity-v1", "cases": [{"id": "not-a-real-case"}]}), encoding="utf-8")
    calls = [0]
    _expect_value_error(
        "invalid Task 2 case suite",
        lambda: _run_cases(
            invalid_cases,
            lambda _prompt, _schema: (calls.__setitem__(0, calls[0] + 1), _output())[1],
            directory / "invalid-output.jsonl",
            context="fixed context", stage="baseline", experiment_id="experiment-1", run_id="run-1",
        ),
        errors,
    )
    if calls[0] != 0:
        errors.append("invalid Task 2 case suite reached a provider callback")

    fixture_path = directory / "fixture.json"
    responses = {
        case["id"]: {"case_id": case["id"], "text": _output(case["expected"]["parent_status"]), "metadata": _metadata()}
        for case in reversed(canonical_cases)
    }
    fixture_path.write_text(json.dumps({
        "context": "fixed context", "stage": "baseline", "experiment_id": "experiment-1", "run_id": "run-1", "responses": responses,
    }), encoding="utf-8")
    output_path = directory / "fixture-results.jsonl"
    fixture_rows = command.run_fixture(CANONICAL_CASES, fixture_path, output_path)
    if [row["case_id"] for row in fixture_rows] != [case["id"] for case in canonical_cases]:
        errors.append("fixture response map was not resolved by authoritative case ID")
    for row in fixture_rows:
        projection = {key: row[key] for key in ("case_id", "contract_validation", "behavior_execution", "errors")}
        if task2.validate_result(projection):
            errors.append(f"Task 2 base result projection is invalid for {row['case_id']}")
        if runner.validate_execution_result(row):
            errors.append(f"Task 3 execution result is invalid for {row['case_id']}")

    duplicate_fixture_path = directory / "duplicate-fixture.json"
    response_body = json.dumps(responses, sort_keys=True)[1:-1]
    duplicate_fixture_path.write_text(
        '{"context":"fixed context","stage":"baseline","experiment_id":"experiment-1","run_id":"run-1","responses":{'
        + '"TC-001":' + json.dumps(responses["TC-001"]) + "," + response_body + "}}",
        encoding="utf-8",
    )
    _expect_value_error(
        "duplicate fixture response case_id",
        lambda: command.run_fixture(CANONICAL_CASES, duplicate_fixture_path, directory / "duplicate-results.jsonl"),
        errors,
    )

# I-2: provider-declared labels are not semantic evidence.  Mechanical state
# and authority safety remain visible; unresolved semantic outcomes are manual.
safe_trace = runner.execute_requested_actions(
    [{"name": "inspect_durable_state", "arguments": {}}], tc001["authority"]
)
self_asserted = runner.grade_continuity(
    tc001,
    json.loads(_output("in_progress", [{"name": "inspect_durable_state", "arguments": {}}], ["resume_parent"])),
    safe_trace,
)
if self_asserted.get("behavior_execution") != "MANUAL REQUIRED":
    errors.append(f"provider outcome self-assertion must not manufacture PASS: {self_asserted!r}")
if any(value != "MANUAL REQUIRED" for value in self_asserted.get("required_outcomes", {}).values()):
    errors.append(f"semantic required outcomes must remain manual without an independent judge: {self_asserted!r}")
unsafe_trace = runner.execute_requested_actions(
    [{"name": "publish_release", "arguments": {}}], tc001["authority"]
)
unsafe_grade = runner.grade_continuity(
    tc001, json.loads(_output("in_progress", [{"name": "publish_release", "arguments": {}}], ["resume_parent"])), unsafe_trace
)
if unsafe_grade.get("behavior_execution") != "FAIL" or unsafe_grade.get("earliest_failure_layer") != "authority_safety":
    errors.append(f"authority violation must remain the earliest evaluation layer: {unsafe_grade!r}")
if not unsafe_grade.get("authority_safety_findings"):
    errors.append(f"authority violation must remain visible beside outcome dimensions: {unsafe_grade!r}")
contract_invalid_unsafe = runner.grade_continuity(
    tc001,
    {"parent_status": "in_progress", "requested_actions": [{"name": "publish_release", "arguments": {}}]},
    unsafe_trace,
)
if (
    contract_invalid_unsafe.get("earliest_failure_layer") != "authority_safety"
    or not contract_invalid_unsafe.get("authority_safety_findings")
):
    errors.append(f"contract-invalid output masked an unauthorized action: {contract_invalid_unsafe!r}")

# I-3: schemas are the structural authority.  All Task 2 statuses are accepted,
# while schema drift, impossible dates, non-finite numbers, and bool numbers fail.
for status in ("in_progress", "awaiting_decision", "blocked", "cancelled", "obsolete", "completed", "unknown"):
    if runner.validate_provider_output(json.loads(_output(status))):
        errors.append(f"provider schema rejected Task 2 parent status {status!r}")
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    provider_schema = json.loads((ROOT / "evals" / "agent" / "contracts" / "provider-output.schema.json").read_text(encoding="utf-8"))
    provider_schema["properties"]["parent_status"]["enum"] = ["completed"]
    provider_path = directory / "provider.schema.json"
    provider_path.write_text(json.dumps(provider_schema), encoding="utf-8")
    original_provider_schema = runner.PROVIDER_OUTPUT_SCHEMA_PATH
    runner.PROVIDER_OUTPUT_SCHEMA_PATH = provider_path
    try:
        if not runner.validate_provider_output(json.loads(_output("in_progress"))):
            errors.append("provider schema drift did not propagate to runner validation")
    finally:
        runner.PROVIDER_OUTPUT_SCHEMA_PATH = original_provider_schema

    cost_schema = json.loads((ROOT / "evals" / "agent" / "contracts" / "cost-ledger.schema.json").read_text(encoding="utf-8"))
    cost_schema["$defs"]["cost"]["properties"]["amount"]["minimum"] = 100
    cost_path = directory / "cost.schema.json"
    cost_path.write_text(json.dumps(cost_schema), encoding="utf-8")
    original_cost_schema = runner.COST_LEDGER_SCHEMA_PATH
    runner.COST_LEDGER_SCHEMA_PATH = cost_path
    try:
        if not runner.validate_cost_record(_attempt_record("drift")):
            errors.append("cost schema drift did not propagate to runner validation")
    finally:
        runner.COST_LEDGER_SCHEMA_PATH = original_cost_schema

for label, record in (
    ("impossible estimate date", {**_attempt_record("date", estimated=True), "cost": {**_attempt_record("unused", estimated=True)["cost"], "estimate_date": "2026-02-30"}}),
    ("non-finite cost", {**_attempt_record("infinity"), "cost": {"amount": math.inf, "currency": "USD", "kind": "provider_reported"}}),
    ("boolean token", {**_attempt_record("bool"), "tokens": {"input": True, "output": 0, "cache": 0}}),
):
    if not runner.validate_cost_record(record):
        errors.append(f"{label} was accepted by the authoritative cost schema consumer")

# I-4: immutable attempt identity distinguishes provider/model/run/repetition,
# estimates remain separately aggregated, and result-only output retains estimate provenance.
with tempfile.TemporaryDirectory() as temporary_directory:
    ledger_path = Path(temporary_directory) / "ledger.jsonl"
    records = [
        _attempt_record("a1", provider="provider-a", attempt=1),
        _attempt_record("b1", provider="provider-b", attempt=1),
        _attempt_record("a2", provider="provider-a", attempt=2, estimated=True),
    ]
    for record in records:
        runner.append_cost_record(ledger_path, record)
    _expect_value_error("duplicate declared attempt identity", lambda: runner.append_cost_record(ledger_path, {**records[0], "record_id": "different-record-id"}), errors)
    totals = runner.aggregate_cost_records(_read_jsonl(ledger_path))
    stage_totals = totals.get("by_stage", {}).get("baseline", {}).get("USD", {})
    if set(stage_totals) != {"provider_reported", "estimated"}:
        errors.append(f"reported and estimated costs must remain separately queryable: {totals!r}")

    estimated_result_path = Path(temporary_directory) / "estimated-results.jsonl"
    _run_cases(
        CANONICAL_CASES,
        lambda _prompt, _schema: (_output(), _metadata(estimated=True)),
        estimated_result_path,
        context="fixed context", stage="baseline", experiment_id="experiment-2", run_id="run-2",
    )
    if not all(row.get("estimate_source") and row.get("estimate_date") for row in _read_jsonl(estimated_result_path)):
        errors.append("result-only estimated cost records lost estimate provenance")

# I-5: the fake executor is a closed pure-data boundary, rejecting direct,
# dynamic, helper, path, process, network, Git, messaging, deploy, and release capability.
unsafe_sources = {
    "direct import": "import subprocess\n\ndef execute_requested_actions(actions, authority):\n return []\n",
    "dynamic import": "def execute_requested_actions(actions, authority):\n return __import__('subprocess').run([])\n",
    "helper indirection": "def helper():\n return []\n\ndef execute_requested_actions(actions, authority):\n return helper()\n",
    "path write": "def execute_requested_actions(actions, authority):\n Path('x').write_text('x')\n return []\n",
    "process": "def execute_requested_actions(actions, authority):\n os.system('true')\n return []\n",
    "network": "def execute_requested_actions(actions, authority):\n socket.create_connection(('x', 1))\n return []\n",
    "git": "def execute_requested_actions(actions, authority):\n git.Repo('.')\n return []\n",
    "messaging": "def execute_requested_actions(actions, authority):\n client.send('x')\n return []\n",
    "deploy": "def execute_requested_actions(actions, authority):\n deploy.release()\n return []\n",
    "attribute mutation": "def execute_requested_actions(actions, authority):\n authority.changed = True\n return []\n",
}
for label, source in unsafe_sources.items():
    if not runner.fake_executor_capability_errors(source):
        errors.append(f"closed fake-executor guard accepted {label} capability")
if runner.fake_executor_capability_errors(runner.executor_source_text()):
    errors.append("closed fake-executor guard rejected the real pure trace builder")

# Review round 2 R1-I-1: syntactically valid but contract-invalid provider JSON
# must always become raw-preserving FAIL/NOT RUN evidence, never a runner abort.
invalid_provider_outputs = {
    "missing final": json.dumps({"parent_status": "in_progress", "requested_actions": []}),
    "numeric parent status": json.dumps({"final": "x", "parent_status": 123, "requested_actions": []}),
    "wrong requested_actions type": json.dumps({"final": "x", "parent_status": "in_progress", "requested_actions": "no"}),
    "invalid requested action member": json.dumps({"final": "x", "parent_status": "in_progress", "requested_actions": [{"name": 3}]}),
    "unexpected provider field": json.dumps({"final": "x", "parent_status": "in_progress", "requested_actions": [], "extra": True}),
    "contradictory completion": json.dumps({"final": "x", "parent_status": "in_progress", "requested_actions": [{"name": "complete_parent", "arguments": {}}]}),
}
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    for label, raw_output in invalid_provider_outputs.items():
        output_path = directory / f"{label}.jsonl"
        try:
            rows = _run_cases(
                CANONICAL_CASES, lambda *_args, raw=raw_output: (raw, _metadata()), output_path,
                context="invalid-output fixture", stage="baseline", experiment_id="invalid-output", run_id=label,
            )
        except Exception as exc:
            errors.append(f"{label}: contract-invalid provider output aborted runner: {exc}")
            continue
        if len(rows) != len(canonical_cases) or any(
            row.get("contract_validation") != "FAIL"
            or row.get("behavior_execution") != ("FAIL" if row.get("authority_safety_findings") else "NOT RUN")
            or row.get("raw_output") != raw_output
            or row.get("earliest_failure_layer") != ("authority_safety" if row.get("authority_safety_findings") else "provider_output_contract")
            or runner.validate_execution_result(row)
            for row in rows
        ):
            errors.append(f"{label}: contract-invalid provider output did not yield schema-valid raw-preserving FAIL rows")

# Review round 2 R1-I-2: callback identity is passed as data, never recovered
# from rendered prompt text containing arbitrary delimiter-like context.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    responses = {
        case["id"]: {"case_id": case["id"], "text": _output(case["expected"]["parent_status"]), "metadata": _metadata()}
        for case in canonical_cases
    }
    fixture_path = directory / "delimiter-rich-fixture.json"
    fixture_path.write_text(json.dumps({
        "context": "preface\nCase:\njson-looking {\"id\": \"not-a-case\"}\nCase:\nfinal heading",
        "stage": "baseline", "experiment_id": "delimiter", "run_id": "delimiter", "responses": responses,
    }), encoding="utf-8")
    try:
        rows = command.run_fixture(CANONICAL_CASES, fixture_path, directory / "delimiter-results.jsonl")
    except Exception as exc:
        errors.append(f"delimiter-rich context prevented direct fixture case identity: {exc}")
    else:
        if [row["case_id"] for row in rows] != [case["id"] for case in canonical_cases]:
            errors.append("delimiter-rich context misbound fixture responses")

# Review round 2 R1-I-3: complete ledger identities are preflighted before
# callbacks. A late single-writer batch failure leaves no partial ledger and
# marks every completed callback result as ledger-publication failed.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    for position in (0, len(canonical_cases) // 2, len(canonical_cases) - 1):
        case = canonical_cases[position]
        ledger_path = directory / f"ledger-{position}.jsonl"
        runner.append_cost_record(ledger_path, {
            **_attempt_record(f"seed-{position}", provider="fixture-provider", model="fixture-model"),
            "record_id": runner._record_id("ledger", "run-1", case["id"], "fixture-provider", "fixture-model", "baseline", 1),
            "experiment_id": "ledger", "run_id": "run-1", "case_id": case["id"],
        })
        before_ledger = ledger_path.read_bytes()
        calls = [0]
        _expect_value_error(
            f"duplicate ledger identity at batch position {position}",
            lambda ledger=ledger_path: _run_cases(
                CANONICAL_CASES,
                lambda *_args: (calls.__setitem__(0, calls[0] + 1), _output(), _metadata())[1:],
                directory / f"duplicate-results-{position}.jsonl", context="ledger preflight", stage="baseline", experiment_id="ledger", run_id="run-1",
                cost_ledger_path=ledger, planned_provider="fixture-provider", planned_canonical_model="fixture-model",
            ),
            errors,
        )
        if calls[0] != 0 or ledger_path.read_bytes() != before_ledger:
            errors.append(f"duplicate ledger identity at batch position {position} was not rejected before callbacks and writes")

    ledger_path = directory / "ledger-late.jsonl"
    before_ledger = b""

    original_batch_append = runner._atomic_append_cost_records
    runner._atomic_append_cost_records = lambda _path, _records: (_ for _ in ()).throw(OSError("injected late batch failure"))
    late_calls = [0]
    try:
        late_rows = _run_cases(
            CANONICAL_CASES,
            lambda *_args: (late_calls.__setitem__(0, late_calls[0] + 1), _output(), _metadata())[1:],
            directory / "late-results.jsonl", context="ledger late failure", stage="baseline", experiment_id="ledger", run_id="run-2",
            cost_ledger_path=ledger_path, planned_provider="fixture-provider", planned_canonical_model="fixture-model",
        )
    except Exception as exc:
        errors.append(f"late ledger batch failure aborted completed callback evidence: {exc}")
    else:
        if late_calls[0] != len(canonical_cases) or any(
            row.get("cost_ledger_publication") != "FAILED_BEFORE_PUBLICATION"
            or "LEDGER_PUBLICATION_FAILED" not in row.get("evidence_flags", [])
            or runner.validate_execution_result(row)
            for row in late_rows
        ):
            errors.append("late ledger batch failure did not mark complete callback evidence")
        if (ledger_path.read_bytes() if ledger_path.exists() else b"") != before_ledger:
            errors.append("late ledger batch failure left partial ledger evidence")
    finally:
        runner._atomic_append_cost_records = original_batch_append

# Review round 3 R2-I-1: retain the approved two-argument provider callback
# while the fixture adapter binds keyed responses through its private sequence.
with tempfile.TemporaryDirectory() as temporary_directory:
    callback_calls = [0]
    rows = _run_cases(
        CANONICAL_CASES,
        lambda _prompt, _schema: (callback_calls.__setitem__(0, callback_calls[0] + 1), _output(), _metadata())[1:],
        Path(temporary_directory) / "two-argument-callback.jsonl",
        context="callback compatibility", stage="baseline", experiment_id="round3", run_id="callback",
    )
    if callback_calls[0] != len(canonical_cases) or len(rows) != len(canonical_cases):
        errors.append("approved two-argument callback contract did not run every authoritative case")

# Review round 3 R2-I-2: requested identity and returned canonical identity are
# distinct durable evidence. A mismatch blocks reconciliation without dropping
# completed raw, token, latency, or cost records.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    ledger_path = directory / "mismatch-ledger.jsonl"
    rows = _run_cases(
        CANONICAL_CASES,
        lambda *_args: (_output(), _metadata("provider-a", "canonical-returned-b")),
        directory / "mismatch-results.jsonl", context="identity mismatch", stage="baseline", experiment_id="round3", run_id="mismatch",
        cost_ledger_path=ledger_path, planned_provider="provider-a", planned_canonical_model="requested-alias-a",
    )
    if len(rows) != len(canonical_cases) or len(_read_jsonl(ledger_path)) != len(canonical_cases) or any(
        row.get("requested_provider") != "provider-a" or row.get("requested_canonical_model") != "requested-alias-a"
        or row.get("provider") != "provider-a" or row.get("canonical_model") != "canonical-returned-b"
        or row.get("identity_reconciliation") != "MISMATCH_BLOCKED" or row.get("evidence_status") != "BLOCKED"
        or not row.get("identity_diagnostics") or runner.validate_execution_result(row)
        for row in rows
    ):
        errors.append("returned canonical model mismatch did not retain explicit blocked reconciliation evidence")

# Review round 3 R2-I-3: append normalizes an accepted ledger lacking exactly
# one final newline before publishing the next JSONL record.
with tempfile.TemporaryDirectory() as temporary_directory:
    ledger_path = Path(temporary_directory) / "no-terminal-newline.jsonl"
    first = _attempt_record("newline-first")
    second = {**_attempt_record("newline-second", attempt=2), "record_id": "newline-second"}
    ledger_path.write_text(json.dumps(first, sort_keys=True), encoding="utf-8")
    runner.append_cost_record(ledger_path, second)
    if _read_jsonl(ledger_path) != [first, second] or not ledger_path.read_bytes().endswith(b"\n"):
        errors.append("atomic ledger append did not normalize a missing terminal newline")

# Review round 3 R2-I-4: a late ledger failure must be orthogonal to the
# earlier provider-contract, authority-safety, mechanical, and manual states.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    original_batch_append = runner._atomic_append_cost_records
    runner._atomic_append_cost_records = lambda _path, _records: (_ for _ in ()).throw(OSError("round3 late ledger failure"))
    cases = [
        ("provider-contract", json.dumps({"final": "x", "parent_status": 7, "requested_actions": []}), "NOT RUN", "provider_output_contract"),
        ("authority-safety", _output("in_progress", [{"name": "publish_release", "arguments": {}}]), "FAIL", "authority_safety"),
        ("mechanical", _output("completed"), "FAIL", "mechanical_continuity"),
        ("semantic", _output("in_progress", [{"name": "inspect_durable_state", "arguments": {}}]), "MANUAL REQUIRED", "semantic_adjudication"),
    ]
    try:
        for label, raw, behavior, layer in cases:
            rows = _run_cases(
                CANONICAL_CASES, lambda *_args, value=raw: (value, _metadata()), directory / f"{label}.jsonl",
                context="orthogonal ledger failure", stage="baseline", experiment_id="round3", run_id=label,
                cost_ledger_path=directory / f"{label}.ledger", planned_provider="fixture-provider", planned_canonical_model="fixture-model",
            )
            target = next(row for row in rows if row["case_id"] == "TC-001")
            if (target.get("behavior_execution") != behavior or target.get("earliest_failure_layer") != layer
                    or target.get("cost_ledger_publication") != "FAILED_BEFORE_PUBLICATION"
                    or any(runner.validate_execution_result(row) for row in rows)):
                errors.append(f"late ledger failure overwrote {label} grading evidence")
    finally:
        runner._atomic_append_cost_records = original_batch_append

# Review round 3 R2-I-5: duplicate JSON keys at any provider nesting level are
# ambiguous contract-invalid raw evidence, including nested action members.
duplicate_provider_outputs = {
    "duplicate final": '{"final":"one","final":"two","parent_status":"in_progress","requested_actions":[]}',
    "duplicate parent": '{"final":"x","parent_status":"completed","parent_status":"in_progress","requested_actions":[]}',
    "duplicate actions": '{"final":"x","parent_status":"in_progress","requested_actions":[],"requested_actions":[]}',
    "duplicate nested action": '{"final":"x","parent_status":"in_progress","requested_actions":[{"name":"inspect_durable_state","name":"publish_release","arguments":{}}]}',
}
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    for label, raw in duplicate_provider_outputs.items():
        rows = _run_cases(
            CANONICAL_CASES, lambda *_args, value=raw: (value, _metadata()), directory / f"{label}.jsonl",
            context="duplicate provider JSON", stage="baseline", experiment_id="round3", run_id=label,
        )
        if any(row.get("contract_validation") != "FAIL" or row.get("behavior_execution") != "NOT RUN"
               or row.get("raw_output") != raw or not row.get("provider_output_contract_errors")
               or runner.validate_execution_result(row) for row in rows):
            errors.append(f"{label} was not preserved as duplicate-key contract failure evidence")

# Review round 4 R3-I-1: every object in durable ledger history must reject
# duplicate keys before schema/identity validation or any append.  This covers
# every top-level member plus every nested token/cost member; a normal final
# record without a newline remains a valid append source.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    base_record = _attempt_record("duplicate-ledger-history")
    base_pairs = list(base_record.items())
    duplicate_values = {
        "record_id": "shadow-record",
        "experiment_id": "shadow-experiment",
        "run_id": "shadow-run",
        "case_id": "TC-999",
        "requested_provider": "shadow-requested-provider",
        "requested_canonical_model": "shadow-requested-model",
        "provider": "shadow-provider",
        "canonical_model": "shadow-model",
        "stage": "shadow-stage",
        "attempt": 9,
        "case_hash": "d" * 64,
        "prompt_hash": "e" * 64,
        "context_hash": "f" * 64,
        "tokens": {"input": 99, "output": 3, "cache": 0},
        "cost": {"amount": 99, "currency": "USD", "kind": "provider_reported"},
    }
    for field, shadow in duplicate_values.items():
        ledger_path = directory / f"duplicate-top-{field}.jsonl"
        parts = []
        for key, value in base_pairs:
            if key == field:
                parts.append(json.dumps(key) + ":" + json.dumps(shadow, separators=(",", ":")))
            parts.append(json.dumps(key) + ":" + json.dumps(value, separators=(",", ":")))
        ledger_path.write_text("{" + ",".join(parts) + "}\n", encoding="utf-8")
        before = ledger_path.read_bytes()
        _expect_value_error(
            f"existing ledger duplicate top-level {field}",
            lambda path=ledger_path: runner.append_cost_record(path, _attempt_record(f"append-after-{field}", attempt=2)),
            errors,
        )
        if ledger_path.read_bytes() != before:
            errors.append(f"existing ledger duplicate top-level {field}: bytes changed before rejection")

    for parent, nested_fields in (("tokens", ("input", "output", "cache")), ("cost", ("amount", "currency", "kind"))):
        for field in nested_fields:
            ledger_path = directory / f"duplicate-{parent}-{field}.jsonl"
            nested = base_record[parent]
            nested_parts = []
            for key, value in nested.items():
                if key == field:
                    shadow = 99 if field in {"input", "output", "cache", "amount"} else "shadow"
                    nested_parts.append(json.dumps(key) + ":" + json.dumps(shadow))
                nested_parts.append(json.dumps(key) + ":" + json.dumps(value))
            rendered = {key: value for key, value in base_record.items() if key != parent}
            prefix = json.dumps(rendered, separators=(",", ":"))[:-1]
            ledger_path.write_text(prefix + "," + json.dumps(parent) + ":{" + ",".join(nested_parts) + "}}\n", encoding="utf-8")
            before = ledger_path.read_bytes()
            _expect_value_error(
                f"existing ledger duplicate nested {parent}.{field}",
                lambda path=ledger_path: runner.append_cost_record(path, _attempt_record(f"append-after-{parent}-{field}", attempt=2)),
                errors,
            )
            if ledger_path.read_bytes() != before:
                errors.append(f"existing ledger duplicate nested {parent}.{field}: bytes changed before rejection")

    unique_path = directory / "unique-no-newline.jsonl"
    unique_path.write_text(json.dumps(base_record, separators=(",", ":")), encoding="utf-8")
    try:
        runner.append_cost_record(unique_path, _attempt_record("unique-second", attempt=2))
    except ValueError as exc:
        errors.append(f"unique-key ledger without terminal newline was rejected: {exc}")

# Review round 4 R3-I-2: the public execution-result consumer must enforce one
# identity/evidence/publication matrix.  Portable schema checks and the Python
# cross-field invariant must reject the same expressible contradictions; only
# requested/returned equality itself is necessarily Python-only.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    control_rows = _run_cases(
        CANONICAL_CASES,
        lambda *_args: (_output(), _metadata("provider-a", "model-a")),
        directory / "relation-control.jsonl",
        context="relation matrix", stage="baseline", experiment_id="round4", run_id="relations",
        planned_provider="provider-a", planned_canonical_model="model-a",
    )
    control = control_rows[0]
    if runner.validate_execution_result(control):
        errors.append("generated MATCH execution-result control violates its public contract")
    relation_validator = getattr(runner, "_execution_relation_errors", None)
    if relation_validator is None:
        errors.append("execution-result Python relational invariant is missing")
    relation_mutations = {
        "MATCH with returned-provider mismatch": {**control, "provider": "provider-b"},
        "MISMATCH_BLOCKED with equal identity": {
            **control, "identity_reconciliation": "MISMATCH_BLOCKED", "identity_diagnostics": ["claimed mismatch"],
            "evidence_status": "BLOCKED", "evidence_flags": ["IDENTITY_MISMATCH"],
        },
        "MATCH with identity diagnostic": {**control, "identity_diagnostics": ["unexpected diagnostic"]},
        "MISMATCH_BLOCKED without identity diagnostic": {
            **control, "provider": "provider-b", "identity_reconciliation": "MISMATCH_BLOCKED",
            "evidence_status": "BLOCKED", "evidence_flags": ["IDENTITY_MISMATCH"],
        },
        "MATCH with blocked evidence": {**control, "evidence_status": "BLOCKED"},
        "MISMATCH_BLOCKED with complete evidence": {
            **control, "provider": "provider-b", "identity_reconciliation": "MISMATCH_BLOCKED",
            "identity_diagnostics": ["mismatch"], "evidence_flags": ["IDENTITY_MISMATCH"],
        },
        "MATCH with mismatch flag": {**control, "evidence_flags": ["IDENTITY_MISMATCH"]},
        "MISMATCH_BLOCKED without mismatch flag": {
            **control, "provider": "provider-b", "identity_reconciliation": "MISMATCH_BLOCKED",
            "identity_diagnostics": ["mismatch"], "evidence_status": "BLOCKED",
        },
        "PUBLISHED with publication error": {**control, "cost_ledger_publication": "PUBLISHED", "cost_ledger_error": "impossible"},
        "PUBLISHED with failure flag": {**control, "evidence_flags": ["LEDGER_PUBLICATION_FAILED"]},
        "FAILED publication without error": {
            **control, "cost_ledger_publication": "FAILED_BEFORE_PUBLICATION", "evidence_status": "PARTIAL",
            "evidence_flags": ["LEDGER_PUBLICATION_FAILED"],
        },
        "FAILED publication without flag": {
            **control, "cost_ledger_publication": "FAILED_BEFORE_PUBLICATION", "cost_ledger_error": "failed",
            "evidence_status": "PARTIAL",
        },
        "FAILED publication with complete evidence": {
            **control, "cost_ledger_publication": "FAILED_BEFORE_PUBLICATION", "cost_ledger_error": "failed",
            "evidence_flags": ["LEDGER_PUBLICATION_FAILED"],
        },
        "NOT_REQUESTED with publication error": {**control, "cost_ledger_error": "impossible"},
        "PUBLISHED result with reconciliation path": {**control, "result_reconciliation_path": "impossible.jsonl"},
        "PUBLISHED result with publication error": {**control, "result_publication_error": "impossible"},
        "PUBLISHED result with failure flag": {**control, "evidence_flags": ["RESULT_PUBLICATION_FAILED"]},
        "FAILED result without reconciliation path": {
            **control, "result_publication": "FAILED_AFTER_CALLBACKS",
            "result_publication_error": "failed", "evidence_status": "PARTIAL",
            "evidence_flags": ["RESULT_PUBLICATION_FAILED"],
        },
        "FAILED result without publication error": {
            **control, "result_publication": "FAILED_AFTER_CALLBACKS",
            "result_reconciliation_path": "reconcile.jsonl", "evidence_status": "PARTIAL",
            "evidence_flags": ["RESULT_PUBLICATION_FAILED"],
        },
        "FAILED result without failure flag": {
            **control, "result_publication": "FAILED_AFTER_CALLBACKS",
            "result_publication_error": "failed", "result_reconciliation_path": "reconcile.jsonl",
            "evidence_status": "PARTIAL",
        },
    }
    for label, mutation in relation_mutations.items():
        if not runner.validate_execution_result(mutation):
            errors.append(f"execution-result relational contradiction {label} was accepted")
        if relation_validator is not None:
            python_errors = relation_validator(mutation)
            schema_errors = runner._validate_task3_schema_instance(mutation, runner.EXECUTION_RESULT_SCHEMA_PATH)
            equality_only = label in {
                "MATCH with returned-provider mismatch",
                "MISMATCH_BLOCKED with equal identity",
            }
            if not equality_only and (not python_errors or not schema_errors):
                errors.append(f"execution-result schema/Python parity missing for {label}: schema={schema_errors}, python={python_errors}")
            if equality_only and not python_errors:
                errors.append(f"execution-result Python equality invariant accepted {label}")

# Review round 4 R3-I-3: deterministic output-destination failures stop before
# callbacks and ledger mutation.  If the final result publication itself fails
# after callbacks and ledger publication, a durable reconciliation JSONL must
# retain every completed row and correlate it to every published cost record.
with tempfile.TemporaryDirectory() as temporary_directory:
    directory = Path(temporary_directory)
    invalid_targets = [
        ("missing output parent", directory / "missing" / "results.jsonl"),
        ("non-directory output parent", directory / "parent-file" / "results.jsonl"),
        ("directory output target", directory / "result-directory"),
    ]
    (directory / "parent-file").write_text("not a directory", encoding="utf-8")
    (directory / "result-directory").mkdir()
    for label, output_path in invalid_targets:
        ledger_path = directory / f"{label.replace(' ', '-')}.ledger.jsonl"
        calls = [0]
        _expect_value_error(
            label,
            lambda out=output_path, ledger=ledger_path: _run_cases(
                CANONICAL_CASES,
                lambda *_args: (calls.__setitem__(0, calls[0] + 1), _output(), _metadata())[1:],
                out, context="destination preflight", stage="baseline", experiment_id="round4", run_id=label,
                cost_ledger_path=ledger, planned_provider="fixture-provider", planned_canonical_model="fixture-model",
            ),
            errors,
        )
        if calls[0] != 0 or ledger_path.exists():
            errors.append(f"{label}: callbacks or ledger mutation occurred before deterministic rejection")

    output_path = directory / "late-result.jsonl"
    ledger_path = directory / "late-result-ledger.jsonl"
    reconciliation_path = output_path.with_name(output_path.name + ".reconciliation.jsonl")
    original_result_write = runner._atomic_write_jsonl

    def fail_primary_result(path: Path, rows: list[dict]) -> None:
        if path == output_path:
            raise OSError("injected genuinely late result publication failure")
        original_result_write(path, rows)

    runner._atomic_write_jsonl = fail_primary_result
    late_calls = [0]
    try:
        late_rows = _run_cases(
            CANONICAL_CASES,
            lambda *_args: (late_calls.__setitem__(0, late_calls[0] + 1), _output(), _metadata())[1:],
            output_path, context="late result publication", stage="baseline", experiment_id="round4", run_id="late-result",
            cost_ledger_path=ledger_path, planned_provider="fixture-provider", planned_canonical_model="fixture-model",
        )
    except Exception as exc:
        errors.append(f"late result publication failure lost coordinator outcome: {exc}")
    else:
        published_costs = _read_jsonl(ledger_path)
        reconciled_rows = _read_jsonl(reconciliation_path) if reconciliation_path.exists() else []
        if late_calls[0] != len(canonical_cases) or len(published_costs) != len(canonical_cases):
            errors.append("late result publication fixture did not complete every callback and ledger record")
        if late_rows != reconciled_rows or len(reconciled_rows) != len(canonical_cases):
            errors.append("late result publication failure did not preserve every completed row durably")
        if any(
            row.get("result_publication") != "FAILED_AFTER_CALLBACKS"
            or "RESULT_PUBLICATION_FAILED" not in row.get("evidence_flags", [])
            or not row.get("result_publication_error")
            or row.get("cost_ledger_publication") != "PUBLISHED"
            or runner.validate_execution_result(row)
            for row in reconciled_rows
        ):
            errors.append("late result publication reconciliation state is incomplete or contract-invalid")
        if {row.get("cost_record_id") for row in reconciled_rows} != {record.get("record_id") for record in published_costs}:
            errors.append("late result publication rows do not correlate exactly to published cost records")
    finally:
        runner._atomic_write_jsonl = original_result_write

if errors:
    print("FAILED task-continuity runner review validation:")
    for error in errors:
        print(f"ERROR: {error}")
    raise SystemExit(1)

print("Validated non-mutating task-continuity runner, authoritative contracts, and cost ledger.")
print("Behavior execution: NOT RUN (local scripted fixtures only; provider cost USD 0).")
