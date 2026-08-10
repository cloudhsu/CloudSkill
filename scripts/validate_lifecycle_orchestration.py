#!/usr/bin/env python3
from pathlib import Path
import json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from lifecycle_orchestration_contract import classify_failure, deployment_decision, load_profiles, select_profiles
from lifecycle_plan_contract import create_plan, replan
import lifecycle_state_store
from lifecycle_state_store import load_state, save_state_atomic
from lifecycle_reconciliation import acquire_lease, assert_fence, cancel_work, reconcile_action
from lifecycle_review_adapter import consume_budget, plan_review

profiles=load_profiles(ROOT/"config/lifecycle-profiles.json")
assert select_profiles({"work_type":"development","risk":"low"},profiles)==["iterative_incremental"]
assert select_profiles({"work_type":"skill_evolution"},profiles)==["eval_driven_evolution"]
assert "discovery_spike" in select_profiles({"work_type":"development","technical_uncertainty":"high"},profiles)
assert "stage_gated" in select_profiles({"work_type":"development","safety":"high"},profiles)
assert classify_failure({"failed_mechanism":"grader"})=="verification_system"
assert classify_failure({"failed_mechanism":"component_interface"})=="design"
assert classify_failure({"failed_mechanism":"state_authority"})=="architect"
plan=create_plan("W1",["iterative_incremental"],"a"*64,[{"task_id":"T1","owner":"architecture-review","dependencies":[],"outputs":["architecture"],"risk_class":"medium","review_level":"L2_SINGLE_FAMILY_QUAD"}])
changed=replan(plan,{"kind":"authority_boundary_changed","evidence_hash":"b"*64},{"risk_class":"high"},{"invalidate":["T1"],"reuse":[]})
assert changed["revision"]==2 and changed["tasks_invalidated"]==["T1"] and changed["required_review_level"]=="L1_CROSS_FAMILY_2X2"
with tempfile.TemporaryDirectory() as name:
    path=Path(name)/"state.json"
    state={"schema_version":1,"work_id":"W1","revision":0,"plan_id":plan["plan_id"],"plan_revision":1,"status":"interrupted","stage":"verify","profiles":["iterative_incremental"],"authority":{"approved_actions":["inspect"]},"current_action":{"action_id":"A1","deduplication_key":"push:one","plan_revision":1,"authority_scope":["inspect"],"attempt":1,"max_attempts":2,"state":"uncertain"},"review":{},"budgets":{"provider_calls":0}}
    saved=save_state_atomic(path,state,0)
    assert saved["revision"]==1 and load_state(path)["revision"]==1
    durable=[]
    original_sync=lifecycle_state_store._fsync_directory
    lifecycle_state_store._fsync_directory=lambda directory: durable.append(directory)
    save_state_atomic(Path(name)/"durable.json",state,0)
    lifecycle_state_store._fsync_directory=original_sync
    assert durable==[Path(name)]
    try: save_state_atomic(path,state,0)
    except ValueError: pass
    else: raise AssertionError("stale revision accepted")
    leased=acquire_lease(saved,"owner-a",100,30)
    newer=acquire_lease(leased,"owner-b",131,30)
    try: assert_fence(newer,"owner-a",leased["lease"]["fencing_token"])
    except ValueError: pass
    else: raise AssertionError("stale owner accepted")
    save_state_atomic(path,newer,1,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"],now=131)
    try: save_state_atomic(path,newer,2,owner_id="owner-a",fencing_token=leased["lease"]["fencing_token"])
    except ValueError: pass
    else: raise AssertionError("persistence boundary accepted stale fence")
    over_authorized={**newer,"authority":{"approved_actions":["inspect"]},"current_action":{**newer["current_action"],"authority_scope":["inspect","publish"]}}
    try: save_state_atomic(path,over_authorized,2,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    except ValueError as exc: assert "authority" in str(exc)
    else: raise AssertionError("persistence boundary accepted expanded authority")
    assert reconcile_action(newer,lambda action:{"state":"completed"})=="ALREADY_COMPLETED"
    assert reconcile_action(newer,lambda action:{"state":"unknown"})=="RECONCILIATION_REQUIRED"
    cancelled=cancel_work(newer,"user pivot",lambda action:{"state":"completed"})
    assert cancelled["status"]=="paused" and cancelled["current_action"] is None and cancelled["completed_steps"][-1]["deduplication_key"]=="push:one"
    missing_revision={**newer,"current_action":{key:value for key,value in newer["current_action"].items() if key!="plan_revision"}}
    assert reconcile_action(missing_revision,lambda action:{"state":"completed"})=="STALE_BASELINE"
budgeted=consume_budget({"status":"active","budgets":{"tokens":{"limit":10,"used":8}}},"tokens",3)
assert budgeted["status"]=="paused" and budgeted["budgets"]["tokens"]["used"]==8 and budgeted["budget_rejection"]["amount"]==3
review=plan_review({"review":{"required_level":"L3_SINGLE_FAMILY_PAIR"},"budgets":{"provider_calls":{"limit":2,"used":0}}},{"workers":[],"blocking_findings":[]})
assert len(review["next_cells"])==2 and review["achieved_level"]=="L0_NONE"
assert deployment_decision({"status":"deployed"},{"observation_complete":False})=="HOLD"
assert deployment_decision({"status":"observing"},{"observation_complete":True,"hard_gate_breached":True})=="ROLLBACK"
assert deployment_decision({"status":"observing"},{"observation_complete":True,"hard_gate_breached":False})=="ADVANCE"
print("Validated composable planning, risk replan, durable state, fencing, and interruption reconciliation")
