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

def save_state_atomic(path:Path,state:dict[str,Any],expected_revision:int,*,owner_id:str|None=None,fencing_token:int|None=None)->dict[str,Any]:
    current=load_state(path) if path.is_file() else None
    actual=current["revision"] if current else 0
    if actual!=expected_revision: raise ValueError("stale state revision")
    lease=(current or {}).get("lease") or state.get("lease")
    if lease is not None and (lease.get("owner_id")!=owner_id or lease.get("fencing_token")!=fencing_token):
        raise ValueError("stale lifecycle fencing token")
    value=json.loads(json.dumps(state))
    if value.get("schema_version")!=1: raise ValueError("MIGRATION_REQUIRED")
    value["revision"]=actual+1
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w",encoding="utf-8") as stream:
        json.dump(value,stream,sort_keys=True,indent=2); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)
    return value
