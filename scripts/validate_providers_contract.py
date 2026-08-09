from __future__ import annotations

import ast
import json
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CONTRACT_PATH = ROOT / "evals" / "runtime" / "contracts" / "providers.json"

errors: list[str] = []

try:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"ERROR: cannot read providers contract: {exc}")
    sys.exit(1)

providers = contract.get("providers")
if not isinstance(providers, dict) or not providers:
    errors.append("providers.json must declare a non-empty 'providers' object")
    providers = {}

VALID_FAMILIES = {"local", "hosted-agent"}
for provider_id, info in providers.items():
    if not isinstance(info, dict):
        errors.append(f"providers.json/{provider_id}: entry must be an object")
        continue
    family = info.get("family")
    if family not in VALID_FAMILIES:
        errors.append(f"providers.json/{provider_id}: family must be one of {sorted(VALID_FAMILIES)}")
    for key in ("label", "default_model", "requires", "refinement_default"):
        if not isinstance(info.get(key), str) or not info.get(key):
            errors.append(f"providers.json/{provider_id}: missing non-empty '{key}'")
    if info.get("refinement_default") not in {"auto", "skip"}:
        errors.append(f"providers.json/{provider_id}: refinement_default must be 'auto' or 'skip'")

    if family == "hosted-agent":
        adapter_rel = info.get("adapter")
        if not isinstance(adapter_rel, str):
            errors.append(f"providers.json/{provider_id}: hosted-agent entry must declare 'adapter'")
        else:
            adapter_path = ROOT / adapter_rel
            if not adapter_path.is_file():
                errors.append(f"providers.json/{provider_id}: adapter file missing: {adapter_rel}")
            else:
                text = adapter_path.read_text(encoding="utf-8")
                for marker in (f"{provider_id}_preflight", f"call_{provider_id}_cli"):
                    if marker not in text:
                        errors.append(f"{adapter_rel}: missing expected marker '{marker}'")
    elif family == "local":
        call_site = info.get("call_site")
        if not isinstance(call_site, str) or "::" not in call_site:
            errors.append(
                f"providers.json/{provider_id}: local entry must declare 'call_site' as "
                "'<path>::<function>'"
            )
        else:
            rel_path, _, function_name = call_site.partition("::")
            call_path = ROOT / rel_path
            if not call_path.is_file():
                errors.append(f"providers.json/{provider_id}: call_site file missing: {rel_path}")
            elif f"def {function_name}(" not in call_path.read_text(encoding="utf-8"):
                errors.append(
                    f"providers.json/{provider_id}: call_site function not found: {call_site}"
                )

required_consumers = contract.get("required_consumer_paths")
if not isinstance(required_consumers, list) or not required_consumers:
    errors.append("providers.json must declare a non-empty 'required_consumer_paths' array")
    required_consumers = []

provider_ids = sorted(providers)

for consumer in required_consumers:
    path = ROOT / consumer
    if not path.is_file():
        errors.append(f"required provider consumer missing: {consumer}")
        continue
    text = path.read_text(encoding="utf-8")
    if consumer.endswith(".py"):
        if "providers_contract" not in text:
            errors.append(f"{consumer}: does not import the shared providers_contract adapter")
    else:
        # Shell consumers (cloudskill-resume) cannot import Python; require every
        # provider ID literal to appear so a newly registered provider cannot be
        # silently unreachable from the interruption-safe continuation command.
        for provider_id in provider_ids:
            if provider_id not in text:
                errors.append(f"{consumer}: missing provider literal '{provider_id}'")
        # cloudskill-resume only stages/commits paths listed in its FORMAL_PATHS
        # array; a hosted-agent provider's smoke launcher that is not listed
        # there is silently left uncommitted (a real regression this validator
        # caught: cloudskill-eval-claude was created but never staged).
        formal_paths_match = re.search(r"FORMAL_PATHS=\((.*?)\)", text, re.S)
        formal_paths_block = formal_paths_match.group(1) if formal_paths_match else ""
        for provider_id, info in providers.items():
            if not isinstance(info, dict) or info.get("family") != "hosted-agent":
                continue
            smoke_command = info.get("smoke_command", "")
            launcher_name = smoke_command.lstrip("./") if smoke_command.startswith("./") else ""
            if launcher_name and f'"{launcher_name}"' not in formal_paths_block:
                errors.append(
                    f"{consumer}: FORMAL_PATHS does not list '{launcher_name}' "
                    f"(providers.json/{provider_id} smoke_command), so it would never be staged"
                )

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

try:
    import providers_contract as loaded_contract
except Exception as exc:
    errors.append(f"cannot load scripts/providers_contract.py: {exc}")
else:
    if set(loaded_contract.PROVIDER_IDS) != set(provider_ids):
        errors.append(
            "scripts/providers_contract.py PROVIDER_IDS does not match "
            "evals/runtime/contracts/providers.json"
        )

# cloudskill-eval-<provider> smoke wrappers for every hosted-agent provider.
for provider_id, info in providers.items():
    if not isinstance(info, dict) or info.get("family") != "hosted-agent":
        continue
    smoke_command = info.get("smoke_command", "")
    launcher_name = smoke_command.lstrip("./") if smoke_command.startswith("./") else ""
    launcher = ROOT / launcher_name if launcher_name else None
    if launcher is None or not launcher.is_file():
        errors.append(f"providers.json/{provider_id}: smoke_command launcher not found: {smoke_command}")
        continue
    if not (launcher.stat().st_mode & stat.S_IXUSR):
        errors.append(f"{launcher_name} is not executable")
    text = launcher.read_text(encoding="utf-8")
    for marker in (f"--provider {provider_id}", "--repeat 1", "--no-refine"):
        if marker not in text:
            errors.append(f"{launcher_name} missing marker: {marker}")

# --- Mutation tests, mirroring the two categories used for the Behavior
# output contract in validate_behavior_contract.py: prove a contract edit
# propagates without touching a consumer (positive), and prove a
# hand-copied literal that bypasses the registry is caught (negative). The
# Behavior contract's version can re-render prompt text live at runtime and
# compare it against the authoritative contract; a --provider argparse
# `choices` tuple is baked into the parser once per process, so instead of
# executing a live mutation here, this checks statically (via AST) that each
# consumer's `choices` expression *is* PROVIDER_IDS rather than a copied
# tuple -- which is the actual guarantee that a future contract edit
# propagates without editing this file.


def provider_choices_expressions(path: Path) -> list[str]:
    """Source text of every `choices=` expression attached to a --provider
    add_argument(...) call in this file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    expressions: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "add_argument"):
            continue
        is_provider_flag = any(
            isinstance(arg, ast.Constant) and arg.value == "--provider" for arg in node.args
        )
        if not is_provider_flag:
            continue
        for keyword in node.keywords:
            if keyword.arg == "choices":
                expressions.append(ast.unparse(keyword.value))
    return expressions


# Positive propagation: every Python consumer with a --provider flag must
# derive its choices from providers_contract.PROVIDER_IDS symbolically.
for consumer in required_consumers:
    if not consumer.endswith(".py"):
        continue
    path = ROOT / consumer
    if not path.is_file():
        continue
    try:
        expressions = provider_choices_expressions(path)
    except SyntaxError as exc:
        errors.append(f"{consumer}: cannot parse for --provider choices check: {exc}")
        continue
    if not expressions:
        continue  # not every required consumer necessarily exposes --provider itself.
    if not any("PROVIDER_IDS" in expression for expression in expressions):
        errors.append(
            f"{consumer}: --provider choices={expressions!r} does not derive from "
            "providers_contract.PROVIDER_IDS; a provider added to or removed from "
            "providers.json would not propagate here automatically"
        )

# Negative drift injection: a hand-typed provider tuple/case-pattern that
# bypasses the registry should never reappear. These exact literals were a
# real regression this validator's own history includes (choices=("ollama",
# "codex") went stale when "claude" was added and had to be hand-fixed).
FORBIDDEN_PROVIDER_LITERALS = (
    'choices=("ollama", "codex")',
    "choices=('ollama', 'codex')",
    'choices=("ollama", "codex", "claude")',
    "choices=('ollama', 'codex', 'claude')",
)
SELF_REFERENCING_VALIDATORS = {
    # These files legitimately quote the forbidden literal as a documented
    # anti-pattern string to detect it elsewhere, not as a real argparse call.
    "validate_providers_contract.py",
    "validate_codex_eval_path.py",
}
for path in sorted(SCRIPTS.glob("*.py")):
    if path.name in SELF_REFERENCING_VALIDATORS:
        continue
    source = path.read_text(encoding="utf-8")
    for literal in FORBIDDEN_PROVIDER_LITERALS:
        if literal in source:
            errors.append(
                f"{path.relative_to(ROOT)}: contains a hand-typed --provider tuple "
                f"that bypasses the registry: {literal!r}"
            )

resume_text = (ROOT / "cloudskill-resume").read_text(encoding="utf-8")
if "ollama|codex)" in resume_text:
    errors.append(
        "cloudskill-resume: case statement still matches the pre-Claude "
        "'ollama|codex' pattern instead of the full registered provider set"
    )

print(
    f"Validated Runtime Eval provider registry: {len(providers)} provider(s), "
    f"{len(required_consumers)} required consumer path(s)."
)
print("NOTE: this validator does not call Ollama, Codex, Claude, or another model.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
