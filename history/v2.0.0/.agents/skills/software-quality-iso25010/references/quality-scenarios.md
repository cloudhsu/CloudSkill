# Quality Scenario Template

Use:

| Field | Description |
|---|---|
| ID | Stable quality requirement ID |
| Characteristic | ISO/IEC 25010 classification |
| Stakeholder/source | Who needs the quality |
| Stimulus | Event or condition |
| Environment | Normal, degraded, startup, recovery, peak load, maintenance, etc. |
| Artifact/system | Affected boundary |
| Response | Required behavior |
| Measure | Quantitative or objectively verifiable criterion |
| Verification | Test, analysis, inspection, monitoring, field data |
| Owner | Accountable role |
| Evidence | Location/version of result |

## Example — Reliability

```text
QAR-REL-001
When the device communication link is interrupted during an acknowledged command,
the controller shall enter a defined uncertain-command state,
reconcile actual device state after reconnection,
and shall not automatically resend the command unless its idempotency is proven.
```

Measures may include:

- No duplicate side effect in defined fault-injection runs.
- Reconciliation completed within the accepted recovery interval.
- Trace contains command ID, disconnect event, state transition, and reconciliation result.

## Example — Maintainability

```text
QAR-MNT-004
A trained engineer shall be able to identify the owning module and primary failure
evidence for a defined command-processing fault within the target diagnostic time.
```

Measure with a controlled maintenance exercise rather than subjective judgment.
