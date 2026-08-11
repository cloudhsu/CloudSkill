from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def load_profiles(path: Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version")!=1 or not isinstance(value.get("profiles"),dict): raise ValueError("invalid lifecycle profiles")
    return value

def select_profiles(pressure: dict[str,Any], profiles: dict[str,Any])->list[str]:
    if pressure.get("work_type")=="controlled_tool_adapter": selected=["controlled_tool_vertical_slice"]
    elif pressure.get("work_type")=="skill_evolution": selected=["eval_driven_evolution"]
    elif pressure.get("risk")=="low" and pressure.get("scope")=="local": selected=["lightweight_change"]
    else: selected=["iterative_incremental"]
    additions=[]
    if pressure.get("technical_uncertainty")=="high": additions.append("discovery_spike")
    if pressure.get("safety")=="high" or pressure.get("regulatory")=="high": additions.append("stage_gated")
    if pressure.get("hardware_dependency") is True: additions.append("hybrid_hardware_software")
    if pressure.get("urgent_field_impact") is True: selected=["hotfix"]
    if pressure.get("brownfield") is True: additions.append("brownfield_migration")
    result=[]
    for item in additions+selected:
        if item not in result:
            if item not in profiles["profiles"]: raise ValueError("unknown lifecycle profile")
            result.append(item)
    return result

def classify_failure(observation: dict[str,Any])->str:
    mechanism=observation.get("failed_mechanism")
    mapping={"grader":"verification_system","test_environment":"verification_system","component_interface":"design","data_model":"design","algorithm":"design","state_authority":"architect","persistence_boundary":"architect","recovery_model":"architect","acceptance_criterion":"analyze","requirement":"analyze","problem_context":"explore"}
    if mechanism in mapping:return mapping[mechanism]
    if mechanism=="implementation":return "implement"
    raise ValueError("failure mechanism is insufficient for re-entry")

def classify_tool_event(action:dict[str,Any],evidence:dict[str,Any])->str:
    if action.get("state")=="UNCERTAIN": return "reconcile"
    if evidence.get("risk_changed") or evidence.get("authority_changed"): return "replan"
    mechanism=evidence.get("failed_mechanism")
    if mechanism in {"state_authority","recovery_model","persistence_boundary"}: return "architect"
    if mechanism in {"malformed_evidence","result_contract","provenance"}: return "verify"
    if mechanism=="implementation": return "implement"
    if action.get("state")=="BLOCKED": return "block"
    if action.get("state")=="FAILED": return "stop"
    raise ValueError("tool event evidence is insufficient for lifecycle re-entry")

def deployment_decision(state:dict[str,Any],health_evidence:dict[str,Any])->str:
    if state.get("status") not in {"deployed","observing"}: return "AUTHORITY_REQUIRED"
    if not health_evidence.get("observation_complete"): return "HOLD"
    if health_evidence.get("hard_gate_breached"): return "ROLLBACK"
    return "ADVANCE"
