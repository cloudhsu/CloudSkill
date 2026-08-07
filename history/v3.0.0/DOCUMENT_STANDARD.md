# Engineering Documentation Standard

## 1. Purpose

Documents must support decisions, implementation, verification, operation, maintenance, learning, or audit. A document without a defined consumer and decision purpose should not be created by default.

## 2. Mandatory Metadata

Every controlled document should identify:

- Title.
- Document ID where applicable.
- Owner.
- Reviewers/approvers.
- Intended audience.
- Status: Draft, In Review, Approved, Superseded, Archived.
- Version.
- Effective date.
- Related product/release/project.
- Authoritative source or upstream data.
- Confidentiality/classification where applicable.

## 3. Information Types

Label or structurally separate:

- Fact: directly supported by evidence.
- Assumption: treated as true for current work but not yet verified.
- Decision: selected option with rationale and date.
- Requirement: mandatory outcome or constraint.
- Recommendation: non-binding proposal.
- Risk: uncertain event and impact.
- Issue: current deviation or unresolved problem.
- Action: accountable task with owner and due condition.
- Evidence: test, log, record, source, or measured result.

Do not present assumptions as confirmed facts.

## 4. Traceability

Where the work is significant, maintain links among:

```text
Business objective
  → stakeholder need
  → requirement
  → architecture/design decision
  → implementation item
  → verification case
  → release
  → field evidence / issue
```

Use stable identifiers. Do not rely only on section titles or file paths.

## 5. Audience Views

Use one evidence base and produce different views when needed:

- Raw evidence: imported data, logs, source records, exclusions, transformation rules.
- Executive/management view: operational effect, trend, risk, decision, owner.
- Engineering view: reproduction, root cause, architecture impact, corrective action, tests, learning.

Do not copy mutable metrics into multiple documents unless the source and refresh date are explicit.

## 6. Writing Rules

- Use domain terminology consistently.
- Define abbreviations and overloaded terms.
- Prefer one concept per sentence where precision matters.
- Use active voice for ownership and actions.
- Replace vague claims with measurable criteria.
- State units, time zone, sample range, version scope, and exclusions.
- Distinguish current state, target state, and transition state.
- For diagrams, include scope, direction, legend, and source-of-truth note.
- For examples, mark them as examples rather than normative behavior.

## 7. Change Control

A material change should record:

- What changed.
- Why it changed.
- Who approved it.
- Which requirements, interfaces, tests, releases, or field procedures are affected.
- Whether older versions remain valid.

## 8. Review Gates

A document is ready for approval only when:

- Purpose and audience are explicit.
- Facts and assumptions are distinguishable.
- Terms are consistent.
- Requirements are testable.
- Decisions include rationale and consequences.
- Figures/tables have sources and scope.
- Open issues have owners or are explicitly accepted.
- Traceability is sufficient for the document's risk level.
- The document does not contradict the authoritative source.
