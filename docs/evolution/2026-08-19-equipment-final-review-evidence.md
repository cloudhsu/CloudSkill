# Equipment Skill final review evidence — 2026-08-19

## Packet identities

| Layer | Packet ID | Purpose |
|---|---|---|
| Equipment candidate | `sha256:71e49176fe52aada154cec420ad78695d8966f8bdad13496c460b06a18ce79e5` | 19-case semantic input |
| Equipment review | `sha256:bb6dc51f5046891eccf146e284b25146c467eed0e037263cec5eec87e0586673` | Candidate plus packet-bound GREEN evidence |
| Manual-review candidate | `sha256:acbaabee6dd1add5337f0f6737cdc0a48ea92d7500250dd374b9031fb686becc` | Process-layer correction after bounded panel |

## Bounded final panel

| Round | Model | Agent id | Verdict | Disposition |
|---:|---|---|---|---|
| 1 | `gpt-5.6-luna` | `01a019f9-fcb3-7030-b275-c2e6a3a4d042` | FAIL | Missing immutable packet binding |
| 1 | `gpt-5.6-sol` | `01a019f9-fcdf-76d0-8c89-ffd570129ab8` | FAIL | Packet, scaffold, owner-rubric and lifecycle defects |
| 2 | `gpt-5.6-luna` | `01a01a07-cde5-7431-8c72-683b5fd85c5d` | PASS | No blocking finding |
| 2 | `gpt-5.6-sol` | `01a01a07-ce07-7ce0-9961-475ebb54c2e5` | FAIL | Developing-skills lifecycle and two meta behavior cases incomplete |

Both round-2 reviewers verified the same 77-record review packet. Both agreed
that the four equipment Skills, all 19 cases, public de-identification, WPH and
family ownership, brownfield boundary and evidence limitations were sound.

## Post-panel correction

The process-layer findings were corrected and DEVSK-BEH-022/023 now pass both
Luna and Sol against the 78-record manual candidate packet. WBD recovery rubric
hardening was a nonblocking suggestion and is deferred to a future candidate so
the bounded correction does not expand scope.

## Gate

- Equipment behavior: PASS, Luna/Sol 19/19.
- Deterministic repository suite: PASS before the manual packet.
- Hardware/field/calibration/recipe/numeric WPH: NOT RUN.
- Claude Sonnet 5/Opus 5 (or 4.8 availability fallback): NOT RUN in Codex host.
- Combined release reached `MANUAL_REQUIRED`; the repository owner accepted
  packet `sha256:4d883ce20513f57ac98ebc67c62cade7ba0c43aab24bd521eb99074d522381a6`
  on 2026-08-19 (Asia/Taipei), authorizing an experimental Skill/tooling
  release only. Product, safety, recipe, calibrated WPH and field claims remain
  outside the authorization.

## Superseding distribution decision

Before any remote push, tag, or GitHub Release succeeded, the repository owner
placed the three new equipment-family Skills in `private-equipment`. Semantic
approval remains evidence for internal use; it is not public-publication
authority. WPH retains the public classification it already held before this
increment.
