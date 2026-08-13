from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime_eval_common import (
    DEFAULT_CASES,
    DEFAULT_SCHEMA,
    MANIFEST,
    ROOT,
    ROUTER_SKILL,
    ROUTER_SKILL_PATH,
    ROUTING_MAP_PATH,
    VERSION_FILE,
    assert_router_context,
    build_routing_prompt,
    build_selected_skills_prompt,
    discover_declared_references,
    grade_decision,
    load_cases,
    load_manifest,
    load_schema,
    skill_ids,
    validate_decision_shape,
)
from run_runtime_evals import deterministic_contract_repair


errors: list[str] = []
ROUTING_VALIDATION_NUM_CTX = 8192
BEHAVIOR_VALIDATION_NUM_CTX = 16384

for path in (
    DEFAULT_CASES,
    DEFAULT_SCHEMA,
    ROOT / "scripts" / "runtime_eval_common.py",
    ROOT / "scripts" / "run_runtime_evals.py",
    ROOT / "scripts" / "grade_runtime_evals.py",
    ROOT / ".github" / "workflows" / "runtime-eval.yml",
    ROOT / "evals" / "runtime" / "README.md",
    ROUTER_SKILL_PATH,
    ROUTING_MAP_PATH,
):
    if not path.exists():
        errors.append(f"missing runtime Eval file: {path.relative_to(ROOT)}")

try:
    manifest = load_manifest(MANIFEST)
    suite = load_cases(DEFAULT_CASES)
    schema = load_schema(DEFAULT_SCHEMA)
except (OSError, json.JSONDecodeError, KeyError) as exc:
    print(f"ERROR: failed to load runtime Eval metadata: {exc}")
    raise SystemExit(1)

version = VERSION_FILE.read_text(encoding="utf-8").strip()
if manifest.get("version") != version:
    errors.append("SKILL_MANIFEST version differs from VERSION")

valid_skills = skill_ids(manifest)
if len(valid_skills) != len(manifest.get("skills", [])):
    errors.append("SKILL_MANIFEST contains duplicate skill IDs")
required_runtime_skills = {ROUTER_SKILL, "local-runtime-eval-debugging"}
missing_runtime_skills = sorted(required_runtime_skills - valid_skills)
if missing_runtime_skills:
    errors.append(f"Runtime Eval routing catalog is missing required skill IDs: {missing_runtime_skills}")

required_schema_fields = {
    "primary_skill",
    "supporting_skills",
    "rejected_skills",
    "execution_order",
    "reason",
    "confidence",
}
if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
    errors.append("routing decision schema must be a closed object")
if set(schema.get("required", [])) != required_schema_fields:
    errors.append("routing decision schema required fields differ from contract")
if set(schema.get("properties", {})) != required_schema_fields:
    errors.append("routing decision schema properties differ from contract")

cases = suite.get("cases")
if not isinstance(cases, list):
    errors.append("runtime suite cases must be an array")
    cases = []
if len(cases) < 10:
    errors.append(f"Canary Suite must contain at least 10 cases, found {len(cases)}")

ids: set[str] = set()
for case in cases:
    cid = case.get("id")
    if not isinstance(cid, str) or not cid:
        errors.append("runtime case has an empty ID")
        continue
    if cid in ids:
        errors.append(f"duplicate runtime case ID: {cid}")
    ids.add(cid)
    if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
        errors.append(f"{cid}: prompt is empty")
    if "behavior_prompt" in case and (
        not isinstance(case.get("behavior_prompt"), str)
        or not case["behavior_prompt"].strip()
    ):
        errors.append(f"{cid}: behavior_prompt must be a non-empty string when present")
    expected = case.get("expected")
    if not isinstance(expected, dict):
        errors.append(f"{cid}: expected must be an object")
        continue
    required_expected = {
        "primary_skill",
        "required_supporting_skills",
        "forbidden_selected_skills",
        "execution_order",
        "allow_additional_supporting_skills",
    }
    optional_expected = {"allowed_execution_orders"}
    if not required_expected.issubset(expected) or set(expected) - required_expected - optional_expected:
        errors.append(f"{cid}: expected fields differ from contract")
        continue
    all_expected_ids = []
    primary = expected["primary_skill"]
    if primary is not None:
        all_expected_ids.append(primary)
    for name in ("required_supporting_skills", "forbidden_selected_skills", "execution_order"):
        value = expected[name]
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"{cid}: {name} must be an array of strings")
            continue
        if len(value) != len(set(value)):
            errors.append(f"{cid}: {name} contains duplicates")
        all_expected_ids.extend(value)
    allowed_orders = expected.get("allowed_execution_orders", [expected["execution_order"]])
    if not isinstance(allowed_orders, list) or not allowed_orders:
        errors.append(f"{cid}: allowed_execution_orders must be a non-empty array when present")
        allowed_orders = []
    for index, candidate in enumerate(allowed_orders):
        if not isinstance(candidate, list) or any(not isinstance(item, str) for item in candidate):
            errors.append(f"{cid}: allowed_execution_orders[{index}] must be an array of strings")
            continue
        if len(candidate) != len(set(candidate)):
            errors.append(f"{cid}: allowed_execution_orders[{index}] contains duplicates")
        all_expected_ids.extend(candidate)

    unknown = sorted({item for item in all_expected_ids if item not in valid_skills})
    if unknown:
        errors.append(f"{cid}: unknown expected skill IDs: {unknown}")
    if primary == ROUTER_SKILL or ROUTER_SKILL in expected["required_supporting_skills"]:
        errors.append(f"{cid}: router must not be selected downstream")
    selected = ([primary] if primary else []) + expected["required_supporting_skills"]
    if set(expected["execution_order"]) != set(selected):
        errors.append(f"{cid}: execution_order must contain expected selected skills exactly once")
    for index, candidate in enumerate(allowed_orders):
        if set(candidate) != set(selected):
            errors.append(
                f"{cid}: allowed_execution_orders[{index}] must contain expected selected skills exactly once"
            )
    if primary is None and (expected["required_supporting_skills"] or expected["execution_order"]):
        errors.append(f"{cid}: no-skill case must not select supporting skills")

required_canary_ids = {
    "R01-networkstream-stale-response",
    "R02-code-and-command-state",
    "R03-versioned-multi-audience-report",
    "R04-greenfield-internal-web",
    "R05A-component-state-contract",
    "R05B-recovery-ownership",
    "R05C-component-and-recovery-composition",
    "R06-chinese-translation-no-skill",
    "R07-english-equipment-architecture",
    "R08-historical-interaction-optimization",
}
missing_canary_ids = sorted(required_canary_ids - ids)
if missing_canary_ids:
    errors.append(f"Canary Suite is missing required case IDs: {missing_canary_ids}")

# Prove deterministic grading with one synthetic pass and one intentional failure.
if cases:
    first = cases[0]
    expected = first["expected"]
    passing = {
        "primary_skill": expected["primary_skill"],
        "supporting_skills": expected["required_supporting_skills"],
        "rejected_skills": expected["forbidden_selected_skills"],
        "execution_order": expected["execution_order"],
        "reason": "Synthetic validator fixture.",
        "confidence": "high",
    }
    shape_errors = validate_decision_shape(passing, valid_skills)
    if shape_errors:
        errors.append(f"synthetic passing decision failed shape validation: {shape_errors}")
    grade = grade_decision(first, passing, valid_skills)
    if not grade["passed"]:
        errors.append(f"synthetic passing decision failed grader: {grade}")
    failing = dict(passing)
    failing["primary_skill"] = None
    failing["supporting_skills"] = []
    failing["execution_order"] = []
    if grade_decision(first, failing, valid_skills)["passed"]:
        errors.append("synthetic failing decision unexpectedly passed grader")
    contract_invalid = dict(passing)
    contract_invalid["execution_order"] = []
    invalid_grade = grade_decision(first, contract_invalid, valid_skills)
    if invalid_grade["checks"].get("valid_output"):
        errors.append("contract-invalid fixture unexpectedly passed contract validation")
    if not invalid_grade["checks"].get("primary_skill"):
        errors.append("independent grading lost a correct primary skill because order was invalid")
    if not invalid_grade["checks"].get("router_not_downstream"):
        errors.append("independent grading falsely reported router self-inclusion")
    repaired, changes = deterministic_contract_repair(contract_invalid, valid_skills)
    if not changes:
        errors.append("deterministic contract repair made no change to invalid execution_order")
    if validate_decision_shape(repaired, valid_skills):
        errors.append("deterministic contract repair did not produce a valid routing decision")

# Rebuild the actual prompts for the four acceptance cases in all diagnostic modes.
acceptance_ids = {
    "R01-networkstream-stale-response",
    "R02-code-and-command-state",
    "R03-versioned-multi-audience-report",
    "R05A-component-state-contract",
    "R05B-recovery-ownership",
    "R05C-component-and-recovery-composition",
    "R06-chinese-translation-no-skill",
    "R07-english-equipment-architecture",
}
case_map = {case["id"]: case for case in cases}
for cid in sorted(acceptance_ids):
    case = case_map.get(cid)
    if case is None:
        errors.append(f"missing acceptance case: {cid}")
        continue
    bundles = {}
    for mode in ("none", "manifest", "router"):
        try:
            bundles[mode] = build_routing_prompt(
                manifest=manifest,
                schema=schema,
                case=case,
                context_mode=mode,
                num_ctx=ROUTING_VALIDATION_NUM_CTX,
                reserve_output_tokens=320,
                manifest_path=MANIFEST,
                schema_path=DEFAULT_SCHEMA,
                cases_path=DEFAULT_CASES,
            )
        except Exception as exc:
            errors.append(f"{cid}: failed to build {mode} prompt at adaptive-safe routing context: {exc}")
            continue
        context = bundles[mode]["context"]
        if context["truncated"]:
            errors.append(f"{cid}: {mode} prompt unexpectedly truncated")
        if context["overflow_tokens"]:
            errors.append(f"{cid}: {mode} prompt exceeds the routing validation input budget")
        if case["prompt"] not in bundles[mode]["user_prompt"]:
            errors.append(f"{cid}: {mode} prompt omitted the current case")
        for skill_id in valid_skills:
            if skill_id not in bundles[mode]["system_prompt"]:
                errors.append(f"{cid}: {mode} prompt omitted skill ID {skill_id}")
                break
        if "using-cloudbox-skills is the router" not in bundles[mode]["system_prompt"]:
            errors.append(f"{cid}: {mode} prompt omitted router exclusion rule")
    if "router" in bundles:
        try:
            assert_router_context(bundles["router"])
        except Exception as exc:
            errors.append(f"{cid}: router context assertion failed: {exc}")
        router_paths = {
            item["path"] for item in bundles["router"]["context"]["loaded_files"] if item["included"]
        }
        for required in (
            ROUTER_SKILL_PATH.relative_to(ROOT).as_posix(),
            ROUTING_MAP_PATH.relative_to(ROOT).as_posix(),
        ):
            if required not in router_paths:
                errors.append(f"{cid}: router prompt did not load {required}")
    if "none" in bundles and "# Using CloudBox" in bundles["none"]["system_prompt"]:
        errors.append(f"{cid}: none baseline unexpectedly contains router SKILL.md")
    if "manifest" in bundles and "# Using CloudBox" in bundles["manifest"]["system_prompt"]:
        errors.append(f"{cid}: manifest baseline unexpectedly contains router SKILL.md")
    if "router" in bundles and "# Using CloudBox" not in bundles["router"]["system_prompt"]:
        errors.append(f"{cid}: router mode omitted full using-cloudbox-skills/SKILL.md")
    if cid == "R02-code-and-command-state" and "router" in bundles:
        prompt = bundles["router"]["system_prompt"]
        for marker in (
            "code-review",
            "equipment-domain-modeling",
            "Do not substitute `equipment-control-architecture`",
        ):
            if marker not in prompt:
                errors.append(f"R02 router excerpt omitted required routing evidence: {marker}")
    if cid == "R03-versioned-multi-audience-report" and "router" in bundles:
        prompt = bundles["router"]["system_prompt"]
        for marker in (
            "CEO/management versus engineer/training reports",
            "update success rates must correlate to an actual software version",
            "Owner versus execution order",
            '"software-quality-iso25010"',
        ):
            if marker not in prompt:
                errors.append(f"R03 router excerpt omitted required routing evidence: {marker}")

# Prove selected-skills mode loads the actual downstream SKILL.md and does not load the router downstream.
engine_skill_path = ROOT / ".agents/skills/cross-platform-engine-architecture/SKILL.md"
engine_references = discover_declared_references(engine_skill_path, engine_skill_path.read_text(encoding="utf-8"))
shared_elicitation = ROOT / ".agents/skills/architecture-review/references/architecture-decision-elicitation.md"
if shared_elicitation.resolve() not in engine_references:
    errors.append("cross-skill architecture elicitation reference was not discovered")

r07 = case_map.get("R07-english-equipment-architecture")
if r07:
    decision = {
        "primary_skill": "equipment-control-architecture",
        "supporting_skills": [],
        "rejected_skills": ["application-client-server-architecture"],
        "execution_order": ["equipment-control-architecture"],
        "reason": "Distributed equipment ownership and recovery boundary.",
        "confidence": "high",
    }
    try:
        behavior = build_selected_skills_prompt(
            manifest=manifest,
            case=r07,
            decision=decision,
            num_ctx=BEHAVIOR_VALIDATION_NUM_CTX,
            reserve_output_tokens=320,
            include_declared_references=True,
            cases_path=DEFAULT_CASES,
        )
        if behavior is None:
            errors.append("selected-skills behavior prompt unexpectedly returned no-skill")
        else:
            loaded_paths = {
                item["path"]
                for item in behavior["context"]["loaded_files"]
                if item["included"]
            }
            expected_path = ".agents/skills/equipment-control-architecture/SKILL.md"
            if expected_path not in loaded_paths:
                errors.append(f"selected-skills prompt did not load {expected_path}")
            if ROUTER_SKILL_PATH.relative_to(ROOT).as_posix() in loaded_paths:
                errors.append("selected-skills prompt loaded using-cloudbox-skills downstream")
            if behavior["context"]["overflow_tokens"]:
                errors.append("selected-skills prompt exceeds the behavior validation context with declared references")
            if "Return exactly one JSON object" not in behavior["system_prompt"]:
                errors.append("selected-skills prompt omitted the structured final-deliverable contract")
            if str(r07.get("behavior_prompt") or "") not in behavior["user_prompt"]:
                errors.append("selected-skills prompt did not use the case behavior_prompt")
            if "Select the smallest sufficient CloudBox skill set" in behavior["user_prompt"]:
                errors.append("selected-skills prompt leaked the routing-only instruction into Behavior Eval")
            declared = [item for item in behavior["context"]["loaded_files"] if item["role"] == "selected-skill-declared-reference"]
            if not declared:
                errors.append("selected-skills prompt did not discover declared references")
    except Exception as exc:
        errors.append(f"failed to build selected-skills behavior prompt: {exc}")

runner = ROOT / "scripts" / "run_runtime_evals.py"
if runner.exists():
    text = runner.read_text(encoding="utf-8")
    for marker in (
        "--context-mode",
        "--allow-context-baseline",
        "--show-prompt",
        "--prompt-output",
        "build_routing_prompt",
        "assert_router_context",
        "build_selected_skills_prompt",
        "Refusing invalid Ollama score",
        "--contract-repair",
        "deterministic_contract_repair",
        "initial_actual",
        "contract_repair",
    ):
        if marker not in text:
            errors.append(f"runtime runner missing marker: {marker}")

grader = ROOT / "scripts" / "grade_runtime_evals.py"
if grader.exists():
    text = grader.read_text(encoding="utf-8")
    for marker in (
        "--markdown-output",
        "initial_metrics",
        "supporting_skill_exact_accuracy",
        "contract_repair",
        "render_markdown",
    ):
        if marker not in text:
            errors.append(f"runtime grader missing marker: {marker}")

workflow = ROOT / ".github" / "workflows" / "runtime-eval.yml"
if workflow.exists():
    text = workflow.read_text(encoding="utf-8")
    for marker in (
        "workflow_dispatch:",
        "OPENAI_API_KEY",
        "run_runtime_evals.py",
        "grade_runtime_evals.py",
        "upload-artifact@v4",
    ):
        if marker not in text:
            errors.append(f"runtime workflow missing marker: {marker}")

print(
    f"Validated Runtime Eval context assembly: {len(cases)} Canary cases, "
    f"{len(valid_skills)} skill IDs, router/manifest/none modes, and selected-skill loading"
)
print("NOTE: static validation and synthetic grader checks do not call Ollama or another model API.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
