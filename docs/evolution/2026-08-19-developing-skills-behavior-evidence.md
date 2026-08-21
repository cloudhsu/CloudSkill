# Developing-skills process behavior evidence — 2026-08-19

## RED

The second bounded final panel found that the materially changed
`developing-skills` Skill still had stale lifecycle truth and no model-behavior
evidence for DEVSK-BEH-022/023. The first attempt to execute those cases also
showed an ambiguous evaluation contract: one model interpreted DEVSK-BEH-022 as
requiring a single read-only executor to dispatch a second reviewer panel,
while another correctly treated it as a coordinator decision contract.

## Minimal correction

- `last_reviewed_version` and notes now identify the unreleased process change
  and manual gate truthfully.
- DEVSK-BEH-022 explicitly evaluates coordinator actions/evidence/release
  disposition; real sub-agent dispatch remains separate integration evidence.
- The brownfield no-unapproved-rewrite case remains unchanged in substance.

## Packet-bound GREEN

Candidate packet:
`sha256:acbaabee6dd1add5337f0f6737cdc0a48ea92d7500250dd374b9031fb686becc`.
Both read-only executors verified all 78 packet records before execution.

| Requested/selected model | Managed agent id | DEVSK-BEH-022 | DEVSK-BEH-023 |
|---|---|---|---|
| `gpt-5.6-luna` | `01a01a11-92ab-7af1-bdf3-81e7732ffb0e` | PASS | PASS |
| `gpt-5.6-sol` | `01a01a11-92cd-76b1-967b-fa21b5c6d701` | PASS | PASS |

The Luna executor separately reported the overall release as BLOCKED because it
correctly refused to treat one behavior execution as the required independent
final review. That does not negate its 2/2 case/contract PASS; it preserves the
layer distinction. Sol reported the same separation explicitly.

## Integration and release truth

Managed sub-agent integration did execute earlier in this increment and is
recorded in the equipment GREEN and final-review evidence. The bounded final
panel ended Luna PASS / Sol FAIL before the process-layer correction. Because
the repository policy limits correction/retest rounds, no third model panel is
used to manufacture a PASS. The repository owner subsequently approved the
frozen manual evidence packet, then held the new equipment Skills in private
distribution before any remote release succeeded.
