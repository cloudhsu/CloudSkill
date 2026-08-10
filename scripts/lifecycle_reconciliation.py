from __future__ import annotations
import copy
from typing import Any,Callable

def acquire_lease(state:dict[str,Any],owner_id:str,now:int,ttl_seconds:int)->dict[str,Any]:
    value=copy.deepcopy(state); old=value.get("lease") or {}
    if old and old.get("expires_at",0)>now and old.get("owner_id")!=owner_id: raise ValueError("active lease held by another owner")
    value["lease"]={"owner_id":owner_id,"fencing_token":int(old.get("fencing_token",0))+1,"expires_at":now+ttl_seconds}
    return value

def assert_fence(state:dict[str,Any],owner_id:str,fencing_token:int)->None:
    lease=state.get("lease") or {}
    if lease.get("owner_id")!=owner_id or lease.get("fencing_token")!=fencing_token: raise ValueError("stale lifecycle writer")

def reconcile_action(state:dict[str,Any],inspector:Callable[[dict[str,Any]],dict[str,Any]])->str:
    action=state.get("current_action")
    if not action:return "SAFE_TO_RESUME"
    if action.get("plan_revision") not in {None,state.get("plan_revision")}:return "STALE_BASELINE"
    result=inspector(action)
    external=result.get("state")
    if external=="completed":return "ALREADY_COMPLETED"
    if external=="failed":return "RETRY_REQUIRED"
    if external=="authority_required":return "AUTHORITY_REQUIRED"
    return "RECONCILIATION_REQUIRED"

