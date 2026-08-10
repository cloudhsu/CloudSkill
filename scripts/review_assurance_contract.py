from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEVELS = ("L0_NONE","L0_SINGLE_REVIEW","L3_SINGLE_FAMILY_PAIR","L2_SINGLE_FAMILY_QUAD","L1_CROSS_FAMILY_2X2")
COMPLETED = {"PASS","FAIL","MANUAL_REQUIRED"}
BLOCKING_SEVERITIES = {"Critical","High"}
EXCEPTION_FIELDS = {"authorizer","authorized_at","scope","source_hash","required_level","achieved_level","remaining_risk"}


def canonical_independent_cells(workers: list[dict[str, Any]]) -> set[tuple[str,str]]:
    cells=set()
    for worker in workers:
        family=worker.get("family")
        model=worker.get("canonical_model")
        if worker.get("status") in COMPLETED and worker.get("model_identity_evidence") in {"provider_returned","explicit_selection"} and isinstance(family,str) and isinstance(model,str) and model.strip():
            cells.add((family,model))
    return cells


def achieved_level(workers: list[dict[str, Any]]) -> str:
    cells=canonical_independent_cells(workers)
    by_family: dict[str,set[str]]={}
    for family,model in cells:
        by_family.setdefault(family,set()).add(model)
    if sum(1 for models in by_family.values() if len(models)>=2)>=2:
        return "L1_CROSS_FAMILY_2X2"
    if any(len(models)>=4 for models in by_family.values()):
        return "L2_SINGLE_FAMILY_QUAD"
    if any(len(models)>=2 for models in by_family.values()):
        return "L3_SINGLE_FAMILY_PAIR"
    return "L0_SINGLE_REVIEW" if cells else "L0_NONE"


def level_rank(level: str) -> int:
    try:
        return LEVELS.index(level)
    except ValueError as exc:
        raise ValueError(f"unknown assurance level: {level}") from exc


def load_review_policy(path: Path) -> dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version")!=1 or value.get("levels")!=list(LEVELS):
        raise ValueError("invalid review assurance policy")
    return value


def required_level(scope: str, risk_class: str, policy: dict[str,Any]) -> str:
    override=policy.get("scope_overrides",{}).get(scope,{})
    level=override.get(risk_class,policy.get("defaults",{}).get(risk_class))
    if level not in LEVELS:
        raise ValueError("review scope/risk has no valid assurance requirement")
    return level


def _valid_exception(exception: Any, required: str, achieved: str) -> bool:
    return isinstance(exception,dict) and set(exception)==EXCEPTION_FIELDS and exception.get("required_level")==required and exception.get("achieved_level")==achieved and all(isinstance(exception.get(key),str) and exception[key].strip() for key in EXCEPTION_FIELDS) and len(exception["source_hash"])==64


def decide_review(required: str, achieved: str, findings: list[dict[str,Any]], exception: dict[str,Any] | None, workers: list[dict[str,Any]] | None=None) -> dict[str,Any]:
    unresolved_worker=workers is not None and any(item.get("status")!="PASS" for item in workers)
    if unresolved_worker or any(item.get("severity") in BLOCKING_SEVERITIES or item.get("veto") is True for item in findings):
        decision="BLOCKED"
    elif level_rank(achieved)>=level_rank(required):
        decision="PASS"
    elif _valid_exception(exception,required,achieved):
        decision="PASS_WITH_EXCEPTION"
    else:
        decision="BLOCKED"
    return {"required_level":required,"achieved_level":achieved,"decision":decision,"exception_used":decision=="PASS_WITH_EXCEPTION"}

def validate_review_record(record: dict[str,Any]) -> list[str]:
    errors=[]
    workers=record.get("workers")
    findings=record.get("blocking_findings")
    if not isinstance(workers,list): return ["workers must be an array"]
    if not isinstance(findings,list): return ["blocking_findings must be an array"]
    computed=achieved_level(workers)
    if record.get("achieved_level")!=computed: errors.append("achieved_level does not match workers")
    try: decision=decide_review(record.get("required_level"),computed,findings,record.get("exception"),workers)["decision"]
    except (TypeError,ValueError): errors.append("review levels are invalid")
    else:
        if record.get("decision")!=decision: errors.append("decision does not match review evidence")
    return errors


def evidence_applicable(record: dict[str,Any], *, source_hash: str, contract_hash: str, packet_hash: str, rubric_hash: str, risk_class: str) -> bool:
    expected={"source_hash":source_hash,"contract_hash":contract_hash,"packet_hash":packet_hash,"rubric_hash":rubric_hash,"risk_class":risk_class}
    return all(record.get(key)==value for key,value in expected.items())


def next_review_cells(record: dict[str,Any], required: str, budget: dict[str,Any]) -> list[dict[str,str]]:
    if required=="L0_NONE" or record.get("blocking_findings") or int(budget.get("provider_calls",0))<=0:
        return []
    current=achieved_level(record.get("workers",[]))
    if level_rank(current)>=level_rank(required):
        return []
    targets={"L0_SINGLE_REVIEW":1,"L3_SINGLE_FAMILY_PAIR":2,"L2_SINGLE_FAMILY_QUAD":4,"L1_CROSS_FAMILY_2X2":4}
    missing=max(0,targets[required]-len(canonical_independent_cells(record.get("workers",[]))))
    return [{"role":"efficient" if index==0 else "frontier","family":"diverse" if required=="L1_CROSS_FAMILY_2X2" else "single"} for index in range(min(missing,int(budget["provider_calls"])))]
