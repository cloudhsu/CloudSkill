# Equipment Skill GREEN evidence — 2026-08-19

## Managed execution identity

The authoritative candidate input is
`docs/evolution/2026-08-19-equipment-candidate-packet.json`, packet ID
`sha256:71e49176fe52aada154cec420ad78695d8966f8bdad13496c460b06a18ce79e5`,
base HEAD `6e4e06cdedc1b90f91556a0a4b5a10ddc0936ba0`. Every executor verified the
manifest self-hash and all 75 file/deletion records before executing. Exact
model identity comes from the explicit assignment and managed selector; a
generic self-label is not canonical identity.

| Requested model | Selected model | Scope | Managed agent id | Cases | Result |
|---|---|---|---|---:|---|
| `gpt-5.6-luna` | `gpt-5.6-luna` | Tray-descum + cluster tool | `01a01a03-ca45-7403-9cd2-f73c0c8cc86d` | 9 | 9 PASS |
| `gpt-5.6-luna` | `gpt-5.6-luna` | bonder/debonder + WPH | `01a01a03-ca70-72d3-b29f-071360aaeb45` | 10 | 10 PASS |
| `gpt-5.6-sol` | `gpt-5.6-sol` | Tray-descum + cluster tool | `01a01a03-ca95-7241-bb92-cbc0c5ee5d98` | 9 | 9 PASS |
| `gpt-5.6-sol` | `gpt-5.6-sol` | bonder/debonder + WPH | `01a01a03-cac1-7e13-9477-4f2288502183` | 10 | 10 PASS |

All workers were read-only, used the current working-tree candidate, loaded the
assigned case files, owning Skills and declared references, and returned an
actual engineering deliverable per case. No executor was allowed to edit the
candidate it executed.

## Per-case result

| Case | Owner | Luna | Sol | Evidence layer |
|---|---|---|---|---|
| TDS-BEH-001 | tray-descum | PASS | PASS | recognition behavior |
| TDS-BEH-002 | tray-descum | PASS | PASS | concurrency/custody behavior |
| TDS-BEH-003 | tray-descum | PASS | PASS | chip-sorter counterexample |
| TDS-BEH-004 | tray-descum | PASS | PASS | restart/blocked-PM recovery |
| TDS-BEH-005 | tray-descum | PASS | PASS | unload/projection/reuse/reporting |
| CTS-BEH-001 | cluster tool | PASS | PASS | configurable topology recognition |
| CTS-BEH-002 | cluster tool | PASS | PASS | module-offline/restart recovery |
| CTS-BEH-003 | cluster tool | PASS | PASS | Tray-line counterexample |
| CTS-BEH-004 | cluster + WPH | PASS | PASS | mixed-cardinality application |
| WBD-BEH-001 | bonder/debonder | PASS | PASS | pair lifecycle recognition |
| WBD-BEH-002 | bonder/debonder + control | PASS | PASS | uncertain separation recovery |
| WBD-BEH-003 | bonder/debonder | PASS | PASS | die-attach counterexample |
| WBD-BEH-004 | bonder/debonder | PASS | PASS | temporary versus hybrid bonding |
| WBD-BEH-005 | bonder/debonder + control | PASS | PASS | wrong pair/cleaner/host disagreement |
| WPH-SIM-REC-001 | WPH + family Skills | PASS | PASS | cross-family recognition/composition |
| WPH-SIM-APP-001 | WPH | PASS | PASS | unsupported capacity repair |
| WPH-SIM-CTR-001 | WPH | PASS | PASS | production-interlock counterexample |
| WPH-SIM-APP-002 | WPH + cluster | PASS | PASS | cardinality/good-output application |
| WPH-SIM-APP-003 | WPH | PASS | PASS | stochastic calibration application |

## First-review RED and correction

| Finding | Correction | GREEN evidence |
|---|---|---|
| Candidate versions claimed the future release | New Skills use `unreleased`; audit distinguishes untracked candidates from shipped Skills | lifecycle audit PASS |
| Public decision ledger retained source-package/path detail | Replaced with generalized provenance and sanitization decisions | privacy scan PASS |
| Behavior suites lacked executable `suite` identity | Added unique suite to every behavior case file; schema and validator now require it | all four candidate Runtime Eval dry-runs PASS at 32K context |
| Family Skills and WPH both appeared to own capacity | Family descriptions/workflows delegate capacity; WPH is primary when capacity is the deliverable | both models route CTS-BEH-004 and WPH composition correctly |
| Bonder reserved an entire route atomically | Reservation is per next physical action; future capacity is staged admission/planning | both WBD executors use action-scoped reservation |
| Production-control overlap was underspecified | Cluster and bonder require equipment-control composition for production sequence/interlock/restart authority | recovery cases route with control support where needed |
| Recovery/statistical seams were prose-only | Added TDS-BEH-004/005, WBD-BEH-005 and WPH-SIM-APP-003 | 8/8 new cross-model executions PASS |
| Public-source facts and inferences were mixed | Evidence note labels `DIRECT` versus `INFERENCE` and removes unsupported subsystem assumptions | source review incorporated |
| Statistical fingerprint omitted reproducibility fields | Added initial state, seed policy, replication count, CI method and stopping rule | WPH-SIM-APP-002/003 pass both models |

## Final-panel RED and bounded correction

The first final-review attempt was blocking, so it did not authorize release.

| Requested/selected model | Managed agent id | Verdict | Blocking pressure closed |
|---|---|---|---|
| `gpt-5.6-luna` | `01a019f9-fcb3-7030-b275-c2e6a3a4d042` | FAIL | GREEN evidence lacked an immutable candidate packet identity |
| `gpt-5.6-sol` | `01a019f9-fcdf-76d0-8c89-ffd570129ab8` | FAIL | scaffold omitted `suite`; CTS-BEH-004 did not enforce WPH ownership; lifecycle text was stale; packet/model binding incomplete |

Corrections were deliberately limited to the failed layers: the real
`manage_skill.py new` path now emits and regression-tests a unique suite,
CTS-BEH-004 requires WPH-primary/Cluster-supporting composition, lifecycle notes
point to dated evidence, and a two-packet hashing tool binds execution and final
review without self-reference. No equipment product implementation was changed.
The 19 cases were then rerun in full against the candidate packet above rather
than reusing the superseded execution evidence.

The second bounded final-review packet was
`sha256:bb6dc51f5046891eccf146e284b25146c467eed0e037263cec5eec87e0586673`.
Luna (`01a01a07-cde5-7431-8c72-683b5fd85c5d`) returned PASS. Sol
(`01a01a07-ce07-7ce0-9961-475ebb54c2e5`) confirmed all 19 equipment cases and
owner boundaries but returned FAIL because the materially changed
`developing-skills` lifecycle and DEVSK-BEH-022/023 evidence were incomplete.
The bounded final-review limit was therefore reached; release requires manual
disposition even after those process-layer defects are corrected.

## Execution limits

- This increment changes Skill, Eval and lifecycle artifacts only. It does not
  rewrite any existing or previously refactored equipment simulator program.
- Hardware, production, approved recipe, measured timing, field recovery and
  calibrated trace evidence: `NOT RUN`.
- No numeric WPH was fabricated. Cases without authoritative scenario inputs
  returned a model/validation contract and withheld capacity claims.
- Static checks and dry-runs are separate from semantic execution. Equipment
  behavior is GREEN, but the combined repository release is `MANUAL_REQUIRED`
  because the bounded final-review panel did not finish with two PASS verdicts.
