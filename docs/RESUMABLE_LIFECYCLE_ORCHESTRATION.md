# Resumable lifecycle orchestration

CloudBox uses a pressure-selected lifecycle graph rather than one mandatory waterfall. The default development profile is iterative/incremental; Skill evolution defaults to Eval-driven RED, minimum change, GREEN and adjacent regression.

The lifecycle planning owner is development-process-tailoring. It owns:

- selected profiles, stages, gates and feedback paths;
- versioned dependency-ordered execution plans;
- risk/evidence-triggered replanning;
- stage entry, exit and re-entry;
- durable checkpoint and resume classification.

Technical Skills still own architecture, domain, design, code, quality and document decisions. A generic planning plugin may produce detailed steps only through the CloudBox plan contract.

A resumed task first reconciles durable state, authoritative plan revision, hashes, external effects and authority. It returns SAFE_TO_RESUME, ALREADY_COMPLETED, RETRY_REQUIRED, RECONCILIATION_REQUIRED, STALE_BASELINE or AUTHORITY_REQUIRED. Timeout alone never proves failure.

One coordinator owns state transitions through a lease/fencing token. Actions carry stable identity and deduplication keys. Risk changes produce a new plan revision, invalidate affected downstream work, preserve unrelated evidence and recalculate review assurance. Release, deployment, target verification and operational confirmation remain separate states.

