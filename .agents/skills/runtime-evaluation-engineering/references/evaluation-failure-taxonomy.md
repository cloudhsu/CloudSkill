# Evaluation failure taxonomy

Diagnose from the earliest layer that failed.

| Layer | Typical evidence | Correct interpretation |
|---|---|---|
| Infrastructure | Python/Ollama/model/file unavailable | No model-quality conclusion |
| Context assembly | required files missing, overflow, truncation | Runner/retrieval defect or unsupported budget |
| Contract adherence | malformed JSON, invalid selected-set relation | Structure problem; field-level routing may still be informative |
| Case validity | repeated plausible alternative owner/order | Expected answer may be ambiguous |
| Model discrimination | valid context and contract, unstable or wrong route | Model/prompt boundary issue |
| Skill/Router rule | repeated failure across models with verified case/context | Authoritative routing or behavior rule may be incomplete |
| Deterministic grader | false positive/negative from patterns or relations | Fix grader before changing Skill |
| Semantic judge | inconsistent equivalence or unsupported inference | Require calibrated judge or human review |
| Release interpretation | pipeline succeeded but score gate failed | Evidence exists; do not call it an execution crash |

## Escalation rule

Never infer a Skill defect from one model run. Require:

- verified context,
- valid case ownership,
- repeated evidence,
- grader review,
- adjacent regression analysis.

## Ambiguity signature

Classify `AMBIGUOUS` when:

- the prompt asks for two independently owned deliverables but names one expected primary;
- multiple execution orders preserve the same required set;
- the expected answer depends on unstated audience, authority, or output form;
- repetitions converge on a plausible alternative rather than varying randomly.
