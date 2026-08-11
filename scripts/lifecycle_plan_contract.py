from __future__ import annotations
import copy,hashlib,json
from typing import Any
from review_assurance_contract import LEVELS

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
        plan["template_resolution"]=_plan_template_resolution(template_resolution,1)
        plan["template_resolution_lineage"]=[]
        plan["required_review_level"]=max(
            plan["required_review_level"],
            plan["template_resolution"]["resolved_review_level"],
            key=LEVELS.index,
        )
    return plan

def _plan_template_resolution(resolution:dict[str,Any],plan_revision:int)->dict[str,Any]:
    if not isinstance(resolution,dict) or resolution.get("status")!="selected" or resolution.get("full_risk_calculation_required") is not False:
        raise ValueError("plan requires a selected template resolution")
    template_ids=resolution.get("template_ids")
    composition_order=resolution.get("composition_order")
    versions=resolution.get("contract_versions")
    evidence_hash=resolution.get("delta_evidence_hash")
    review_level=resolution.get("resolved_review_level")
    if (
        not isinstance(template_ids,list)
        or not template_ids
        or any(not isinstance(value,str) or not value for value in template_ids)
        or len(template_ids)!=len(set(template_ids))
        or composition_order!=template_ids
        or not isinstance(versions,dict)
        or set(versions)!=set(template_ids)
        or any(type(value) is not int or value<1 for value in versions.values())
        or not isinstance(evidence_hash,str)
        or len(evidence_hash)!=64
        or any(character not in "0123456789abcdef" for character in evidence_hash)
        or review_level not in LEVELS
    ):
        raise ValueError("plan requires a selected template resolution with valid lineage evidence")
    return {
        "status":"selected",
        "template_ids":copy.deepcopy(template_ids),
        "contract_versions":copy.deepcopy(versions),
        "delta_evidence_hash":evidence_hash,
        "composition_order":copy.deepcopy(composition_order),
        "resolved_review_level":review_level,
        "plan_revision":plan_revision,
    }

def replan(plan:dict[str,Any], trigger:dict[str,Any], risk:dict[str,Any], impact:dict[str,Any])->dict[str,Any]:
    if not trigger.get("kind") or not trigger.get("evidence_hash"): raise ValueError("replan needs evidence trigger")
    value=copy.deepcopy(plan)
    value["based_on_revision"]=plan["revision"]; value["revision"]+=1
    value["change_trigger"]=copy.deepcopy(trigger); value["risk_baseline"]=copy.deepcopy(risk)
    value["tasks_invalidated"]=list(dict.fromkeys(impact.get("invalidate",[])))
    value["evidence_reused"]=list(dict.fromkeys(impact.get("reuse",[])))
    if "template_resolution" in plan:
        prior_resolution=copy.deepcopy(plan["template_resolution"])
        lineage=copy.deepcopy(plan.get("template_resolution_lineage",[]))
        invalidated_evidence=list(dict.fromkeys(impact.get("invalidate_evidence",[])))
        if set(invalidated_evidence)&set(value["evidence_reused"]):
            raise ValueError("evidence cannot be both invalidated and reused")
        lineage.append(prior_resolution)
        value["template_resolution_lineage"]=lineage
        value["template_resolution"]=copy.deepcopy(prior_resolution)
        value["template_resolution"]["plan_revision"]=value["revision"]
        value["evidence_invalidated"]=invalidated_evidence
    value["required_review_level"]="L1_CROSS_FAMILY_2X2" if risk.get("risk_class")=="high" else plan["required_review_level"]
    value["authority_required"]=["expanded_scope"] if trigger["kind"] in {"authority_boundary_changed","side_effect_scope_changed"} else []
    return value
