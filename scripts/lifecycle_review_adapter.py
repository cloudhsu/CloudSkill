from __future__ import annotations
import copy
import math
from typing import Any
from review_assurance_contract import achieved_level,evidence_applicable,next_review_cells

REVIEW_CONTEXT_FIELDS={"review_scope","source_hash","contract_hash","packet_hash","rubric_hash","risk_class"}

def consume_budget(state:dict[str,Any],kind:str,amount:int|float)->dict[str,Any]:
    if isinstance(amount,bool) or not isinstance(amount,(int,float)) or not math.isfinite(amount) or amount<=0:
        raise ValueError("budget amount must be finite and positive")
    value=copy.deepcopy(state); budget=value.setdefault("budgets",{}).get(kind)
    if not isinstance(budget,dict): raise ValueError("unknown lifecycle budget")
    proposed=budget.get("used",0)+amount
    if proposed>budget.get("limit",0):
        value["status"]="paused"
        value["budget_rejection"]={"kind":kind,"amount":amount,"remaining":max(0,budget.get("limit",0)-budget.get("used",0))}
        return value
    budget["used"]=proposed
    return value

def plan_review(state:dict[str,Any],record:dict[str,Any])->dict[str,Any]:
    required=state.get("review",{}).get("required_level","L0_NONE")
    budget=state.get("budgets",{}).get("provider_calls",{"limit":0,"used":0})
    if not isinstance(budget,dict): raise ValueError("invalid provider_calls budget")
    remaining=max(0,int(budget.get("limit",0)-budget.get("used",0)))
    context=state.get("review",{}).get("evidence_context")
    reusable=isinstance(context,dict) and set(context)==REVIEW_CONTEXT_FIELDS and evidence_applicable(record,**{key:context[key] for key in REVIEW_CONTEXT_FIELDS if key!="review_scope"}) and record.get("review_scope")==context["review_scope"]
    effective=record if reusable else {"workers":[],"blocking_findings":[]}
    return {"required_level":required,"achieved_level":achieved_level(effective.get("workers",[])),"evidence_reused":reusable,"next_cells":next_review_cells(effective,required,{"provider_calls":remaining})}
