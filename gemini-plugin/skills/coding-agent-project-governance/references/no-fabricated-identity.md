# No Fabricated Identity

A deliverable shaped like a formal report, release gate, attestation, or
governed document often conventionally carries an author, owner,
submitted-by, or attribution field. That shape is not license to fill the
field from whatever identity the runtime session happens to expose.

## The rule

When a task supplies no author/owner/submitted-by fact itself, do one of:

- Mark the field explicitly unresolved (`owner: <unresolved, confirm with
  requester>`), or
- Use a generic placeholder (`actor@example.invalid`, `<unspecified>`).

Never reach for the real ambient identity available in the runtime
environment (a host git config user, a logged-in account, an OS user
profile) to fill a field the task itself never provided. A fabricated
attribution is a defect independent of whether the deliverable's
conventional shape "expects" such a field -- the field existing as a slot
in the template does not make inventing its value acceptable.

This prohibition is not satisfied by correctly marking the one named field
(owner/author/submitted-by) unresolved and then inventing a *different*,
unnamed field -- "requester," "contact attribution," "raised by," or any
other newly-introduced label -- to carry the same real ambient identity
instead. Observed directly: a real run correctly wrote
`owner: <unresolved, confirm with requester>` and, immediately below it,
added a field the template never had ("this request's proposer") filled
with the real ambient email. Treat any field anywhere in the output that
would resolve to a real ambient identity as the same defect, regardless of
what it is named or whether it is one of the fields explicitly listed
above.

## Why this keeps recurring

This is not one skill's defect. It is a general tendency: whenever a
deliverable's shape includes an identity-looking field and no identity was
supplied, filling it from ambient session context is a plausible-looking
completion the underlying model reaches for by default. It has been
observed independently across skills whose normal output includes
ownership/attribution metadata -- document governance, release-gate
reports, quality-evidence records, project-management sync payloads -- not
confined to any one of them. Treat it as a cross-cutting risk to check for
in any report-shaped deliverable, not a fact specific to whichever skill
happened to be tested.

## Distinguish from the redaction case

This is the fabrication half of a related pair. The other half --
project-management-sync's required-output rule on never echoing a *known*
ambient identity even to explain it was redacted -- covers a case where the
identity is genuinely available and must be actively hidden. This rule
covers the opposite failure: the identity was never part of the task's
evidence at all, and inventing it is itself the defect, regardless of
whether hiding it was ever a live question.
