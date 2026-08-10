from __future__ import annotations
import json,os
from pathlib import Path
from typing import Any

def _pairs(pairs):
    value={}
    for key,item in pairs:
        if key in value: raise ValueError("duplicate state member")
        value[key]=item
    return value

def load_state(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=_pairs)
    if value.get("schema_version")!=1: raise ValueError("MIGRATION_REQUIRED")
    return value

def _validate_authority(state:dict[str,Any])->None:
    action=state.get("current_action")
    if not action:return
    approved=set((state.get("authority") or {}).get("approved_actions",[]))
    requested=action.get("authority_scope")
    if not isinstance(requested,list) or any(not isinstance(item,str) or not item for item in requested) or not set(requested)<=approved:
        raise ValueError("current action exceeds approved authority")

def save_state_atomic(path:Path,state:dict[str,Any],expected_revision:int,*,owner_id:str|None=None,fencing_token:int|None=None,now:int|None=None)->dict[str,Any]:
    current=load_state(path) if path.is_file() else None
    actual=current["revision"] if current else 0
    if actual!=expected_revision: raise ValueError("stale state revision")
    current_lease=(current or {}).get("lease")
    proposed_lease=state.get("lease")
    if current_lease is not None and (current_lease.get("owner_id")!=owner_id or current_lease.get("fencing_token")!=fencing_token):
        turnover=(now is not None and current_lease.get("expires_at",0)<=now and proposed_lease is not None and proposed_lease.get("owner_id")==owner_id and proposed_lease.get("fencing_token")==fencing_token and isinstance(fencing_token,int) and fencing_token>current_lease.get("fencing_token",0))
        if not turnover: raise ValueError("stale lifecycle fencing token")
    elif current_lease is None and proposed_lease is not None and (proposed_lease.get("owner_id")!=owner_id or proposed_lease.get("fencing_token")!=fencing_token):
        raise ValueError("stale lifecycle fencing token")
    value=json.loads(json.dumps(state))
    if value.get("schema_version")!=1: raise ValueError("MIGRATION_REQUIRED")
    _validate_authority(value)
    value["revision"]=actual+1
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w",encoding="utf-8") as stream:
        json.dump(value,stream,sort_keys=True,indent=2); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)
    return value
