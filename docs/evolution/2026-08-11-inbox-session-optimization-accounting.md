# Inbox and session optimization accounting

Status: implementation candidate; formal release not yet authorized.

## Evidence boundary

The pass reviewed 45 private `manual-review` candidates plus sanitized current
session evidence. Raw candidates remain private and were not copied here. The
records were deduplicated into O01–O30; project-history conclusions remain
inferred/unknown, while executed importer and release failures are observed.

## Decisions

| Decision | Candidate IDs | Owner/result |
|---|---|---|
| PROMOTED | O01–O03, O06 | `developing-skills`: consumer parity, whole-archive planning, untrusted intake, owning-config privacy policy; executable config parity fixed. |
| REGRESSION_ONLY | O04–O05 | Exact-tip and release-closure cases added; baseline already complied, so target Skills were unchanged. |
| NO_CHANGE_JUSTIFIED | O07–O10, O16, O23, O25–O26, O28, O30 | Existing agent/process/review/plugin/governance behavior already complied. Token-specific deterministic clustering and stop-on-blocker rules were consolidated in `developing-skills`; no duplicate token Skill was created. |
| MERGED_AND_PROMOTED | O11–O14 | `code-review`: ordered parsing, joined shutdown, readiness/acceptance/completion/readback separation. |
| MERGED_AND_PROMOTED | O15, O17 | `framework-design`: unequal capabilities and authoritative registry propagation/drift. |
| MERGED_AND_PROMOTED | O18, O24, O29 | `cross-platform-native-architecture`: design-host ABI, process identity/liveness, startup and local-secret ownership. |
| MERGED_AND_PROMOTED | O19–O20 | `software-quality-iso25010`: freshness/correlation and risk-bounded native evidence cells/denominators. |
| MERGED_AND_PROMOTED | O21 | `safe-incremental-refactoring`: seam/test/bootstrap/auth decision table. |
| SPLIT_AND_PROMOTED | O22 | `application-client-server-architecture`: four distinct cases for durability divergence, schema/product versions, immutable compensation, and post-external-commit reconciliation. |
| PROMOTED | O27 | `document-governance`: container version, observation version, and transformation provenance remain distinct. |

No source candidate was deleted. Manual review, unsupported retention, and
legacy recovery remain supported until a separately approved stable exchange
format and migration policy exist.

## Evidence status

- Task 1 independent RED: 0/4; GREEN: 4/4.
- Task 2 and token/governance baselines: `NO_CHANGE_JUSTIFIED`.
- Domain owners: pre-change semantic gap audit plus focused current cases.
- Structural Behavior contracts and lifecycle audit: PASS.
- Combined targeted semantic GREEN: 11/11 PASS; boundary audit found no
  High/Medium omission.
- Complete deterministic suite after integration: PASS (two passes).
- Model-backed Runtime Eval corpus execution: not claimed; the targeted GREEN
  is an independent semantic execution, not a full provider-backed corpus run.
- Exact-tip review remains the final candidate gate.
