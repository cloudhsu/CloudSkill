# Candidate release notes: proposed 5.6.0

## Conversation-derived routing

- Added bilingual routing cues for recurring production-code, equipment-control, equipment-modeling, document-quality, native/Qt, client/server, AI-agent, and repository-governance questions.
- Added an explicit route from historical conversation optimization requests to `developing-skills`.
- Added safeguards against claiming complete conversation access, hidden skill-loading traces, repository writes, tests, installs, or releases that did not occur.

## Skill-development workflow

- Added a historical-interaction mining workflow covering accessible-evidence inventory, sanitization, clustering, owner selection, RED cases, minimal changes, adjacent-skill regression, and read-only overlay fallback.
- Added behavior cases for version-scoped quality metrics, audience-derived documents, duplicate/stale communication review, application architecture, GitHub 403 fallback, and inspection-only counterexamples.

## Release gate

Before promoting this candidate to 5.6.0:

- run `python3 scripts/run_all_checks.py`,
- execute representative routing and behavior evaluations with the installed plugin,
- verify the ChatGPT plugin loads the updated descriptions,
- update VERSION, README, CHANGELOG, and both plugin manifests together,
- create a single-purpose commit and tag.
