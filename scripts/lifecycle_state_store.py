from __future__ import annotations
import errno,json,os
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
    authority=value.get("authority") or {}
    if "grant" in authority:
        if "grants" in authority: raise ValueError("ambiguous authority grant history")
        authority["grants"]=[authority.pop("grant")]
    return value

def _validate_authority(state:dict[str,Any],current:dict[str,Any]|None)->None:
    authority=state.get("authority") or {}
    approved=set(authority.get("approved_actions",[]))
    prohibited=set(authority.get("prohibited_actions",[]))
    if approved & prohibited: raise ValueError("approved authority overlaps prohibited authority")
    if current is not None:
        current_authority=current.get("authority") or {}
        prior=set(current_authority.get("approved_actions",[]))
        prior_grants=current_authority.get("grants",[])
        proposed_grants=authority.get("grants",[])
        if not isinstance(prior_grants,list) or not isinstance(proposed_grants,list) or proposed_grants[:len(prior_grants)]!=prior_grants:
            raise ValueError("durable authority grant history must be append-only")
        added=approved-prior
        if added:
            appended=proposed_grants[len(prior_grants):]
            grant=appended[0] if len(appended)==1 else None
            valid=isinstance(grant,dict) and set(grant)=={"authorizer","authorized_at","source_hash","plan_revision","added_actions"} and grant.get("plan_revision")==state.get("plan_revision") and grant.get("added_actions")==sorted(added) and all(isinstance(grant.get(key),str) and grant[key] for key in ("authorizer","authorized_at")) and isinstance(grant.get("source_hash"),str) and len(grant["source_hash"])==64 and all(char in "0123456789abcdef" for char in grant["source_hash"])
            if not valid: raise ValueError("resumed writer cannot expand authority without exact grant evidence")
        elif len(proposed_grants)!=len(prior_grants):
            raise ValueError("authority grant cannot be appended without expansion")
    action=state.get("current_action")
    if not action:return
    requested=action.get("authority_scope")
    attempt=action.get("attempt"); maximum=action.get("max_attempts")
    if not isinstance(attempt,int) or isinstance(attempt,bool) or not isinstance(maximum,int) or isinstance(maximum,bool) or attempt<1 or maximum<1 or attempt>maximum:
        raise ValueError("current action attempt exceeds retry bound")
    if not isinstance(requested,list) or any(not isinstance(item,str) or not item for item in requested) or not set(requested)<=approved or set(requested)&prohibited:
        raise ValueError("current action exceeds approved authority")

def _fsync_directory(directory:Path)->None:
    try: descriptor=os.open(str(directory),os.O_RDONLY)
    except OSError as exc:
        if exc.errno in {errno.EINVAL,errno.ENOTSUP,errno.EISDIR}: return
        raise
    try: os.fsync(descriptor)
    except OSError as exc:
        if exc.errno not in {errno.EINVAL,errno.ENOTSUP}: raise
    finally: os.close(descriptor)

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
    _validate_authority(value,current)
    value["revision"]=actual+1
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w",encoding="utf-8") as stream:
        json.dump(value,stream,sort_keys=True,indent=2); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)
    _fsync_directory(path.parent)
    return value
