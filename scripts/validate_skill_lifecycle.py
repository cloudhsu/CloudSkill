from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "manage_skill.py"

spec = importlib.util.spec_from_file_location("cloudskill_manage_skill", MODULE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {MODULE_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PACKET_MODULE_PATH = ROOT / "scripts" / "freeze_skill_review_packet.py"
packet_spec = importlib.util.spec_from_file_location("cloudskill_review_packet", PACKET_MODULE_PATH)
if packet_spec is None or packet_spec.loader is None:
    raise SystemExit(f"cannot load {PACKET_MODULE_PATH}")
packet_module = importlib.util.module_from_spec(packet_spec)
packet_spec.loader.exec_module(packet_module)

semantic_cases = [
    ({"introduced_version": "unreleased", "last_reviewed_version": "5.8.0"}, "5.8.0", "shipped Skill cannot remain unreleased"),
    ({"introduced_version": "5.7.0", "last_reviewed_version": "5.6.0", "next_review_triggers": ["the skill has not been reviewed for two feature releases"]}, "5.8.0", "two feature releases require review"),
]
for payload, current_version, label in semantic_cases:
    if not module.lifecycle_semantic_errors(payload, current_version):
        raise SystemExit(f"lifecycle semantic mutation was accepted: {label}")
# _feature_releases_since (and therefore lifecycle_semantic_errors) reads the
# *actual* live git tag history of whatever repository scripts/manage_skill.py
# is running inside (cwd=ROOT, hardcoded) -- it deliberately declines to
# fabricate a count when it can't prove one from real tags. That makes an
# assertion tied to specific hardcoded version numbers repository-specific:
# this repo's own tags happen to span 5.8.0..7.6.34, but a different clone
# (e.g. the filtered public export, whose own release history only reaches
# a different tip) has a different tag set and would fail this exact
# assertion for reasons that have nothing to do with the checker's logic.
# Build an isolated synthetic git repo with a controlled tag history instead,
# so this regression proves the *counting logic*, not today's live tag list --
# same isolation pattern the scaffold-path test below already uses via
# module.ROOT reassignment.
with tempfile.TemporaryDirectory() as tag_fixture_dir:
    tag_fixture = Path(tag_fixture_dir)
    from git_support import run_git_command  # local import: only needed for this fixture

    run_git_command(["init", "-q"], cwd=tag_fixture)
    run_git_command(["config", "user.email", "fixture@example.invalid"], cwd=tag_fixture)
    run_git_command(["config", "user.name", "fixture"], cwd=tag_fixture)
    (tag_fixture / "seed.txt").write_text("seed", encoding="utf-8")
    run_git_command(["add", "seed.txt"], cwd=tag_fixture)
    run_git_command(["commit", "-q", "-m", "seed"], cwd=tag_fixture)
    for tag in (
        "v5.7.0", "v5.8.0", "v6.0.0", "v6.1.0", "v6.2.0", "v6.3.0", "v6.4.0", "v6.5.0",
        "v7.4.0", "v7.5.0", "v7.6.0", "v7.6.34",
    ):
        run_git_command(["tag", tag], cwd=tag_fixture)

    saved_root = module.ROOT
    module.ROOT = tag_fixture
    try:
        if module.lifecycle_semantic_errors(
            {"introduced_version": "5.7.0", "last_reviewed_version": "5.8.0", "next_review_triggers": ["the skill has not been reviewed for two feature releases"]},
            "6.0.0",
        ):
            raise SystemExit("major-version boundary with only one real intervening release was falsely flagged")
        if not module.lifecycle_semantic_errors(
            {"introduced_version": "5.7.0", "last_reviewed_version": "5.8.0", "next_review_triggers": ["the skill has not been reviewed for two feature releases"]},
            "7.6.34",
        ):
            raise SystemExit(
                "major-version-boundary staleness blind spot regressed: last_reviewed_version 5.8.0 "
                "against current 7.6.34 (9 real intervening tagged minor releases: 6.0-6.5, 7.4-7.6) "
                "must be flagged, not silently skipped"
            )
    finally:
        module.ROOT = saved_root
if module.lifecycle_semantic_errors(
    {"introduced_version": "unreleased", "last_reviewed_version": "5.8.0"},
    "5.8.0",
    is_shipped=False,
):
    raise SystemExit("untracked working-tree candidate was falsely treated as shipped")

# Exercise the real scaffold path so schema changes cannot make every newly
# generated Skill invalid while validators only inspect pre-existing files.
original_paths = (module.ROOT, module.SKILLS, module.BEHAVIOR_CASES, module.POLICY, module.VERSION)
with tempfile.TemporaryDirectory() as temporary:
    fixture = Path(temporary)
    module.ROOT = fixture
    module.SKILLS = fixture / ".agents" / "skills"
    module.BEHAVIOR_CASES = fixture / "evals" / "behavior" / "cases"
    module.POLICY = ROOT / "config" / "skill-lifecycle-policy.json"
    module.VERSION = ROOT / "VERSION"
    module.scaffold(SimpleNamespace(
        name="fixture-skill",
        description="Use when validating the new-Skill scaffold.",
        display_name="Fixture Skill",
        short_description="Validate the Skill scaffold",
        case_prefix="FIXTURE",
    ))
    scaffold_payload = json.loads(
        (module.BEHAVIOR_CASES / "fixture-skill.json").read_text(encoding="utf-8")
    )
    if scaffold_payload.get("suite") != "fixture-skill-behavior":
        raise SystemExit("new-Skill scaffold omitted its unique behavior suite")
module.ROOT, module.SKILLS, module.BEHAVIOR_CASES, module.POLICY, module.VERSION = original_paths

packet_probe = packet_module.build_manifest(set())
if not packet_module.verify_manifest(packet_probe):
    raise SystemExit("review packet manifest failed deterministic verification")
explicit_base_probe = packet_module.build_manifest(set(), "HEAD")
if explicit_base_probe.get("base_head") != packet_module.git_bytes(
    "rev-parse", "HEAD"
).decode("ascii").strip():
    raise SystemExit("review packet manifest ignored its explicit base ref")

# Mechanical refresh must preserve manually sourced lifecycle truth rather than
# inventing release/review evidence to make an audit green.
preserved = module.lifecycle_payload(
    "fixture", policy={"review_triggers": []}, routing={}, behavior={},
    existing={"stage": "experimental", "introduced_version": "unreleased", "last_reviewed_version": "5.6.0"},
    default_stage="active",
)
if (preserved["stage"], preserved["introduced_version"], preserved["last_reviewed_version"]) != ("experimental", "unreleased", "5.6.0"):
    raise SystemExit("mechanical refresh invented lifecycle evidence")

original_version_path = module.VERSION
module.VERSION = ROOT / "missing-version-fixture"
try:
    missing_version_errors = module.audit(check=False)
except FileNotFoundError as exc:
    raise SystemExit(f"missing VERSION crashed lifecycle audit: {exc}") from exc
finally:
    module.VERSION = original_version_path
if not any("VERSION" in error for error in missing_version_errors):
    raise SystemExit("missing VERSION did not produce an auditable lifecycle error")

errors = module.audit(check=False)

# The standardization owner must declare the lifecycle reference and CLI --
# but developing-skills is private-meta (2026-08-28) and is not shipped in
# every checkout that runs this validator (e.g. the public CloudSkill
# mirror). Enforce every check below only where developing-skills is
# actually present; a repo that doesn't ship the standard-defining Skill
# can't audit its content, and that is a distribution-tier fact, not a
# lifecycle defect. DEVELOPING_SKILLS_PRESENT gates all 3 blocks that
# reference it further down this file.
DEVELOPING_SKILLS_PRESENT = (ROOT / ".agents/skills/developing-skills").is_dir()

developing_path = ROOT / ".agents/skills/developing-skills/SKILL.md"
if DEVELOPING_SKILLS_PRESENT:
    developing = developing_path.read_text(encoding="utf-8")
    for marker in (
        "references/skill-lifecycle-standard.md",
        "scripts/manage_skill.py",
        "draft",
        "experimental",
        "active",
        "stable",
        "deprecated",
    ):
        if marker not in developing:
            errors.append(f"developing-skills missing lifecycle marker: {marker}")

policy_path = ROOT / "config/skill-lifecycle-policy.json"
try:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    errors.append(f"cannot load lifecycle policy: {exc}")
    policy = {}
model_review = policy.get("semantic_model_review", {})
expected_review = {
    "transport": "managed_model_selected_subagents",
    "codex_models": ["gpt-5.6-luna", "gpt-5.6-sol"],
    "claude_preferred_models": ["sonnet-5", "opus-5"],
    "claude_allowed_fallback_generation": "4.8",
    "execution": "parallel_independent_same_packet",
    "minimum_completed_reviews_per_available_family": 2,
    "mutation_authority": "read_only",
    "cli_substitution_allowed_when_subagents_available": False,
    "require_exact_selected_or_returned_model_identity": True,
    "blocking_verdicts": ["FAIL", "BLOCKED", "MANUAL_REQUIRED"],
}
if model_review != expected_review:
    errors.append(
        "lifecycle semantic_model_review policy drifted from the managed "
        "Luna/Sol and Sonnet/Opus sub-agent gate"
    )

expected_brownfield_guard = {
    "default_change_mode": "extend_existing_refactored_implementation",
    "require_current_architecture_and_behavior_baseline": True,
    "require_smallest_coherent_slice": True,
    "preserve_public_and_operational_contracts": True,
    "whole_rewrite_requires_explicit_user_authorization": True,
    "skill_distillation_does_not_authorize_product_rewrite": True,
}
if policy.get("brownfield_implementation_guard") != expected_brownfield_guard:
    errors.append("lifecycle brownfield implementation guard drifted")

if DEVELOPING_SKILLS_PRESENT:
    behavior_reference = (
        ROOT / ".agents/skills/developing-skills/references/behavior-driven-skill-development.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "GPT-5.6 Luna",
        "GPT-5.6 Sol",
        "Sonnet 5",
        "Opus 5",
        "4.8",
        "Do not substitute `codex exec`",
        "previously refactored program",
        "whole rewrite",
        "two packet identities",
        "scripts/freeze_skill_review_packet.py",
    ):
        if marker not in behavior_reference:
            errors.append(f"behavior-driven lifecycle missing sub-agent review marker: {marker}")

# The policy and templates are release-critical -- but only the ones this
# checkout actually ships; developing-skills' own reference/asset files are
# conditional on DEVELOPING_SKILLS_PRESENT, same as the blocks above.
release_critical_files = ["config/skill-lifecycle-policy.json", "scripts/freeze_skill_review_packet.py"]
if DEVELOPING_SKILLS_PRESENT:
    release_critical_files.extend(
        [
            ".agents/skills/developing-skills/references/skill-lifecycle-standard.md",
            ".agents/skills/developing-skills/assets/SKILL_PROPOSAL.template.md",
            ".agents/skills/developing-skills/assets/SKILL_LIFECYCLE.template.json",
            ".agents/skills/developing-skills/assets/SKILL_RELEASE_EVIDENCE.template.md",
        ]
    )
for relative in release_critical_files:
    if not (ROOT / relative).is_file():
        errors.append(f"missing lifecycle standard file: {relative}")

for error in errors:
    print(f"ERROR: {error}")
print(f"Validated standardized lifecycle evidence for {len(module.skill_names())} skills.")
sys.exit(1 if errors else 0)
