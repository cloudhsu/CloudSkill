from __future__ import annotations
import copy,hashlib,json
from typing import Any

def create_plan(work_id:str, profiles:list[str], source_hash:str, tasks:list[dict[str,Any]])->dict[str,Any]:
    ids=[task.get("task_id") for task in tasks]
    if any(not value for value in ids) or len(ids)!=len(set(ids)): raise ValueError("task IDs must be unique and nonblank")
    known=set(ids)
    for task in tasks:
        if not task.get("owner") or any(dep not in known for dep in task.get("dependencies",[])): raise ValueError("task owner/dependency invalid")
    plan_id="PLAN-"+hashlib.sha256((work_id+source_hash).encode()).hexdigest()[:12]
    return {"schema_version":1,"plan_id":plan_id,"revision":1,"based_on_revision":None,"work_id":work_id,"profiles":profiles,"source_hash":source_hash,"risk_baseline":{},"tasks":copy.deepcopy(tasks),"tasks_added":ids,"tasks_removed":[],"tasks_invalidated":[],"evidence_reused":[],"authority_required":[],"required_review_level":"L2_SINGLE_FAMILY_QUAD"}

def replan(plan:dict[str,Any], trigger:dict[str,Any], risk:dict[str,Any], impact:dict[str,Any])->dict[str,Any]:
    if not trigger.get("kind") or not trigger.get("evidence_hash"): raise ValueError("replan needs evidence trigger")
    value=copy.deepcopy(plan)
    value["based_on_revision"]=plan["revision"]; value["revision"]+=1
    value["change_trigger"]=copy.deepcopy(trigger); value["risk_baseline"]=copy.deepcopy(risk)
    value["tasks_invalidated"]=list(dict.fromkeys(impact.get("invalidate",[])))
    value["evidence_reused"]=list(dict.fromkeys(impact.get("reuse",[])))
    value["required_review_level"]="L1_CROSS_FAMILY_2X2" if risk.get("risk_class")=="high" else plan["required_review_level"]
    value["authority_required"]=["expanded_scope"] if trigger["kind"] in {"authority_boundary_changed","side_effect_scope_changed"} else []
    return value

