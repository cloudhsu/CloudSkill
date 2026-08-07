# Traceability

## Recommended Identifier Families

- OBJ: business objective.
- NEED: stakeholder need.
- REQ: requirement.
- QAR: quality-attribute requirement.
- ADR: architecture decision.
- INT: interface.
- RISK: risk.
- TEST: verification case.
- DEFECT: defect.
- REL: release.
- FIELD: field evidence.

## Minimum Linkage

For high-impact work:

```text
REQ/QAR
  → ADR or design element
  → implementation location
  → TEST
  → REL
  → FIELD/DEFECT evidence
```

## Traceability Quality

Traceability must answer:

- Why does this exist?
- Where is it implemented?
- How is it verified?
- Which release contains it?
- Which evidence supports its current status?
- What is affected if it changes?
