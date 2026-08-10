#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from review_assurance_contract import achieved_level, decide_review, evidence_applicable, load_review_policy, next_review_cells, required_level, validate_review_record

def w(family, model, status="PASS"):
    return {"family":family,"canonical_model":model,"status":status,"model_identity_evidence":"provider_returned" if status!="BLOCKED" else None}

assert achieved_level([])=="L0_NONE"
assert achieved_level([w("gpt","a")]*4)=="L0_SINGLE_REVIEW"
assert achieved_level([w("gpt","a"),w("gpt","b")])=="L3_SINGLE_FAMILY_PAIR"
assert achieved_level([w("gpt",x) for x in "abcd"])=="L2_SINGLE_FAMILY_QUAD"
assert achieved_level([w("gpt","a"),w("gpt","b"),w("claude","c"),w("claude","d")])=="L1_CROSS_FAMILY_2X2"
assert achieved_level([w("gpt","a"),w("gpt","b"),w("claude","c","BLOCKED"),w("claude","d","BLOCKED")])=="L3_SINGLE_FAMILY_PAIR"
policy=load_review_policy(ROOT/"config/review-assurance-policy.json")
assert required_level("architecture","high",policy)=="L1_CROSS_FAMILY_2X2"
assert required_level("document_governance","presentation_only",policy)=="L0_NONE"
blocked=decide_review("L1_CROSS_FAMILY_2X2","L0_SINGLE_REVIEW",[],None)
assert blocked["decision"]=="BLOCKED"
exception={"authorizer":"user","authorized_at":"2026-08-11T00:00:00Z","scope":"release","source_hash":"1"*64,"contract_hash":"2"*64,"packet_hash":"3"*64,"rubric_hash":"4"*64,"risk_class":"high","required_level":"L1_CROSS_FAMILY_2X2","achieved_level":"L0_SINGLE_REVIEW","remaining_risk":"single-family evidence only"}
assert decide_review("L1_CROSS_FAMILY_2X2","L0_SINGLE_REVIEW",[],exception,evidence_context={**exception,"review_scope":"release"})["decision"]=="PASS_WITH_EXCEPTION"
assert decide_review("L3_SINGLE_FAMILY_PAIR","L2_SINGLE_FAMILY_QUAD",[{"severity":"High"}],None)["decision"]=="BLOCKED"
record={"source_hash":"1"*64,"contract_hash":"2"*64,"packet_hash":"3"*64,"rubric_hash":"4"*64,"risk_class":"low","workers":[w("gpt","a")]}
assert evidence_applicable(record,source_hash="1"*64,contract_hash="2"*64,packet_hash="3"*64,rubric_hash="4"*64,risk_class="low")
assert not evidence_applicable(record,source_hash="9"*64,contract_hash="2"*64,packet_hash="3"*64,rubric_hash="4"*64,risk_class="low")
assert next_review_cells({"workers":[],"blocking_findings":[]}, "L0_NONE", {"provider_calls":0})==[]
assert next_review_cells({"workers":[],"blocking_findings":[{"severity":"High"}]}, "L1_CROSS_FAMILY_2X2", {"provider_calls":4})==[]
same_family={"workers":[w("gpt",name) for name in "abcd"],"blocking_findings":[]}
assert len(next_review_cells(same_family,"L1_CROSS_FAMILY_2X2",{"provider_calls":4}))==2
persisted={"schema_version":1,"review_id":"R1","review_scope":"release","risk_class":"high","required_level":"L1_CROSS_FAMILY_2X2","achieved_level":"L1_CROSS_FAMILY_2X2","decision":"PASS","source_hash":"1"*64,"contract_hash":"2"*64,"packet_hash":"3"*64,"rubric_hash":"4"*64,"workers":[w("gpt","a")],"blocking_findings":[],"exception":None}
assert "achieved_level does not match workers" in validate_review_record(persisted)
persisted["achieved_level"]="L0_SINGLE_REVIEW"
persisted["decision"]="BLOCKED"
assert validate_review_record(persisted)==[]
forged={**persisted,"decision":"PASS_WITH_EXCEPTION","exception":{**exception,"source_hash":"9"*64}}
assert "decision does not match review evidence" in validate_review_record(forged)
wrong_scope={**persisted,"decision":"PASS_WITH_EXCEPTION","exception":{**exception,"scope":"architecture"}}
assert "decision does not match review evidence" in validate_review_record(wrong_scope)
failed={**persisted,"workers":[w("gpt","a","FAIL")],"decision":"PASS"}
assert "decision does not match review evidence" in validate_review_record(failed)
print("Validated risk-based review assurance, degradation, evidence reuse, and token-aware scheduling")
