#!/usr/bin/env python3
from pathlib import Path
import copy,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from lifecycle_orchestration_contract import classify_failure, deployment_decision, load_profiles, select_profiles
from lifecycle_plan_contract import create_plan, replan
from lifecycle_template_contract import compose_templates, load_templates
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
tasks=[{"task_id":"T1","owner":"architecture-review","dependencies":[],"outputs":["architecture"],"risk_class":"medium","review_level":"L2_SINGLE_FAMILY_QUAD"}]
plan=create_plan("W1",["iterative_incremental"],"a"*64,tasks)
assert "template_resolution" not in plan and "template_resolution_lineage" not in plan
template_registry=load_templates(ROOT/"config/lifecycle-templates.json")
compatible_registry=copy.deepcopy(template_registry)
base_template=compatible_registry["templates"]["bounded-feature"]
overlay_template=compatible_registry["templates"]["skill-evolution"]
overlay_template["owners"]=copy.deepcopy(base_template["owners"])
for gate in overlay_template["gates"]: gate["owner"]=base_template["owners"]["policy"]
template_facts={
    **base_template["applicability"],
    **overlay_template["applicability"],
    **{field:False for field in base_template["exclusion_facts"]},
    **{field:False for field in overlay_template["exclusion_facts"]},
    "external_side_effect":False,
    "authority_or_state":False,
    "sensitive_or_privileged":False,
    "platform_or_compatibility":False,
    "irreversible_or_unreconciled":False,
    "outside_verified_envelope":False,
}
resolution=compose_templates("bounded-feature",["skill-evolution"],template_facts,compatible_registry)
templated_plan=create_plan("W2",["eval_driven_evolution"],"c"*64,tasks,resolution)
assert templated_plan["template_resolution"]=={
    "status":"selected",
    "template_ids":["bounded-feature","skill-evolution"],
    "contract_versions":{"bounded-feature":1,"skill-evolution":1},
    "delta_evidence_hash":resolution["delta_evidence_hash"],
    "composition_order":["bounded-feature","skill-evolution"],
    "resolved_review_level":"L2_SINGLE_FAMILY_QUAD",
    "plan_revision":1,
}
assert templated_plan["template_resolution_lineage"]==[]
assert templated_plan["required_review_level"]=="L2_SINGLE_FAMILY_QUAD"
stronger_resolution={**resolution,"resolved_review_level":"L1_CROSS_FAMILY_2X2"}
stronger_plan=create_plan("W3",["eval_driven_evolution"],"f"*64,tasks,stronger_resolution)
assert stronger_plan["required_review_level"]=="L1_CROSS_FAMILY_2X2"
for rejected_resolution in (
    compose_templates("release",[],template_facts,template_registry),
    compose_templates("bounded-feature",[],{**template_facts,"outside_verified_envelope":True},template_registry),
    compose_templates("bounded-feature",["skill-evolution"],template_facts,template_registry),
):
    try: create_plan("W-rejected",["iterative_incremental"],"d"*64,tasks,rejected_resolution)
    except ValueError as exc: assert "selected template resolution" in str(exc)
    else: raise AssertionError("non-selected template resolution accepted as plan input")
changed=replan(plan,{"kind":"authority_boundary_changed","evidence_hash":"b"*64},{"risk_class":"high"},{"invalidate":["T1"],"reuse":[]})
assert changed["revision"]==2 and changed["tasks_invalidated"]==["T1"] and changed["required_review_level"]=="L1_CROSS_FAMILY_2X2"
template_changed=replan(templated_plan,{"kind":"source_changed","evidence_hash":"e"*64},{"risk_class":"medium"},{"invalidate":["T1"],"invalidate_evidence":["delta evidence"],"reuse":["approved design","approved design"]})
assert template_changed["template_resolution_lineage"]==[templated_plan["template_resolution"]]
assert template_changed["template_resolution"]["plan_revision"]==2
assert template_changed["evidence_invalidated"]==["delta evidence"]
assert template_changed["evidence_reused"]==["approved design"]
try: replan(templated_plan,{"kind":"source_changed","evidence_hash":"f"*64},{"risk_class":"medium"},{"invalidate":[],"invalidate_evidence":["delta evidence"],"reuse":["delta evidence"]})
except ValueError as exc: assert "invalidated and reused" in str(exc)
else: raise AssertionError("replan reused invalidated evidence")
with tempfile.TemporaryDirectory() as name:
    path=Path(name)/"state.json"
    state={"schema_version":1,"work_id":"W1","revision":0,"plan_id":plan["plan_id"],"plan_revision":1,"status":"interrupted","stage":"verify","profiles":["iterative_incremental"],"authority":{"approved_actions":["inspect"]},"current_action":{"action_id":"A1","deduplication_key":"push:one","plan_revision":1,"authority_scope":["inspect"],"attempt":1,"max_attempts":2,"state":"uncertain"},"review":{},"budgets":{"provider_calls":{"limit":2,"used":0}}}
    saved=save_state_atomic(path,state,0)
    assert saved["revision"]==1 and load_state(path)["revision"]==1
    durable=[]
    original_sync=lifecycle_state_store._fsync_directory
    lifecycle_state_store._fsync_directory=lambda directory: durable.append(directory)
    save_state_atomic(Path(name)/"durable.json",state,0)
    lifecycle_state_store._fsync_directory=original_sync
    assert durable==[Path(name)]
    legacy_path=Path(name)/"legacy-grant.json"
    legacy={**saved,"authority":{"approved_actions":["inspect","publish"],"grant":{"authorizer":"user","authorized_at":"2026-08-11T00:00:00Z","source_hash":"a"*64,"plan_revision":1,"added_actions":["publish"]}},"current_action":None}
    legacy_path.write_text(json.dumps(legacy),encoding="utf-8")
    migrated=load_state(legacy_path)
    assert "grant" not in migrated["authority"] and len(migrated["authority"]["grants"])==1
    migrated["authority"]["approved_actions"]=["inspect"]
    migrated=save_state_atomic(legacy_path,migrated,1)
    assert len(migrated["authority"]["grants"])==1
    ambiguous={**migrated,"authority":{**migrated["authority"],"grant":migrated["authority"]["grants"][0]}}
    try: save_state_atomic(legacy_path,ambiguous,2)
    except ValueError as exc: assert "ambiguous" in str(exc)
    else: raise AssertionError("ambiguous grant shape was persisted")
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
    widened={**newer,"authority":{"approved_actions":["inspect","publish"]},"current_action":{**newer["current_action"],"authority_scope":["publish"]}}
    try: save_state_atomic(path,widened,2,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    except ValueError as exc: assert "authority" in str(exc)
    else: raise AssertionError("resumed writer widened its own authority")
    prohibited={**newer,"authority":{"approved_actions":["inspect"],"prohibited_actions":["inspect"]}}
    try: save_state_atomic(path,prohibited,2,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    except ValueError as exc: assert "prohibited" in str(exc)
    else: raise AssertionError("explicitly prohibited action was accepted")
    exhausted={**newer,"current_action":{**newer["current_action"],"attempt":3,"max_attempts":2}}
    try: save_state_atomic(path,exhausted,2,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    except ValueError as exc: assert "attempt" in str(exc)
    else: raise AssertionError("exhausted retry state was accepted")
    grant={"authorizer":"user","authorized_at":"2026-08-11T00:00:00Z","source_hash":"a"*64,"plan_revision":1,"added_actions":["publish"]}
    granted={**widened,"authority":{**widened["authority"],"grants":[grant]}}
    granted_saved=save_state_atomic(path,granted,2,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    assert "publish" in granted_saved["authority"]["approved_actions"]
    dropped_grant={**granted_saved,"authority":{key:value for key,value in granted_saved["authority"].items() if key!="grants"}}
    try: save_state_atomic(path,dropped_grant,3,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    except ValueError as exc: assert "grant" in str(exc)
    else: raise AssertionError("durable authority grant evidence was dropped")
    preserved_grant=save_state_atomic(path,granted_saved,3,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    assert preserved_grant["authority"]["grants"]==[grant]
    grant2={"authorizer":"user","authorized_at":"2026-08-11T00:10:00Z","source_hash":"b"*64,"plan_revision":1,"added_actions":["deploy"]}
    expanded_again={**preserved_grant,"authority":{**preserved_grant["authority"],"approved_actions":["inspect","publish","deploy"],"grants":[grant,grant2]}}
    expanded_again=save_state_atomic(path,expanded_again,4,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    assert expanded_again["authority"]["grants"]==[grant,grant2]
    revoked={**expanded_again,"current_action":None,"authority":{**expanded_again["authority"],"approved_actions":["inspect"]}}
    revoked=save_state_atomic(path,revoked,5,owner_id="owner-b",fencing_token=newer["lease"]["fencing_token"])
    assert revoked["authority"]["grants"]==[grant,grant2]
    assert reconcile_action(newer,lambda action:{"state":"completed"})=="ALREADY_COMPLETED"
    assert reconcile_action(newer,lambda action:{"state":"unknown"})=="RECONCILIATION_REQUIRED"
    at_limit={**newer,"current_action":{**newer["current_action"],"attempt":2,"max_attempts":2}}
    assert reconcile_action(at_limit,lambda action:{"state":"failed"})=="ATTEMPTS_EXHAUSTED"
    cancelled=cancel_work(newer,"user pivot",lambda action:{"state":"completed"})
    assert cancelled["status"]=="paused" and cancelled["current_action"] is None and cancelled["completed_steps"][-1]["deduplication_key"]=="push:one"
    missing_revision={**newer,"current_action":{key:value for key,value in newer["current_action"].items() if key!="plan_revision"}}
    assert reconcile_action(missing_revision,lambda action:{"state":"completed"})=="STALE_BASELINE"
budgeted=consume_budget({"status":"active","budgets":{"tokens":{"limit":10,"used":8}}},"tokens",3)
assert budgeted["status"]=="paused" and budgeted["budgets"]["tokens"]["used"]==8 and budgeted["budget_rejection"]["amount"]==3
for invalid_amount in (-1,0,True,float("inf"),float("nan")):
    try: consume_budget({"status":"active","budgets":{"tokens":{"limit":10,"used":1}}},"tokens",invalid_amount)
    except ValueError: pass
    else: raise AssertionError("invalid budget amount accepted")
review=plan_review({"review":{"required_level":"L3_SINGLE_FAMILY_PAIR"},"budgets":{"provider_calls":{"limit":2,"used":0}}},{"workers":[],"blocking_findings":[]})
assert len(review["next_cells"])==2 and review["achieved_level"]=="L0_NONE"
assert review["evidence_reused"] is False
context={"review_scope":"release","source_hash":"1"*64,"contract_hash":"2"*64,"packet_hash":"3"*64,"rubric_hash":"4"*64,"risk_class":"high"}
stale={**context,"source_hash":"9"*64,"workers":[{"family":"gpt","canonical_model":"a","status":"PASS","model_identity_evidence":"provider_returned"}],"blocking_findings":[]}
review=plan_review({"review":{"required_level":"L0_SINGLE_REVIEW","evidence_context":context},"budgets":{"provider_calls":{"limit":1,"used":0}}},stale)
assert review["achieved_level"]=="L0_NONE" and review["evidence_reused"] is False and len(review["next_cells"])==1
fresh={**context,"workers":[{"family":"gpt","canonical_model":"a","status":"PASS","model_identity_evidence":"provider_returned"}],"blocking_findings":[]}
review=plan_review({"review":{"required_level":"L0_SINGLE_REVIEW","evidence_context":context},"budgets":{"provider_calls":{"limit":1,"used":0}}},fresh)
assert review["achieved_level"]=="L0_SINGLE_REVIEW" and review["evidence_reused"] is True
assert deployment_decision({"status":"deployed"},{"observation_complete":False})=="HOLD"
assert deployment_decision({"status":"observing"},{"observation_complete":True,"hard_gate_breached":True})=="ROLLBACK"
assert deployment_decision({"status":"observing"},{"observation_complete":True,"hard_gate_breached":False})=="ADVANCE"
print("Validated composable planning, risk replan, durable state, fencing, and interruption reconciliation")
