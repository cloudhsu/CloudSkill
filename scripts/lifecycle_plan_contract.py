from __future__ import annotations
import copy,hashlib,json
from typing import Any
from lifecycle_template_contract import RESOLUTION_PROVENANCE, validate_selected_resolution
from review_assurance_contract import LEVELS

UNRESOLVED_PROVENANCE="lifecycle_plan_contract.replan_unresolved"
PLAN_RESOLUTION_FIELDS={
    "status","template_ids","contract_versions","delta_evidence_hash",
    "composition_order","resolved_review_level","resolution_schema_version",
    "resolution_provenance","composer_resolution_integrity_hash",
    "plan_revision","full_risk_calculation_required",
    "plan_resolution_integrity_hash",
}

def create_plan(
    work_id:str,
    profiles:list[str],
    source_hash:str,
    tasks:list[dict[str,Any]],
    template_resolution:dict[str,Any]|None=None,
)->dict[str,Any]:
    ids=[task.get("task_id") for task in tasks]
    if any(not value for value in ids) or len(ids)!=len(set(ids)): raise ValueError("task IDs must be unique and nonblank")
    known=set(ids)
    for task in tasks:
        if not task.get("owner") or any(dep not in known for dep in task.get("dependencies",[])): raise ValueError("task owner/dependency invalid")
    plan_id="PLAN-"+hashlib.sha256((work_id+source_hash).encode()).hexdigest()[:12]
    plan={"schema_version":1,"plan_id":plan_id,"revision":1,"based_on_revision":None,"work_id":work_id,"profiles":profiles,"source_hash":source_hash,"risk_baseline":{},"tasks":copy.deepcopy(tasks),"tasks_added":ids,"tasks_removed":[],"tasks_invalidated":[],"evidence_reused":[],"authority_required":[],"required_review_level":"L2_SINGLE_FAMILY_QUAD"}
    if template_resolution is not None:
        plan["template_resolution"]=_selected_plan_resolution(template_resolution,1)
        plan["template_resolution_lineage"]=[]
        plan["required_review_level"]=max(
            plan["required_review_level"],
            plan["template_resolution"]["resolved_review_level"],
            key=LEVELS.index,
        )
    return plan

def _selected_plan_resolution(resolution:dict[str,Any],plan_revision:int)->dict[str,Any]:
    try:
        validate_selected_resolution(resolution)
    except ValueError as exc:
        raise ValueError(
            "plan requires selected template resolution with composer-selected provenance and integrity"
        ) from exc
    snapshot={
        "status":"selected",
        "template_ids":copy.deepcopy(resolution["template_ids"]),
        "contract_versions":copy.deepcopy(resolution["contract_versions"]),
        "delta_evidence_hash":resolution["delta_evidence_hash"],
        "composition_order":copy.deepcopy(resolution["composition_order"]),
        "resolved_review_level":resolution["resolved_review_level"],
        "resolution_schema_version":resolution["resolution_schema_version"],
        "resolution_provenance":resolution["resolution_provenance"],
        "composer_resolution_integrity_hash":resolution["resolution_integrity_hash"],
        "plan_revision":plan_revision,
        "full_risk_calculation_required":False,
    }
    return _seal_plan_resolution(snapshot)

def _unresolved_plan_resolution(prior:dict[str,Any],plan_revision:int)->dict[str,Any]:
    snapshot={
        "status":"escalation_required",
        "template_ids":copy.deepcopy(prior["template_ids"]),
        "contract_versions":copy.deepcopy(prior["contract_versions"]),
        "delta_evidence_hash":None,
        "composition_order":copy.deepcopy(prior["composition_order"]),
        "resolved_review_level":prior["resolved_review_level"],
        "resolution_schema_version":1,
        "resolution_provenance":UNRESOLVED_PROVENANCE,
        "composer_resolution_integrity_hash":None,
        "plan_revision":plan_revision,
        "full_risk_calculation_required":True,
    }
    return _seal_plan_resolution(snapshot)

def _advance_plan_resolution(prior:dict[str,Any],plan_revision:int)->dict[str,Any]:
    snapshot={key:copy.deepcopy(value) for key,value in prior.items() if key!="plan_resolution_integrity_hash"}
    snapshot["plan_revision"]=plan_revision
    return _seal_plan_resolution(snapshot)

def _seal_plan_resolution(snapshot:dict[str,Any])->dict[str,Any]:
    value=copy.deepcopy(snapshot)
    value["plan_resolution_integrity_hash"]=_canonical_hash(value)
    return value

def _validate_plan_resolution(snapshot:Any,expected_revision:int|None=None)->None:
    if not isinstance(snapshot,dict) or set(snapshot)!=PLAN_RESOLUTION_FIELDS:
        raise ValueError("invalid template resolution lineage shape")
    supplied_hash=snapshot["plan_resolution_integrity_hash"]
    payload={key:copy.deepcopy(value) for key,value in snapshot.items() if key!="plan_resolution_integrity_hash"}
    template_ids=snapshot["template_ids"]
    versions=snapshot["contract_versions"]
    revision=snapshot["plan_revision"]
    status=snapshot["status"]
    common_invalid=(
        not _is_hash(supplied_hash)
        or supplied_hash!=_canonical_hash(payload)
        or type(revision) is not int or revision<1
        or (expected_revision is not None and revision!=expected_revision)
        or not isinstance(template_ids,list) or not template_ids
        or any(not isinstance(value,str) or not value for value in template_ids)
        or len(template_ids)!=len(set(template_ids))
        or snapshot["composition_order"]!=template_ids
        or not isinstance(versions,dict) or set(versions)!=set(template_ids)
        or any(type(value) is not int or value<1 for value in versions.values())
        or snapshot["resolved_review_level"] not in LEVELS
        or snapshot["resolution_schema_version"]!=1
    )
    selected_invalid=(
        status=="selected"
        and (
            snapshot["full_risk_calculation_required"] is not False
            or snapshot["resolution_provenance"]!=RESOLUTION_PROVENANCE
            or not _is_hash(snapshot["delta_evidence_hash"])
            or not _is_hash(snapshot["composer_resolution_integrity_hash"])
        )
    )
    unresolved_invalid=(
        status=="escalation_required"
        and (
            snapshot["full_risk_calculation_required"] is not True
            or snapshot["resolution_provenance"]!=UNRESOLVED_PROVENANCE
            or snapshot["delta_evidence_hash"] is not None
            or snapshot["composer_resolution_integrity_hash"] is not None
        )
    )
    if common_invalid or status not in {"selected","escalation_required"} or selected_invalid or unresolved_invalid:
        raise ValueError("invalid template resolution lineage shape")

def _validated_lineage(plan:dict[str,Any])->tuple[dict[str,Any],list[dict[str,Any]]]:
    revision=plan.get("revision")
    if type(revision) is not int or revision<1:
        raise ValueError("invalid template resolution lineage revision")
    current=plan.get("template_resolution")
    _validate_plan_resolution(current,revision)
    lineage=plan.get("template_resolution_lineage")
    if not isinstance(lineage,list):
        raise ValueError("invalid template resolution lineage shape")
    previous_revision=0
    for item in lineage:
        _validate_plan_resolution(item)
        item_revision=item["plan_revision"]
        if item["status"]!="selected" or item_revision<=previous_revision or item_revision>=revision:
            raise ValueError("invalid template resolution lineage revision ordering")
        previous_revision=item_revision
    return copy.deepcopy(current),copy.deepcopy(lineage)

def _canonical_hash(value:Any)->str:
    encoded=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

def _is_hash(value:Any)->bool:
    return isinstance(value,str) and len(value)==64 and all(character in "0123456789abcdef" for character in value)

def replan(plan:dict[str,Any], trigger:dict[str,Any], risk:dict[str,Any], impact:dict[str,Any], template_resolution:dict[str,Any]|None=None)->dict[str,Any]:
    if not trigger.get("kind") or not trigger.get("evidence_hash"): raise ValueError("replan needs evidence trigger")
    prior_resolution:dict[str,Any]|None=None
    lineage:list[dict[str,Any]]|None=None
    if "template_resolution" in plan:
        prior_resolution,lineage=_validated_lineage(plan)
    elif "template_resolution_lineage" in plan:
        raise ValueError("invalid template resolution lineage shape")
    elif type(plan.get("revision")) is not int or plan["revision"]<1:
        raise ValueError("replan needs valid plan revision")
    value=copy.deepcopy(plan)
    value["based_on_revision"]=plan["revision"]; value["revision"]+=1
    value["change_trigger"]=copy.deepcopy(trigger); value["risk_baseline"]=copy.deepcopy(risk)
    value["tasks_invalidated"]=list(dict.fromkeys(impact.get("invalidate",[])))
    value["evidence_reused"]=list(dict.fromkeys(impact.get("reuse",[])))
    if "template_resolution" in plan:
        assert prior_resolution is not None and lineage is not None
        invalidated_evidence=list(dict.fromkeys(impact.get("invalidate_evidence",[])))
        if set(invalidated_evidence)&set(value["evidence_reused"]):
            raise ValueError("evidence cannot be both invalidated and reused")
        if prior_resolution["status"]=="selected":
            lineage.append(prior_resolution)
        value["template_resolution_lineage"]=lineage
        if template_resolution is not None:
            value["template_resolution"]=_selected_plan_resolution(template_resolution,value["revision"])
        elif invalidated_evidence:
            value["template_resolution"]=_unresolved_plan_resolution(prior_resolution,value["revision"])
        else:
            value["template_resolution"]=_advance_plan_resolution(prior_resolution,value["revision"])
        value["evidence_invalidated"]=invalidated_evidence
    elif template_resolution is not None:
        raise ValueError("template resolution replacement requires existing template resolution lineage")
    value["required_review_level"]="L1_CROSS_FAMILY_2X2" if risk.get("risk_class")=="high" else plan["required_review_level"]
    if "template_resolution" in value:
        value["required_review_level"]=max(
            value["required_review_level"],
            value["template_resolution"]["resolved_review_level"],
            key=LEVELS.index,
        )
    value["authority_required"]=["expanded_scope"] if trigger["kind"] in {"authority_boundary_changed","side_effect_scope_changed"} else []
    return value
