from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "runtime" / "cases" / "canary.json"
DEFAULT_SCHEMA = ROOT / "evals" / "runtime" / "schemas" / "routing-decision.schema.json"
MANIFEST = ROOT / "SKILL_MANIFEST.json"
VERSION_FILE = ROOT / "VERSION"
ROUTER_SKILL = "using-cloudskill"
ROUTER_SKILL_PATH = ROOT / ".agents" / "skills" / ROUTER_SKILL / "SKILL.md"
ROUTING_MAP_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / ROUTER_SKILL
    / "references"
    / "conversation-routing-map.md"
)
CONTEXT_MODES = ("none", "manifest", "router", "selected-skills")
ROUTING_CONTEXT_MODES = ("none", "manifest", "router")
EXPECTED_DECISION_KEYS = {
    "primary_skill",
    "supporting_skills",
    "rejected_skills",
    "execution_order",
    "reason",
    "confidence",
}


class ContextBudgetError(RuntimeError):
    """Raised when required prompt context cannot fit without unsafe truncation."""

    def __init__(self, message: str, evidence: dict[str, Any]):
        super().__init__(message)
        self.evidence = evidence


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(path: Path = DEFAULT_CASES) -> dict[str, Any]:
    return load_json(path)


def load_schema(path: Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    return load_json(path)


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    return load_json(path)


def skill_ids(manifest: dict[str, Any]) -> set[str]:
    return {item["name"] for item in manifest["skills"]}


def selected_skills(decision: dict[str, Any]) -> list[str]:
    primary = decision.get("primary_skill")
    supporting = decision.get("supporting_skills") or []
    return ([primary] if primary else []) + supporting


def estimate_tokens(text: str) -> int:
    """Conservative tokenizer-independent estimate for mixed English/CJK prompts."""

    return max(1, math.ceil(len(text.encode("utf-8")) / 4))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _file_evidence(
    *,
    path: Path,
    source_text: str,
    included_text: str,
    role: str,
    required: bool,
    included: bool = True,
    truncated: bool = False,
    reason: str | None = None,
) -> dict[str, Any]:
    return {
        "path": _relative(path),
        "role": role,
        "required": required,
        "included": included,
        "source_characters": len(source_text),
        "included_characters": len(included_text) if included else 0,
        "sha256": _sha256(source_text),
        "truncated": truncated,
        "reason": reason,
    }


def _read_required(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"required Runtime Eval context file is unavailable: {_relative(path)}: {exc}") from exc
    if not text.strip():
        raise RuntimeError(f"required Runtime Eval context file is empty: {_relative(path)}")
    return text


def _manifest_catalog(manifest: dict[str, Any], include_descriptions: bool) -> str:
    if include_descriptions:
        return "\n".join(
            f'- {item["name"]}: {item["description"]}' for item in manifest["skills"]
        )
    return "\n".join(f'- {item["name"]}' for item in manifest["skills"])



def _markdown_section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)"
    )
    match = pattern.search(text)
    if not match:
        return ""
    return f"## {heading}\n\n{match.group(1).strip()}\n"


def _character_ngrams(text: str, size: int = 2) -> set[str]:
    normalized = re.sub(r"\s+", "", text.casefold())
    normalized = re.sub(r"[^\w\u3400-\u9fff]", "", normalized)
    if len(normalized) < size:
        return {normalized} if normalized else set()
    return {normalized[index : index + size] for index in range(len(normalized) - size + 1)}


def _similarity(left: str, right: str) -> float:
    a = _character_ngrams(left)
    b = _character_ngrams(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# These concepts are used only to retrieve the most relevant routing-map rows.
# They do not make the routing decision; the model still receives the Router Skill,
# full catalog, JSON contract, and an explicit decision-boundary instruction.
_ROUTING_CONCEPT_PATTERNS: dict[str, tuple[str, ...]] = {
    "code-communication": (
        r"networkstream", r"buffer", r"dictionary", r"stale", r"callback",
        r"thread[- ]?safe", r"race condition", r"retry", r"retransmi", r"late response",
        r"重送", r"殘留", r"上一輪", r"執行緒", r"回呼", r"逾時",
    ),
    "state-modeling": (
        r"commanded", r"pending", r"actual", r"readback", r"desired",
        r"typed command", r"state semantics", r"狀態語意", r"狀態模型",
        r"實際狀態", r"命令狀態", r"讀回", r"late response",
    ),
    "equipment-architecture": (
        r"sequence", r"equipment service", r"shared (?:robot|resource)", r"interlock",
        r"pump", r"vent", r"material flow", r"chamber", r"ipc", r"failover",
        r"high availability", r"\bha\b", r"reconnect", r"restart recovery",
        r"共用資源", r"共享資源", r"腔體", r"斷線重連", r"故障切換", r"復原責任",
    ),
    "multi-audience-document": (
        r"management", r"executive", r"engineer", r"training", r"audience", r"report",
        r"raw data", r"source data", r"管理層", r"執行長", r"工程師", r"學習文件",
        r"訓練文件", r"原始資料", r"報告", r"多受眾",
    ),
    "version-metrics": (
        r"software version", r"versioned", r"unversioned", r"success rate", r"denominator",
        r"population", r"exclusion", r"update success", r"版本", r"無版本",
        r"成功率", r"分母", r"母體", r"排除", r"隔離", r"更新資料",
    ),
    "web-application": (
        r"\bweb\b", r"api", r"sqlite", r"rbac", r"nas", r"container", r"order",
        r"client/server", r"登入", r"下單", r"儲值", r"備份", r"手機版",
    ),
    "native-platform": (
        r"\bqt\b", r"\bmfc\b", r"hid", r"usb", r"firmware", r"installer",
        r"hot[- ]?plug", r"windows", r"macos", r"跨平台", r"韌體", r"安裝程式",
    ),
    "agent-product": (
        r"ai agent", r"autonomy", r"guardrail", r"memory", r"tool contract",
        r"approval", r"agentic", r"代理", r"工具呼叫", r"人工核准",
    ),
    "skill-development": (
        r"cloudbox", r"cloudskill", r"skill", r"eval", r"routing", r"plugin",
        r"repository", r"prior interaction", r"historical interaction", r"過去互動",
        r"歷史互動", r"技能優化", r"路由案例", r"覆蓋本機",
    ),
    "runtime-evaluation-engineering": (
        r"case validity", r"case ambiguity", r"rubric", r"grader", r"semantic judge",
        r"false positive", r"false negative", r"evaluation gate", r"release gate",
        r"評分規則", r"評分器", r"案例歧義", r"案例有效", r"發布門檻",
    ),
    "local-eval-debugging": (
        r"runtime eval", r"local eval", r"ollama", r"context budget", r"context overflow",
        r"missing report", r"missing jsonl", r"python 3\.1", r"review bundle", r"upload bundle",
        r"本機.*評分", r"本機.*eval", r"評分.*壓縮", r"找不到.*報告", r"結果.*上傳",
    ),
    "translation": (
        r"translate", r"translation", r"翻譯", r"譯成", r"翻成",
    ),
}



# Stable canonical rows prevent unrelated vocabulary in a new cue from displacing
# an established acceptance-case boundary. Add one marker when a new concept is added.
_ROUTING_CANONICAL_CUE_MARKERS: dict[str, str] = {
    "code-communication": "Duplicate command, stale response, NetworkStream/buffer suspicion",
    "state-modeling": "Valve/MFC/pump/gauge DTOs",
    "equipment-architecture": "Sequence versus Equipment Service",
    "multi-audience-document": "CEO/management versus engineer/training reports",
    "version-metrics": "Field failures or update success rates must correlate to an actual software version",
    "web-application": "Small web/client-server system",
    "native-platform": "Qt/MFC modernization",
    "agent-product": "AI Agent task contract",
    "skill-development": "AGENTS.md, coding-agent worktrees",
    "runtime-evaluation-engineering": "Executable Eval design or review",
    "local-eval-debugging": "Local Runtime Eval execution or diagnosis",
}


def _canonical_cue_rows(case_concepts: set[str], cue_rows: list[str]) -> list[str]:
    selected: list[str] = []
    for concept in sorted(case_concepts):
        marker = _ROUTING_CANONICAL_CUE_MARKERS.get(concept)
        if not marker:
            continue
        match = next((row for row in cue_rows if marker in row), None)
        if match is not None and match not in selected:
            selected.append(match)
    return selected


def _detected_routing_concepts(text: str) -> set[str]:
    lowered = text.casefold()
    return {
        concept
        for concept, patterns in _ROUTING_CONCEPT_PATTERNS.items()
        if any(re.search(pattern, lowered, re.I) for pattern in patterns)
    }


def _routing_row_score(case_prompt: str, row: str) -> tuple[float, int, str]:
    case_concepts = _detected_routing_concepts(case_prompt)
    row_concepts = _detected_routing_concepts(row)
    concept_overlap = len(case_concepts & row_concepts)
    # Concept overlap dominates retrieval. Character similarity is only a tie-breaker.
    score = concept_overlap * 10.0 + _similarity(case_prompt, row)
    return score, concept_overlap, row


def _table_rows(section: str) -> tuple[list[str], list[str]]:
    lines = [line for line in section.splitlines() if line.startswith("|")]
    if len(lines) < 3:
        return lines, []
    return lines[:2], lines[2:]


def extract_routing_reference(routing_map_text: str, case_prompt: str) -> str:
    """Select compact routing evidence by semantic pressure, not raw keyword similarity alone."""

    contract = _markdown_section(routing_map_text, "Routing contract")
    cues = _markdown_section(routing_map_text, "Reusable routing cues")
    counterexamples = _markdown_section(routing_map_text, "Language-neutral counterexamples")
    owner_order = _markdown_section(routing_map_text, "Owner versus execution order")

    cue_header, cue_rows = _table_rows(cues)
    counter_header, counter_rows = _table_rows(counterexamples)
    case_concepts = _detected_routing_concepts(case_prompt)

    ranked_cues = sorted(
        cue_rows,
        key=lambda row: _routing_row_score(case_prompt, row),
        reverse=True,
    )
    selected_cues = _canonical_cue_rows(case_concepts, cue_rows)
    cue_limit = max(2, min(4, len(case_concepts)))
    for row in ranked_cues:
        if len(selected_cues) >= cue_limit:
            break
        if row in selected_cues:
            continue
        if _routing_row_score(case_prompt, row)[1] <= 0:
            continue
        selected_cues.append(row)
        if len(selected_cues) >= cue_limit:
            break
    if not selected_cues:
        selected_cues = ranked_cues[:2]

    ranked_counterexamples = sorted(
        counter_rows,
        key=lambda row: _routing_row_score(case_prompt, row),
        reverse=True,
    )
    selected_counterexamples = [
        row for row in ranked_counterexamples if _routing_row_score(case_prompt, row)[1] > 0
    ][:1]
    if not selected_counterexamples and ranked_counterexamples:
        selected_counterexamples = ranked_counterexamples[:1]

    sections = ["# Conversation-derived routing map — selected excerpt", contract.rstrip()]
    if selected_cues:
        sections.append(
            "## Reusable routing cues — case-relevant excerpt\n\n"
            + "\n".join(cue_header + selected_cues)
        )
    if selected_counterexamples:
        sections.append(
            "## Language-neutral counterexamples — case-relevant excerpt\n\n"
            + "\n".join(counter_header + selected_counterexamples)
        )
    # Owner-versus-order is essential for metric/report work and skill-development work.
    if owner_order and (
        case_concepts & {"multi-audience-document", "version-metrics", "skill-development"}
        or _similarity(case_prompt, owner_order) >= 0.025
    ):
        sections.append(owner_order.rstrip())
    return "\n\n".join(section for section in sections if section).strip() + "\n"

def _routing_rules(compact: bool = False) -> str:
    if compact:
        return """Mandatory routing check:
- Output one JSON object only; route by decision/failure boundary, not language or isolated keywords.
- Pick the primary deliverable owner, then add every independent boundary that materially requires a supporting skill.
- When the explicit main deliverable is a component Commanded/Pending/Actual/Readback or ACK-versus-physical-completion contract, choose equipment-domain-modeling as primary. Add equipment-control-architecture for a separate cross-layer timeout, interlock, late-completion, shared-resource, or recovery-ownership deliverable; do not collapse that explicitly required second deliverable.
- When the component contract is already defined and the requested deliverable is Sequence/Equipment Service responsibility, shared-resource ownership, reconnect, restart, or failover, choose equipment-control-architecture as primary without equipment-domain-modeling.
- Do not add semiconductor-equipment-domain-knowledge merely because chamber, valve, transfer, or completion vocabulary appears; add it only when physical purpose, process meaning, readiness criteria, or completion evidence is actually unresolved.
- execution_order must contain the selected primary/supporting set exactly once and cannot be empty when primary_skill is not null.
- using-cloudskill is the router and must be absent downstream. Translation/simple rewriting/trivial work selects no skill.
"""
    return """Mandatory routing rules:
- Return exactly one JSON object matching the supplied schema. Do not add Markdown fences.
- Route by decision/failure boundary and requested deliverable, never by prompt language or isolated keywords.
- using-cloudskill is the router and MUST NOT appear in primary_skill or supporting_skills for ordinary downstream tasks.
- Translation, simple rewriting, trivial calculation, and inspection-only work require no downstream skill.
- Do not solve the engineering task during a Routing Eval.

Before returning JSON, perform this checklist:
1. Choose the one primary_skill that owns the requested deliverable or final decision.
   - A component Commanded/Pending/Actual/Readback, ACK-versus-physical-completion, or late-readback contract is owned by equipment-domain-modeling.
   - Sequence/Equipment Service responsibility, shared-resource ownership, reconnect, restart, failover, fencing, or recovery architecture is owned by equipment-control-architecture when the component contract is already defined.
2. Scan the task again for every independent decision boundary that materially changes the work; add only those as supporting_skills.
   - A separately required Sequence/Equipment Service timeout or recovery deliverable cannot be absorbed into the component state-contract owner.
   - Add equipment-control-architecture to a component-contract task when that separate cross-layer responsibility deliverable is explicitly requested.
   - Do not add semiconductor-equipment-domain-knowledge when physical purpose and completion evidence are explicitly supplied.
3. Build execution_order from the selected set: primary_skill plus supporting_skills, each exactly once. If primary_skill is not null, execution_order must not be empty.
4. Confirm rejected_skills does not overlap the selected set and using-cloudskill is absent downstream.

- The primary owner does not have to execute first when a supporting analysis establishes inputs first.
- confidence must be high, medium, or low.
"""

def _routing_system_prompt(
    *,
    context_mode: str,
    router_text: str | None,
    routing_map_text: str | None,
    catalog: str,
    schema_text: str,
) -> str:
    sections = [
        "You are executing a CloudBox Routing Eval. The supplied context is authoritative for this request.",
        _routing_rules(compact=context_mode == "router").rstrip(),
    ]
    if router_text is not None:
        sections.append(
            '<router-skill>\n'
            + router_text.rstrip()
            + "\n</router-skill>"
        )
    if routing_map_text is not None:
        sections.append(
            '<routing-reference>\n'
            + routing_map_text.rstrip()
            + "\n</routing-reference>"
        )
    catalog_label = "skill IDs only; diagnostic no-skill-context baseline" if context_mode == "none" else "skill IDs and descriptions"
    sections.append(f"<skill-catalog mode=\"{catalog_label}\">\n{catalog}\n</skill-catalog>")
    sections.append(
        "<json-schema>\n"
        + schema_text
        + "\n</json-schema>"
    )
    return "\n\n".join(sections).strip() + "\n"


def _routing_user_prompt(case: dict[str, Any]) -> str:
    return (
        f'Case ID: {case["id"]}\n\n'
        "User task:\n"
        f'{case["prompt"].strip()}\n\n'
        "Return the routing decision JSON only."
    )


def _finalize_prompt_evidence(
    *,
    mode: str,
    system_prompt: str,
    user_prompt: str,
    loaded_files: list[dict[str, Any]],
    num_ctx: int,
    reserve_output_tokens: int,
    truncated_files: list[str] | None = None,
    diagnostic_baseline: bool = False,
) -> dict[str, Any]:
    combined = system_prompt + "\n\n" + user_prompt
    estimated = estimate_tokens(combined)
    budget = num_ctx - reserve_output_tokens
    truncated_files = truncated_files or []
    evidence = {
        "mode": mode,
        "loaded_files": loaded_files,
        "system_prompt_characters": len(system_prompt),
        "user_prompt_characters": len(user_prompt),
        "prompt_characters": len(combined),
        "prompt_utf8_bytes": len(combined.encode("utf-8")),
        "estimated_tokens": estimated,
        "estimated_tokens_method": "ceil(utf8_bytes/4)",
        "num_ctx": num_ctx,
        "reserved_output_tokens": reserve_output_tokens,
        "input_budget_tokens": budget,
        "overflow_tokens": max(0, estimated - budget),
        "truncated": bool(truncated_files),
        "truncated_files": truncated_files,
        "prompt_sha256": _sha256(combined),
        "diagnostic_baseline": diagnostic_baseline,
    }
    return evidence


def build_routing_prompt(
    *,
    manifest: dict[str, Any],
    schema: dict[str, Any],
    case: dict[str, Any],
    context_mode: str,
    num_ctx: int,
    reserve_output_tokens: int,
    manifest_path: Path = MANIFEST,
    schema_path: Path = DEFAULT_SCHEMA,
    cases_path: Path = DEFAULT_CASES,
) -> dict[str, Any]:
    if context_mode not in ROUTING_CONTEXT_MODES:
        raise ValueError(
            f"routing prompt requires one of {ROUTING_CONTEXT_MODES}; got {context_mode!r}"
        )
    if reserve_output_tokens < 1 or reserve_output_tokens >= num_ctx:
        raise ValueError("reserve_output_tokens must be positive and smaller than num_ctx")

    manifest_source = json.dumps(manifest, ensure_ascii=False, indent=2)
    include_descriptions = context_mode in {"manifest", "router"}
    catalog = _manifest_catalog(manifest, include_descriptions=include_descriptions)
    schema_source = json.dumps(schema, ensure_ascii=False, indent=2)
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    case_source = json.dumps(case, ensure_ascii=False, indent=2)
    case_included = json.dumps(
        {"id": case["id"], "prompt": case["prompt"]},
        ensure_ascii=False,
        separators=(",", ":"),
    )

    router_text: str | None = None
    routing_map_text: str | None = None
    loaded_files: list[dict[str, Any]] = []
    if context_mode == "router":
        router_text = _read_required(ROUTER_SKILL_PATH)
        routing_map_source = _read_required(ROUTING_MAP_PATH)
        routing_map_text = extract_routing_reference(routing_map_source, case["prompt"])
        loaded_files.extend(
            [
                _file_evidence(
                    path=ROUTER_SKILL_PATH,
                    source_text=router_text,
                    included_text=router_text,
                    role="router-skill-full",
                    required=True,
                ),
                _file_evidence(
                    path=ROUTING_MAP_PATH,
                    source_text=routing_map_source,
                    included_text=routing_map_text,
                    role="routing-reference-case-excerpt",
                    required=True,
                    reason="full Routing contract plus deterministically selected case-relevant rows",
                ),
            ]
        )

    loaded_files.extend(
        [
            _file_evidence(
                path=manifest_path,
                source_text=manifest_source,
                included_text=catalog,
                role="skill-catalog-descriptions" if include_descriptions else "skill-catalog-ids-only",
                required=True,
            ),
            _file_evidence(
                path=schema_path,
                source_text=schema_source,
                included_text=schema_text,
                role="routing-json-schema",
                required=True,
            ),
            _file_evidence(
                path=cases_path,
                source_text=case_source,
                included_text=case_included,
                role=f'routing-case:{case["id"]}',
                required=True,
            ),
        ]
    )

    system_prompt = _routing_system_prompt(
        context_mode=context_mode,
        router_text=router_text,
        routing_map_text=routing_map_text,
        catalog=catalog,
        schema_text=schema_text,
    )
    user_prompt = _routing_user_prompt(case)
    evidence = _finalize_prompt_evidence(
        mode=context_mode,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        loaded_files=loaded_files,
        num_ctx=num_ctx,
        reserve_output_tokens=reserve_output_tokens,
        diagnostic_baseline=context_mode in {"none", "manifest"},
    )
    if evidence["overflow_tokens"]:
        raise ContextBudgetError(
            "required routing context exceeds the configured input budget; "
            "CloudBox refuses to truncate using-cloudskill/SKILL.md, the routing reference, "
            "the routing contract, schema, catalog, or current case. Increase --num-ctx or reduce "
            "--context-reserve-tokens.",
            evidence,
        )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt, "context": evidence}


def assert_router_context(bundle: dict[str, Any]) -> None:
    evidence = bundle.get("context") or {}
    loaded = {
        item.get("path"): item
        for item in evidence.get("loaded_files", [])
        if item.get("included")
    }
    router_rel = _relative(ROUTER_SKILL_PATH)
    route_map_rel = _relative(ROUTING_MAP_PATH)
    missing = [path for path in (router_rel, route_map_rel) if path not in loaded]
    if missing:
        raise RuntimeError(
            "router context is invalid because required files were not loaded: " + ", ".join(missing)
        )
    for path in (router_rel, route_map_rel):
        if loaded[path].get("truncated"):
            raise RuntimeError(f"router context is invalid because required file was truncated: {path}")
    system_prompt = bundle.get("system_prompt", "")
    for marker in (
        "Routing decision contract",
        "using-cloudskill is the router",
        "Prompt language alone is never a routing condition",
    ):
        if marker not in system_prompt:
            raise RuntimeError(f"router context is missing required contract marker: {marker}")


def _skill_entry_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["name"]: item for item in manifest["skills"]}


def discover_declared_references(skill_path: Path, skill_text: str) -> list[Path]:
    references: list[Path] = []
    seen: set[Path] = set()
    for match in re.finditer(r"(?:`|\$)?(references/[A-Za-z0-9_.\-/]+\.md)(?:`)?", skill_text):
        candidate = (skill_path.parent / match.group(1)).resolve()
        if candidate in seen or not candidate.is_file():
            continue
        seen.add(candidate)
        references.append(candidate)
    return references


def _behavior_system_prompt(
    *,
    decision: dict[str, Any],
    skill_sections: Iterable[tuple[str, str]],
    reference_sections: Iterable[tuple[str, str]],
) -> str:
    selected = selected_skills(decision)
    sections = [
        "Return the final engineering deliverable only.",
        "The first non-whitespace line must be <final> and the last non-whitespace line must be </final>. Write nothing before or after that block.",
        "Do not expose internal analysis, planning, chain-of-thought, self-instructions, Router decisions, Eval machinery, case IDs, skill IDs, file names, or source tags.",
        "Apply the supplied engineering instructions silently. Do not explain which instructions were selected.",
        "Preserve evidence honesty: distinguish provided facts, design assumptions, unresolved inputs, and verification that is proposed rather than already executed.",
        "Use concise task-relevant sections, explicit ownership, state transitions, rejection rules, recovery gates, and verification scenarios.",
    ]
    if "equipment-control-architecture" in selected:
        sections.append(
            "For a distributed ownership/recovery deliverable, explicitly include: "
            "an authority matrix; one shared-resource owner with reservation/arbitration and owner-loss behavior; "
            "a reconnect admission gate; restart reconstruction from current physical/material evidence; "
            "failover authority transfer with epoch/term, lease, fencing token, or equivalent single-writer control that rejects the old owner; "
            "command ID, attempt ID, idempotency/duplicate handling, timeout and late completion; "
            "fresh interlock/readiness revalidation; at least six fault-injection scenarios; "
            "and assumptions/unresolved inputs. Do not invent a backup topology or plant fact."
        )
    if "equipment-domain-modeling" in selected:
        sections.append(
            "For a component command/state contract, explicitly define Commanded, Desired, Pending/InProgress, "
            "Actual/Readback, Quality/Stale, Error/Uncertain, Reconciled, Success ACK versus physical completion, "
            "command ID, attempt ID, duplicate/idempotent policy, timeout, late completion/readback, and reconciliation."
        )
    for _path, instruction_text in skill_sections:
        sections.append("<instruction-set>\n" + instruction_text.rstrip() + "\n</instruction-set>")
    for _path, reference_text in reference_sections:
        sections.append("<reference-material>\n" + reference_text.rstrip() + "\n</reference-material>")
    return "\n\n".join(sections).strip() + "\n"


def _behavior_user_prompt(case: dict[str, Any]) -> str:
    return (
        "/no_think\n\n"
        "User request:\n"
        f'{case["prompt"].strip()}\n\n'
        "Begin immediately with <final>. Return one complete engineering deliverable and end with </final>."
    )


def build_selected_skills_prompt(
    *,
    manifest: dict[str, Any],
    case: dict[str, Any],
    decision: dict[str, Any],
    num_ctx: int,
    reserve_output_tokens: int,
    include_declared_references: bool = True,
    cases_path: Path = DEFAULT_CASES,
) -> dict[str, Any] | None:
    selected = selected_skills(decision)
    if not selected:
        return None
    if ROUTER_SKILL in selected:
        raise RuntimeError("using-cloudskill is the router and cannot be loaded as a downstream selected skill")
    if reserve_output_tokens < 1 or reserve_output_tokens >= num_ctx:
        raise ValueError("reserve_output_tokens must be positive and smaller than num_ctx")

    entries = _skill_entry_map(manifest)
    unknown = sorted(set(selected) - set(entries))
    if unknown:
        raise RuntimeError(f"router selected unknown skill IDs: {unknown}")

    loaded_files: list[dict[str, Any]] = []
    required_skill_sections: list[tuple[str, str]] = []
    optional_references: list[tuple[Path, str]] = []
    for skill_id in selected:
        skill_path = ROOT / entries[skill_id]["path"]
        skill_text = _read_required(skill_path)
        required_skill_sections.append((_relative(skill_path), skill_text))
        loaded_files.append(
            _file_evidence(
                path=skill_path,
                source_text=skill_text,
                included_text=skill_text,
                role=f"selected-skill-full:{skill_id}",
                required=True,
            )
        )
        if include_declared_references:
            for reference_path in discover_declared_references(skill_path, skill_text):
                reference_text = _read_required(reference_path)
                optional_references.append((reference_path, reference_text))

    case_source = json.dumps(case, ensure_ascii=False, indent=2)
    case_included = json.dumps(
        {"id": case["id"], "prompt": case["prompt"]},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    loaded_files.append(
        _file_evidence(
            path=cases_path,
            source_text=case_source,
            included_text=case_included,
            role=f'behavior-case:{case["id"]}',
            required=True,
        )
    )

    included_references = list(optional_references)
    dropped: list[tuple[Path, str]] = []
    user_prompt = _behavior_user_prompt(case)
    while True:
        reference_sections = [(_relative(path), text) for path, text in included_references]
        system_prompt = _behavior_system_prompt(
            decision=decision,
            skill_sections=required_skill_sections,
            reference_sections=reference_sections,
        )
        evidence = _finalize_prompt_evidence(
            mode="selected-skills",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            loaded_files=[],
            num_ctx=num_ctx,
            reserve_output_tokens=reserve_output_tokens,
            truncated_files=[_relative(path) for path, _ in dropped],
        )
        if not evidence["overflow_tokens"]:
            break
        if included_references:
            dropped.append(included_references.pop())
            continue
        required_evidence = list(loaded_files)
        for path, text in optional_references:
            required_evidence.append(
                _file_evidence(
                    path=path,
                    source_text=text,
                    included_text=text if path not in {p for p, _ in dropped} else "",
                    role="selected-skill-declared-reference",
                    required=False,
                    included=path not in {p for p, _ in dropped},
                    truncated=path in {p for p, _ in dropped},
                    reason="dropped as a whole file to fit context budget" if path in {p for p, _ in dropped} else None,
                )
            )
        evidence["loaded_files"] = required_evidence
        raise ContextBudgetError(
            "selected SKILL.md files and the current task exceed the configured input budget even after dropping all optional references. "
            "CloudBox refuses to truncate selected SKILL.md files. Increase --num-ctx or reduce the selected skill set.",
            evidence,
        )

    dropped_paths = {path for path, _ in dropped}
    for path, text in optional_references:
        loaded_files.append(
            _file_evidence(
                path=path,
                source_text=text,
                included_text=text if path not in dropped_paths else "",
                role="selected-skill-declared-reference",
                required=False,
                included=path not in dropped_paths,
                truncated=path in dropped_paths,
                reason="dropped as a whole file to fit context budget" if path in dropped_paths else None,
            )
        )
    evidence = _finalize_prompt_evidence(
        mode="selected-skills",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        loaded_files=loaded_files,
        num_ctx=num_ctx,
        reserve_output_tokens=reserve_output_tokens,
        truncated_files=[_relative(path) for path, _ in dropped],
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt, "context": evidence}


def validate_decision_shape(decision: Any, valid_skills: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(decision, dict):
        return ["decision is not an object"]
    keys = set(decision)
    if keys != EXPECTED_DECISION_KEYS:
        errors.append(
            f"decision keys differ: missing={sorted(EXPECTED_DECISION_KEYS - keys)} "
            f"extra={sorted(keys - EXPECTED_DECISION_KEYS)}"
        )
        return errors

    primary = decision["primary_skill"]
    supporting = decision["supporting_skills"]
    rejected = decision["rejected_skills"]
    order = decision["execution_order"]
    reason = decision["reason"]
    confidence = decision["confidence"]

    if primary is not None and not isinstance(primary, str):
        errors.append("primary_skill must be a string or null")
    for name, value in (
        ("supporting_skills", supporting),
        ("rejected_skills", rejected),
        ("execution_order", order),
    ):
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"{name} must be an array of strings")
        elif len(value) != len(set(value)):
            errors.append(f"{name} contains duplicates")

    if not isinstance(reason, str) or not reason.strip():
        errors.append("reason must be a non-empty string")
    if confidence not in {"high", "medium", "low"}:
        errors.append("confidence must be high, medium, or low")

    if errors:
        return errors

    all_ids = ([primary] if primary else []) + supporting + rejected + order
    unknown = sorted({item for item in all_ids if item not in valid_skills})
    if unknown:
        errors.append(f"unknown skill IDs: {unknown}")

    selected = ([primary] if primary else []) + supporting
    if len(selected) != len(set(selected)):
        errors.append("primary and supporting skills overlap")
    if set(order) != set(selected):
        errors.append("execution_order must contain every selected skill exactly once")
    if set(rejected) & set(selected):
        errors.append("rejected skills overlap selected skills")
    if primary is None and (supporting or order):
        errors.append("no-skill decisions must have empty supporting_skills and execution_order")
    if ROUTER_SKILL in supporting:
        errors.append("using-cloudskill is the router and must not appear in supporting_skills")
    return errors


def grade_decision(
    case: dict[str, Any], decision: Any, valid_skills: set[str]
) -> dict[str, Any]:
    """Grade fields independently while preserving a strict all-contract pass result."""

    expected = case["expected"]
    shape_errors = validate_decision_shape(decision, valid_skills)
    is_object = isinstance(decision, dict)

    primary = decision.get("primary_skill") if is_object else None
    supporting_raw = decision.get("supporting_skills") if is_object else None
    rejected_raw = decision.get("rejected_skills") if is_object else None
    order_raw = decision.get("execution_order") if is_object else None

    primary_type_valid = primary is None or isinstance(primary, str)
    supporting_type_valid = isinstance(supporting_raw, list) and all(
        isinstance(item, str) for item in supporting_raw
    )
    rejected_type_valid = isinstance(rejected_raw, list) and all(
        isinstance(item, str) for item in rejected_raw
    )
    order_type_valid = isinstance(order_raw, list) and all(
        isinstance(item, str) for item in order_raw
    )

    supporting = supporting_raw if supporting_type_valid else []
    rejected = rejected_raw if rejected_type_valid else []
    order = order_raw if order_type_valid else []
    selected_list = ([primary] if isinstance(primary, str) else []) + supporting
    selected = set(selected_list)
    required = set(expected["required_supporting_skills"])
    forbidden = set(expected["forbidden_selected_skills"])
    allow_extra = expected.get("allow_additional_supporting_skills", False)
    allowed_orders = expected.get("allowed_execution_orders")
    if allowed_orders is None:
        allowed_orders = [expected["execution_order"]]
    execution_order_matches = order_type_valid and any(order == candidate for candidate in allowed_orders)

    all_reported_ids = [
        item
        for item in ([primary] if isinstance(primary, str) else []) + supporting + rejected + order
        if isinstance(item, str)
    ]
    known_skill_ids = all(item in valid_skills for item in all_reported_ids)
    exact_keys = is_object and set(decision) == EXPECTED_DECISION_KEYS

    checks = {
        "valid_output": not shape_errors,
        "json_object": is_object,
        "exact_keys": exact_keys,
        "field_types": primary_type_valid and supporting_type_valid and rejected_type_valid and order_type_valid,
        "known_skill_ids": known_skill_ids,
        "primary_skill": primary_type_valid and primary == expected["primary_skill"],
        "required_supporting_skills": supporting_type_valid and required.issubset(set(supporting)),
        "additional_supporting_skills": supporting_type_valid and (
            allow_extra or set(supporting) == required
        ),
        "forbidden_selected_skills": primary_type_valid and supporting_type_valid and not bool(selected & forbidden),
        "execution_order": execution_order_matches,
        "router_not_downstream": primary_type_valid and supporting_type_valid and ROUTER_SKILL not in selected,
        "selected_set_consistent": (
            primary_type_valid
            and supporting_type_valid
            and order_type_valid
            and len(selected_list) == len(selected)
            and set(order) == selected
        ),
    }

    strict_checks = (
        "valid_output",
        "primary_skill",
        "required_supporting_skills",
        "additional_supporting_skills",
        "forbidden_selected_skills",
        "execution_order",
        "router_not_downstream",
    )
    failed_outcome_checks = [name for name in strict_checks if not checks[name]]
    errors = list(shape_errors)
    for name in failed_outcome_checks:
        if name not in errors:
            errors.append(name)
    return {
        "passed": all(checks[name] for name in strict_checks),
        "checks": checks,
        "errors": errors,
        "contract_errors": shape_errors,
    }

