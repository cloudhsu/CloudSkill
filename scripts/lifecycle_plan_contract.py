from __future__ import annotations
import copy,hashlib,json
from typing import Any
from lifecycle_template_contract import DELTA_FIELDS, RESOLUTION_PROVENANCE, validate_selected_resolution
from review_assurance_contract import LEVELS

UNRESOLVED_PROVENANCE="lifecycle_plan_contract.replan_unresolved"
DELTA_INVALIDATING_TRIGGER_KINDS={
    "authority_boundary_changed",
    "side_effect_scope_changed",
    "sensitive_or_privileged_changed",
    "platform_or_compatibility_changed",
    "irreversible_or_unreconciled_changed",
    "outside_verified_envelope_changed",
    "verified_envelope_changed",
}
PLAN_RESOLUTION_FIELDS={
    "status","template_ids","contract_versions","delta_evidence_hash",
    "composition_order","resolved_review_level","resolution_schema_version",
    "resolution_provenance","composer_resolution_integrity_hash",
    "selection_context","selection_context_hash",
    "plan_revision","full_risk_calculation_required",
    "plan_resolution_integrity_hash",
}

def create_plan(
    work_id:str,
    profiles:list[str],
    source_hash:str,
    tasks:list[dict[str,Any]],
    template_resolution:dict[str,Any]|None=None,
    template_registry:dict[str,Any]|None=None,
    template_facts:dict[str,Any]|None=None,
    risk_context:dict[str,Any]|None=None,
)->dict[str,Any]:
    ids=[task.get("task_id") for task in tasks]
    if any(not value for value in ids) or len(ids)!=len(set(ids)): raise ValueError("task IDs must be unique and nonblank")
    known=set(ids)
    for task in tasks:
        if not task.get("owner") or any(dep not in known for dep in task.get("dependencies",[])): raise ValueError("task owner/dependency invalid")
    plan_id="PLAN-"+hashlib.sha256((work_id+source_hash).encode()).hexdigest()[:12]
    plan={"schema_version":1,"plan_id":plan_id,"revision":1,"based_on_revision":None,"work_id":work_id,"profiles":profiles,"source_hash":source_hash,"risk_baseline":{},"tasks":copy.deepcopy(tasks),"tasks_added":ids,"tasks_removed":[],"tasks_invalidated":[],"evidence_reused":[],"authority_required":[],"required_review_level":"L2_SINGLE_FAMILY_QUAD"}
    if template_resolution is not None:
        plan["template_resolution"]=_selected_plan_resolution(
            template_resolution,
            template_registry,
            1,
            work_id,
            source_hash,
            tasks,
            template_facts,
            risk_context,
        )
        plan["template_resolution_lineage"]=[]
        plan["risk_baseline"]=copy.deepcopy(risk_context)
        plan["required_review_level"]=max(
            plan["required_review_level"],
            plan["template_resolution"]["resolved_review_level"],
            key=LEVELS.index,
        )
    return plan

def _selected_plan_resolution(
    resolution:dict[str,Any],
    registry:dict[str,Any]|None,
    plan_revision:int,
    work_id:str,
    source_hash:str,
    tasks:list[dict[str,Any]],
    task_facts:dict[str,Any]|None,
    risk_context:dict[str,Any]|None,
)->dict[str,Any]:
    if registry is None:
        raise ValueError("plan requires authoritative registry for selected template resolution")
    try:
        validate_selected_resolution(
            resolution,
            registry,
            work_id=work_id,
            source_hash=source_hash,
            tasks=tasks,
            task_facts=task_facts,
            risk_context=risk_context,
        )
    except ValueError as exc:
        raise ValueError(
            "plan requires selected template resolution with composer-selected provenance, integrity, and authoritative registry replay"
        ) from exc
    snapshot={
        "status":"selected",
        "template_ids":copy.deepcopy(resolution["template_ids"]),
        "contract_versions":copy.deepcopy(resolution["contract_versions"]),
        "delta_evidence_hash":resolution["delta_evidence_hash"],
        "composition_order":copy.deepcopy(resolution["composition_order"]),
        "resolved_review_level":resolution["resolved_review_level"],
        "selection_context":copy.deepcopy(resolution["selection_context"]),
        "selection_context_hash":resolution["selection_context_hash"],
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
        "selection_context":copy.deepcopy(prior["selection_context"]),
        "selection_context_hash":prior["selection_context_hash"],
        "resolution_schema_version":2,
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
    selection_context=snapshot["selection_context"]
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
        or snapshot["resolution_schema_version"]!=2
        or not isinstance(selection_context,dict)
        or set(selection_context)!={"work_id","source_hash","tasks","task_facts","risk_context","registry_identity"}
        or not isinstance(selection_context.get("work_id"),str)
        or not selection_context.get("work_id","").strip()
        or not _is_hash(selection_context.get("source_hash"))
        or not isinstance(selection_context.get("tasks"),list)
        or not selection_context.get("tasks")
        or not isinstance(selection_context.get("task_facts"),dict)
        or not isinstance(selection_context.get("risk_context"),dict)
        or not isinstance(selection_context.get("registry_identity"),dict)
        or set(selection_context.get("registry_identity",{}))!={"schema_version","sha256"}
        or selection_context.get("registry_identity",{}).get("schema_version")!=1
        or not _is_hash(selection_context.get("registry_identity",{}).get("sha256"))
        or not _is_hash(snapshot["selection_context_hash"])
        or snapshot["selection_context_hash"]!=_canonical_hash(selection_context)
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
    if current["status"]=="selected":
        context=current["selection_context"]
        if (
            context["work_id"]!=plan.get("work_id")
            or context["source_hash"]!=plan.get("source_hash")
            or context["tasks"]!=plan.get("tasks")
            or context["risk_context"]!=plan.get("risk_baseline")
        ):
            raise ValueError("invalid template resolution lineage context binding")
    lineage=plan.get("template_resolution_lineage")
    if not isinstance(lineage,list):
        raise ValueError("invalid template resolution lineage shape")
    if len(lineage)!=revision-1:
        raise ValueError("invalid template resolution lineage revision ordering")
    for expected_revision,item in enumerate(lineage,start=1):
        _validate_plan_resolution(item)
        item_revision=item["plan_revision"]
        if item_revision!=expected_revision:
            raise ValueError("invalid template resolution lineage revision ordering")
    return copy.deepcopy(current),copy.deepcopy(lineage)

def _canonical_hash(value:Any)->str:
    encoded=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

def _is_hash(value:Any)->bool:
    return isinstance(value,str) and len(value)==64 and all(character in "0123456789abcdef" for character in value)

def _trigger_contradicts_selected_context(
    prior_resolution:dict[str,Any],
    trigger:dict[str,Any],
    risk:dict[str,Any],
    template_facts:dict[str,Any]|None,
)->bool:
    if prior_resolution["status"]!="selected":
        return False
    context=prior_resolution["selection_context"]
    kind=trigger["kind"]
    if kind=="source_changed" or kind in DELTA_INVALIDATING_TRIGGER_KINDS:
        return True
    if kind in {f"{field}_changed" for field in DELTA_FIELDS}:
        return True
    delta_changes=trigger.get("delta_changes")
    if delta_changes is not None:
        if not isinstance(delta_changes,dict) or any(
            field not in DELTA_FIELDS or type(value) is not bool
            for field,value in delta_changes.items()
        ):
            return True
        if any(value is True for value in delta_changes.values()):
            return True
    if any(
        field in trigger and trigger[field] is not False
        for field in DELTA_FIELDS
    ):
        return True
    if risk!=context["risk_context"]:
        return True
    if template_facts is not None and template_facts!=context["task_facts"]:
        return True
    return False

def replan(plan:dict[str,Any], trigger:dict[str,Any], risk:dict[str,Any], impact:dict[str,Any], template_resolution:dict[str,Any]|None=None, template_registry:dict[str,Any]|None=None, template_facts:dict[str,Any]|None=None)->dict[str,Any]:
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
    if trigger["kind"]=="source_changed":
        if not _is_hash(trigger["evidence_hash"]):
            raise ValueError("source change requires authoritative source hash evidence")
        value["source_hash"]=trigger["evidence_hash"]
    value["change_trigger"]=copy.deepcopy(trigger); value["risk_baseline"]=copy.deepcopy(risk)
    value["tasks_invalidated"]=list(dict.fromkeys(impact.get("invalidate",[])))
    value["evidence_reused"]=list(dict.fromkeys(impact.get("reuse",[])))
    if "template_resolution" in plan:
        assert prior_resolution is not None and lineage is not None
        invalidated_evidence=list(dict.fromkeys(impact.get("invalidate_evidence",[])))
        context_invalidated=_trigger_contradicts_selected_context(
            prior_resolution,
            trigger,
            risk,
            template_facts,
        )
        if context_invalidated and prior_resolution["status"]=="selected":
            invalidated_evidence=list(dict.fromkeys([
                *invalidated_evidence,
                prior_resolution["delta_evidence_hash"],
            ]))
        if set(invalidated_evidence)&set(value["evidence_reused"]):
            raise ValueError("evidence cannot be both invalidated and reused")
        lineage.append(prior_resolution)
        value["template_resolution_lineage"]=lineage
        selection_evidence_ids={
            prior_resolution["delta_evidence_hash"]
        } if prior_resolution["status"]=="selected" else set()
        selection_evidence_invalidated=bool(
            selection_evidence_ids & set(invalidated_evidence)
        )
        if template_resolution is not None:
            replacement_resolution=_selected_plan_resolution(
                template_resolution,
                template_registry,
                value["revision"],
                value["work_id"],
                value["source_hash"],
                value["tasks"],
                template_facts,
                risk,
            )
            if (
                context_invalidated
                and prior_resolution["status"]=="selected"
                and replacement_resolution["selection_context_hash"]
                ==prior_resolution["selection_context_hash"]
            ):
                raise ValueError("invalidating trigger requires a fresh authoritative resolution bound to new context")
            value["template_resolution"]=replacement_resolution
        elif selection_evidence_invalidated:
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
