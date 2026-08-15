from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PROCESS_SKILL = ROOT / ".agents/skills/development-process-tailoring/SKILL.md"
DEVELOPING_SKILL = ROOT / ".agents/skills/developing-skills/SKILL.md"
DEVELOPING_EVAL_SKILL = ROOT / ".agents/skills/developing-eval/SKILL.md"


def contract_errors(process_text: str, developing_text: str, eval_text: str = ""):
    process = re.sub(r"\s+", " ", process_text).lower()
    developing = re.sub(r"\s+", " ", developing_text).lower()
    ev = re.sub(r"\s+", " ", eval_text).lower()
    checks = {
        "development-process-tailoring owns the lifecycle plan": (
            "own the lifecycle plan, execution-plan contract" in process
        ),
        "lifecycle is highest planning authority": (
            "lifecycle is always the highest planning authority" in process
        ),
        "generic planner is not a second authority": (
            "does not become a second process authority" in process
        ),
        "risk creates a new plan revision": (
            "new risk or authority evidence creates a new plan revision"
            in process
        ),
        "template fast path requires six literal false values": (
            "answer all six bounded-delta questions with literal `true` or `false` values"
            in process
            and "only when every one of the six answers is literal `false`"
            in process
            and "any literal `true`, missing, non-boolean, or unknown answer requires"
            in process
        ),
        "template selection binds context and auto-invalidates contradictions": (
            "every template's stage partial order" in process
            and "deterministic topological merge" in process
            and "bound work/source/tasks/facts/risk/registry context" in process
            and "automatically invalidates that identity" in process
            and "do not depend on a caller invalidation list" in process
            and "result bound to the new context" in process
        ),
        "process priority is lifecycle then evidence then token": (
            "lifecycle and dynamic feedback loop first" in process
            and "evidence and verification second" in process
            and "token/context cost third" in process
        ),
        "skill optimization uses the same priority": (
            "lifecycle and its dynamic feedback loop" in developing
            and "then evidence and verification" in developing
            and "then token/context cost" in developing
        ),
        "manual review remains default-visible": (not eval_text) or ("manual-review" in ev),
        "unsupported retention remains default-visible": (
            (not eval_text) or ("unsupported evidence" in ev)
        ),
        "legacy recovery remains default-visible": (not eval_text) or ("legacy recovery" in ev),
        "raw transcript prohibition remains default-visible": (
            (not eval_text) or ("raw or complete transcript" in ev)
        ),
    }
    return [label for label, passed in checks.items() if not passed]


def main() -> int:
    process_text = PROCESS_SKILL.read_text(encoding="utf-8")
    developing_text = DEVELOPING_SKILL.read_text(encoding="utf-8")
    eval_text = DEVELOPING_EVAL_SKILL.read_text(encoding="utf-8") if DEVELOPING_EVAL_SKILL.is_file() else ""
    errors = contract_errors(process_text, developing_text, eval_text)

    # Negative mutation proves the validator detects removal of the priority
    # authority rather than merely confirming that both files are readable.
    mutated = process_text.replace(
        "highest planning authority",
        "participating planning authority",
        1,
    )
    if not contract_errors(mutated, developing_text):
        errors.append("negative mutation did not detect lifecycle-priority drift")

    owner_mutation = process_text.replace(
        "Own the lifecycle plan, execution-plan contract",
        "Observe the lifecycle plan and execution-plan contract",
        1,
    )
    if not contract_errors(owner_mutation, developing_text):
        errors.append("negative mutation did not detect Plan Owner drift")

    literal_boolean_mutation = re.sub(
        r"only when every one of the six answers is literal\s+`false`",
        "when the answers appear false",
        process_text,
        1,
    )
    if not contract_errors(literal_boolean_mutation, developing_text):
        errors.append("negative mutation did not detect literal-boolean drift")

    template_context_mutation = process_text.replace(
        "automatically invalidates that identity",
        "may invalidate that identity when requested",
        1,
    )
    if not contract_errors(template_context_mutation, developing_text):
        errors.append("negative mutation did not detect automatic-invalidation drift")

    if errors:
        for error in errors:
            print(f"ERROR: planning-priority contract missing: {error}")
        return 1

    print(
        "Validated lifecycle-first, evidence-second, token-third planning "
        "priority, sole Plan Owner, and retained Skill-evolution safeguards"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
