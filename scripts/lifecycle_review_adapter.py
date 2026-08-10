from __future__ import annotations
import copy
from typing import Any
from review_assurance_contract import achieved_level,next_review_cells

def consume_budget(state:dict[str,Any],kind:str,amount:int|float)->dict[str,Any]:
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
    remaining=max(0,int(budget.get("limit",0)-budget.get("used",0)))
    return {"required_level":required,"achieved_level":achieved_level(record.get("workers",[])),"next_cells":next_review_cells(record,required,{"provider_calls":remaining})}
