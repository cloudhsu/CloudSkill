#!/usr/bin/env python3
from pathlib import Path
import copy,hashlib,json,sys,tempfile
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
assert plan=={
    "schema_version":1,
    "plan_id":"PLAN-"+hashlib.sha256(("W1"+"a"*64).encode()).hexdigest()[:12],
    "revision":1,
    "based_on_revision":None,
    "work_id":"W1",
    "profiles":["iterative_incremental"],
    "source_hash":"a"*64,
    "risk_baseline":{},
    "tasks":tasks,
    "tasks_added":["T1"],
    "tasks_removed":[],
    "tasks_invalidated":[],
    "evidence_reused":[],
    "authority_required":[],
    "required_review_level":"L2_SINGLE_FAMILY_QUAD",
}
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
template_risk={"risk_class":"medium","scope":"bounded","assessment_complete":False,"review_required":True}
resolution=compose_templates(
    "bounded-feature",
    ["skill-evolution"],
    template_facts,
    compatible_registry,
    work_id="W2",
    source_hash="c"*64,
    tasks=tasks,
    risk_context=template_risk,
)
composer_integrity_hash=resolution.get("resolution_integrity_hash")
assert isinstance(composer_integrity_hash,str) and len(composer_integrity_hash)==64
try:
    templated_plan=create_plan(
        "W2",
        ["eval_driven_evolution"],
        "c"*64,
        tasks,
        resolution,
        compatible_registry,
        template_facts,
        template_risk,
    )
except TypeError as exc:
    raise AssertionError("template plan admission does not accept authoritative task/risk context") from exc
expected_registry_identity={
    "schema_version":1,
    "sha256":hashlib.sha256(json.dumps(compatible_registry,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest(),
}
expected_selection_context={
    "work_id":"W2",
    "source_hash":"c"*64,
    "tasks":tasks,
    "task_facts":template_facts,
    "risk_context":template_risk,
    "registry_identity":expected_registry_identity,
}
expected_selection_context_hash=hashlib.sha256(json.dumps(expected_selection_context,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
assert templated_plan["template_resolution"]=={
    "status":"selected",
    "template_ids":["bounded-feature","skill-evolution"],
    "contract_versions":{"bounded-feature":1,"skill-evolution":1},
    "delta_evidence_hash":resolution["delta_evidence_hash"],
    "composition_order":["bounded-feature","skill-evolution"],
    "resolved_review_level":"L2_SINGLE_FAMILY_QUAD",
    "selection_context":expected_selection_context,
    "selection_context_hash":expected_selection_context_hash,
    "resolution_schema_version":2,
    "resolution_provenance":"lifecycle_template_contract.compose_templates",
    "composer_resolution_integrity_hash":composer_integrity_hash,
    "plan_revision":1,
    "full_risk_calculation_required":False,
    "plan_resolution_integrity_hash":templated_plan["template_resolution"]["plan_resolution_integrity_hash"],
}
assert templated_plan["template_resolution_lineage"]==[]
assert templated_plan["required_review_level"]=="L2_SINGLE_FAMILY_QUAD"
assert templated_plan["risk_baseline"]==template_risk
context_reuse_cases=(
    ("cross-work", "W-other", "c"*64, tasks, template_facts, template_risk, compatible_registry),
    ("cross-source", "W2", "d"*64, tasks, template_facts, template_risk, compatible_registry),
    ("cross-task", "W2", "c"*64, [{**tasks[0],"outputs":["different"]}], template_facts, template_risk, compatible_registry),
    ("cross-facts", "W2", "c"*64, tasks, {**template_facts,"requirement_revision":2}, template_risk, compatible_registry),
    ("cross-facts-bool-int", "W2", "c"*64, tasks, {**template_facts,"external_side_effect":0}, template_risk, compatible_registry),
    ("cross-facts-bool-int-true", "W2", "c"*64, tasks, {**template_facts,"design_approved":1}, template_risk, compatible_registry),
    ("cross-risk", "W2", "c"*64, tasks, template_facts, {**template_risk,"risk_class":"high"}, compatible_registry),
    ("cross-risk-bool-int", "W2", "c"*64, tasks, template_facts, {**template_risk,"assessment_complete":0}, compatible_registry),
    ("cross-risk-bool-int-true", "W2", "c"*64, tasks, template_facts, {**template_risk,"review_required":1}, compatible_registry),
)
for label,work_id,source_hash,candidate_tasks,candidate_facts,candidate_risk,candidate_registry in context_reuse_cases:
    try:
        create_plan(work_id,["eval_driven_evolution"],source_hash,candidate_tasks,resolution,candidate_registry,candidate_facts,candidate_risk)
    except ValueError as exc:
        assert "work/source/task/risk" in str(exc) or "composer-selected" in str(exc)
    else:
        raise AssertionError(f"{label} selected-resolution reuse accepted")
drifted_registry=copy.deepcopy(compatible_registry)
drifted_registry["templates"]["release"]["deferred_reason"]="A different authoritative registry revision."
try:
    create_plan("W2",["eval_driven_evolution"],"c"*64,tasks,resolution,drifted_registry,template_facts,template_risk)
except ValueError as exc:
    assert "authoritative registry" in str(exc) or "composer-selected" in str(exc)
else:
    raise AssertionError("cross-registry selected-resolution reuse accepted")

forged_context_resolution=copy.deepcopy(resolution)
forged_context_resolution["selection_context"]["work_id"]="W-forged-replay"
forged_context_resolution["selection_context_hash"]=hashlib.sha256(json.dumps(forged_context_resolution["selection_context"],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
forged_delta_evidence={
    "composition_order":forged_context_resolution["composition_order"],
    "contract_versions":forged_context_resolution["contract_versions"],
    "selection_context":forged_context_resolution["selection_context"],
    "templates":{
        template_id:{
            "matched_conditions":assessment["matched_conditions"],
            "matched_exclusions":assessment["matched_exclusions"],
            "exclusion_answers":assessment["exclusion_answers"],
            "delta_answers":assessment["delta_answers"],
        }
        for template_id,assessment in forged_context_resolution["assessments"].items()
    },
}
forged_context_resolution["delta_evidence_hash"]=hashlib.sha256(json.dumps(forged_delta_evidence,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
forged_context_payload={key:value for key,value in forged_context_resolution.items() if key!="resolution_integrity_hash"}
forged_context_resolution["resolution_integrity_hash"]=hashlib.sha256(json.dumps(forged_context_payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
try:
    create_plan("W2",["eval_driven_evolution"],"c"*64,tasks,forged_context_resolution,compatible_registry,template_facts,template_risk)
except ValueError as exc:
    assert "work/source/task/risk" in str(exc) or "composer-selected" in str(exc)
else:
    raise AssertionError("caller-resealed cross-work replay accepted")
stronger_registry=copy.deepcopy(compatible_registry)
stronger_registry["templates"]["bounded-feature"]["review_level"]="L1_CROSS_FAMILY_2X2"
stronger_resolution=compose_templates(
    "bounded-feature",
    ["skill-evolution"],
    template_facts,
    stronger_registry,
    work_id="W3",
    source_hash="f"*64,
    tasks=tasks,
    risk_context=template_risk,
)
stronger_plan=create_plan("W3",["eval_driven_evolution"],"f"*64,tasks,stronger_resolution,stronger_registry,template_facts,template_risk)
assert stronger_plan["required_review_level"]=="L1_CROSS_FAMILY_2X2"
hand_built={
    "status":"selected",
    "template_ids":["bounded-feature"],
    "contract_versions":{"bounded-feature":1},
    "delta_evidence_hash":"0"*64,
    "composition_order":["bounded-feature"],
    "resolved_review_level":"L2_SINGLE_FAMILY_QUAD",
    "full_risk_calculation_required":False,
}
deferred_relabel=compose_templates("release",[],template_facts,template_registry)
deferred_relabel.update(hand_built)
tampered_resolution=copy.deepcopy(resolution)
tampered_resolution["delta_evidence_hash"]="0"*64
for invalid_selected in (hand_built,deferred_relabel,tampered_resolution):
    try: create_plan("W-forged",["iterative_incremental"],"0"*64,tasks,invalid_selected,compatible_registry,template_facts,template_risk)
    except ValueError as exc: assert "composer-selected" in str(exc)
    else: raise AssertionError("non-composer or integrity-invalid selected resolution accepted")
forged_resealed=copy.deepcopy(resolution)
forged_assessment=copy.deepcopy(next(iter(forged_resealed["assessments"].values())))
forged_assessment["template_id"]="release"
forged_assessment["contract_version"]=1
forged_resealed["template_ids"]=["release"]
forged_resealed["composition_order"]=["release"]
forged_resealed["contract_versions"]={"release":1}
forged_resealed["assessments"]={"release":forged_assessment}
forged_payload={key:value for key,value in forged_resealed.items() if key!="resolution_integrity_hash"}
forged_resealed["resolution_integrity_hash"]=hashlib.sha256(json.dumps(forged_payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
try: create_plan("W-resealed-forge",["iterative_incremental"],"4"*64,tasks,forged_resealed,template_registry,template_facts,template_risk)
except ValueError as exc: assert "authoritative registry" in str(exc)
else: raise AssertionError("resealed deferred-template forgery accepted")
for rejected_resolution in (
    compose_templates("release",[],template_facts,template_registry),
    compose_templates("bounded-feature",[],{**template_facts,"outside_verified_envelope":True},template_registry),
    compose_templates("bounded-feature",["skill-evolution"],template_facts,template_registry),
):
    try: create_plan("W-rejected",["iterative_incremental"],"d"*64,tasks,rejected_resolution,template_registry,template_facts,template_risk)
    except ValueError as exc: assert "selected template resolution" in str(exc)
    else: raise AssertionError("non-selected template resolution accepted as plan input")
changed=replan(plan,{"kind":"authority_boundary_changed","evidence_hash":"b"*64},{"risk_class":"high"},{"invalidate":["T1"],"reuse":[]})
assert changed["revision"]==2 and changed["tasks_invalidated"]==["T1"] and changed["required_review_level"]=="L1_CROSS_FAMILY_2X2"
unrelated_changed=replan(templated_plan,{"kind":"test_report_changed","evidence_hash":"5"*64},template_risk,{"invalidate":[],"invalidate_evidence":["unrelated:test-report"],"reuse":["approved design"]})
assert unrelated_changed["template_resolution"]["status"]=="selected"
assert unrelated_changed["template_resolution"]["delta_evidence_hash"]==resolution["delta_evidence_hash"]
template_changed=replan(templated_plan,{"kind":"source_changed","evidence_hash":"e"*64},template_risk,{"invalidate":["T1"],"reuse":["approved design","approved design"]})
assert template_changed["template_resolution_lineage"]==[templated_plan["template_resolution"]]
assert template_changed["source_hash"]=="e"*64
assert template_changed["template_resolution"]["plan_revision"]==2
assert template_changed["template_resolution"]["status"]=="escalation_required"
assert template_changed["template_resolution"]["full_risk_calculation_required"] is True
assert template_changed["template_resolution"]["delta_evidence_hash"] is None
assert template_changed["template_resolution"]["composer_resolution_integrity_hash"] is None
assert template_changed["evidence_invalidated"]==[resolution["delta_evidence_hash"]]
assert template_changed["evidence_reused"]==["approved design"]
still_unresolved=replan(template_changed,{"kind":"scope_rechecked","evidence_hash":"3"*64},template_risk,{"invalidate":[],"reuse":["approved design"]})
assert still_unresolved["template_resolution"]["status"]=="escalation_required"
assert still_unresolved["template_resolution"]["plan_revision"]==3
assert still_unresolved["template_resolution"]["delta_evidence_hash"] is None
assert still_unresolved["template_resolution_lineage"]==[
    templated_plan["template_resolution"],
    template_changed["template_resolution"],
]
replacement_facts={key:value for key,value in template_facts.items() if key not in overlay_template["applicability"] and key not in overlay_template["exclusion_facts"]}
replacement=compose_templates(
    "bounded-feature",
    [],
    replacement_facts,
    template_registry,
    work_id="W2",
    source_hash="e"*64,
    tasks=tasks,
    risk_context=template_risk,
)
reselected=replan(template_changed,{"kind":"scope_rechecked","evidence_hash":"1"*64},template_risk,{"invalidate":["T1"],"invalidate_evidence":[],"reuse":[]},replacement,template_registry,replacement_facts)
assert reselected["template_resolution"]["status"]=="selected"
assert reselected["template_resolution"]["plan_revision"]==3
assert reselected["template_resolution"]["delta_evidence_hash"]==replacement["delta_evidence_hash"]
assert reselected["template_resolution_lineage"]==[
    templated_plan["template_resolution"],
    template_changed["template_resolution"],
]
for trigger in (
    {"kind":"authority_boundary_changed","evidence_hash":"6"*64},
    {"kind":"side_effect_scope_changed","evidence_hash":"7"*64},
    {"kind":"requirement_changed","evidence_hash":"8"*64,"delta_changes":{"sensitive_or_privileged":True}},
):
    automatically_unresolved=replan(templated_plan,trigger,template_risk,{"invalidate":[],"reuse":[]})
    assert automatically_unresolved["template_resolution"]["status"]=="escalation_required"
    assert automatically_unresolved["template_resolution"]["full_risk_calculation_required"] is True
    assert automatically_unresolved["evidence_invalidated"]==[resolution["delta_evidence_hash"]]
safe_delta_trigger=replan(templated_plan,{"kind":"requirement_checked","evidence_hash":"9"*64,"delta_changes":{"sensitive_or_privileged":False}},template_risk,{"invalidate":[],"reuse":[]})
assert safe_delta_trigger["template_resolution"]["status"]=="selected"
for label, changed_facts, changed_risk in (
    ("fact false-to-zero", {**template_facts,"external_side_effect":0}, template_risk),
    ("fact true-to-one", {**template_facts,"design_approved":1}, template_risk),
    ("risk false-to-zero", template_facts, {**template_risk,"assessment_complete":0}),
    ("risk true-to-one", template_facts, {**template_risk,"review_required":1}),
):
    typed_change=replan(
        templated_plan,
        {"kind":"context_rechecked","evidence_hash":"d"*64},
        changed_risk,
        {"invalidate":[],"reuse":[]},
        template_facts=changed_facts,
    )
    assert typed_change["template_resolution"]["status"]=="escalation_required", label
    assert typed_change["evidence_invalidated"]==[resolution["delta_evidence_hash"]], label
risk_changed=replan(templated_plan,{"kind":"risk_changed","evidence_hash":"a"*64},{**template_risk,"risk_class":"high"},{"invalidate":[],"reuse":[]})
assert risk_changed["template_resolution"]["status"]=="escalation_required"
try:
    replan(
        templated_plan,
        {"kind":"authority_boundary_changed","evidence_hash":"a"*64},
        template_risk,
        {"invalidate":[],"reuse":[]},
        resolution,
        compatible_registry,
        template_facts,
    )
except ValueError as exc:
    assert "fresh" in str(exc) and "new context" in str(exc)
else:
    raise AssertionError("invalidating trigger accepted replay of the prior selected resolution")
fresh_risk={**template_risk,"risk_class":"high","assessment_revision":2}
fresh_resolution=compose_templates(
    "bounded-feature",
    ["skill-evolution"],
    template_facts,
    compatible_registry,
    work_id="W2",
    source_hash="c"*64,
    tasks=tasks,
    risk_context=fresh_risk,
)
freshly_reselected=replan(
    templated_plan,
    {"kind":"authority_boundary_changed","evidence_hash":"a"*64},
    fresh_risk,
    {"invalidate":[],"reuse":[]},
    fresh_resolution,
    compatible_registry,
    template_facts,
)
assert freshly_reselected["template_resolution"]["status"]=="selected"
assert freshly_reselected["template_resolution"]["selection_context"]["risk_context"]==fresh_risk
assert freshly_reselected["template_resolution"]["delta_evidence_hash"]==fresh_resolution["delta_evidence_hash"]
assert freshly_reselected["evidence_invalidated"]==[resolution["delta_evidence_hash"]]
try: replan(templated_plan,{"kind":"source_changed","evidence_hash":"f"*64},{"risk_class":"medium"},{"invalidate":[],"invalidate_evidence":[resolution["delta_evidence_hash"]],"reuse":[resolution["delta_evidence_hash"]]})
except ValueError as exc: assert "invalidated and reused" in str(exc)
else: raise AssertionError("replan reused invalidated evidence")
for malformed_plan in (
    {**templated_plan,"template_resolution_lineage":{}},
    {**templated_plan,"template_resolution_lineage":[templated_plan["template_resolution"]]},
    {**templated_plan,"template_resolution":{**templated_plan["template_resolution"],"plan_revision":9}},
    {**templated_plan,"work_id":"W-other"},
    {**templated_plan,"source_hash":"d"*64},
    {**templated_plan,"tasks":[{**tasks[0],"outputs":["different"]}]},
    {**templated_plan,"risk_baseline":{**template_risk,"risk_class":"high"}},
    {**templated_plan,"revision":"1"},
    {**plan,"template_resolution_lineage":[]},
    {**template_changed,"template_resolution_lineage":[]},
):
    try: replan(malformed_plan,{"kind":"source_changed","evidence_hash":"2"*64},{"risk_class":"medium"},{"invalidate":[],"reuse":[]})
    except ValueError as exc: assert "template resolution lineage" in str(exc)
    else: raise AssertionError("malformed or unordered template resolution lineage accepted")
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
