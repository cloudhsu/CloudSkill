# Review assurance levels

CloudBox records the review evidence actually obtained separately from the level required by risk.

| Level | Composition |
|---|---|
| L1_CROSS_FAMILY_2X2 | two independent canonical models from each of two families |
| L2_SINGLE_FAMILY_QUAD | four independent canonical models from one family |
| L3_SINGLE_FAMILY_PAIR | two independent canonical models from one family |
| L0_SINGLE_REVIEW | one independent canonical model |
| L0_NONE | deterministic evidence only |

Architecture, security, privacy, authority and irreversible release changes normally require L1. Normal feature, Skill, Eval, persistence and recovery changes normally require L2. Bounded patches normally require L3. Proven presentation-only document changes may use L0_NONE.

Blocked or invalid cells do not count. Repeated calls and aliases resolving to one canonical model count once. Exceptions preserve achieved level and require exact source, scope, residual risk and authorizer. No majority can override an unresolved safety, privacy, authority or High finding.

Run deterministic checks first. Reuse only source/contract/packet/rubric/risk-equivalent evidence. Stop when the required level is complete or a blocker is found. Record usage and cost by provider/model without averaging.

