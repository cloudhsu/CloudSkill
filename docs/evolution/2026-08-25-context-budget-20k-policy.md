# 2026-08-25 Skill context-budget policy update

## Decision

The repository default `SKILL.md` context budget is now **20,000 UTF-8
bytes**, enforced by `scripts/validate_skill_context_budget.py`.

This is a deterministic file-size gate based on `Path.read_bytes()`. It is
not a tokenizer limit, an exact token count, or a provider billing claim.
The runtime design still keeps shared routing, mandatory invariants, and
essential workflow in `SKILL.md`, while conditional procedures and large
examples belong in `references/` and are loaded only when relevant.

The change was explicitly requested by the repository owner on 2026-08-25
after the existing 10,500-byte gate failed seven current Skills. The
historical grandfathered ceilings are retired; no `SKILL.md` content was
changed by this policy update.

## Inventory and alternatives

| Ceiling | Skills passing | Skills failing | Largest current `SKILL.md` | Headroom above largest |
|---:|---:|---:|---:|---:|
| 10,500 bytes | 34 / 41 | 7 | 14,876 bytes | -4,376 bytes |
| 20,000 bytes (adopted) | 41 / 41 | 0 | 14,876 bytes | 5,124 bytes |
| 21,000 bytes (considered) | 41 / 41 | 0 | 14,876 bytes | 6,124 bytes |

The seven files that exceeded the retired ceiling were:

- `developing-skills`: 10,686 bytes
- `development-process-tailoring`: 12,666 bytes
- `equipment-control-architecture`: 14,876 bytes
- `equipment-domain-modeling`: 12,064 bytes
- `game-art-pipeline`: 10,670 bytes
- `game-narrative-design`: 10,654 bytes
- `local-runtime-eval-debugging`: 11,647 bytes

Changing from 20,000 to 21,000 bytes would not change the current pass/fail
result or any package/projection output. It would add 1,000 bytes of future
headroom, approximately 5% more than the adopted gate, while weakening the
early warning for main-file growth. The extra allowance is not currently
needed, so 20,000 bytes is the recorded policy decision.

The earlier 10,500-byte token-refactor evidence remains historical evidence
for that earlier policy and is intentionally not rewritten.
