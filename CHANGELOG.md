# Changelog

## 5.0.0

### Documentation architecture

- Removed full history snapshot directories; Git commits and annotated tags are authoritative.
- Reduced root-level Markdown entry points and introduced a document ownership map.
- Consolidated overlapping profile/capability documents.
- Separated source evidence by source without repeating it in the profile.
- Replaced standalone duplicated standards with one concise governance overview linked to executable skills.
- Consolidated migration guidance into the changelog and release index.
- Added an exact-paragraph duplication audit.

### Codex and Claude Code

- Added `INSTALL.md` for user and project installation.
- Added PowerShell and Bash installers.
- Added `CLAUDE.md` as a minimal adapter importing `AGENTS.md`.
- Kept `.agents/skills/` as the canonical skill source and synchronized it to Claude Code locations.
- Updated coding-agent governance for dual-tool repositories.

### Skill behavior

- Document governance now checks for an existing authoritative source before creating a new document.
- Coding-agent workflow recognizes both `AGENTS.md` and `CLAUDE.md`.
- Added a Claude project adapter template.

## 4.0.0

- Added source-grounded Bento and CloudBox evidence.
- Added safe incremental refactoring and cross-platform engine architecture.
- Added evidence confidence levels and source-aware architecture guidance.

## 3.0.0

- Added Client/Server, cross-platform native, coding-agent governance, and architect profile.

## 2.0.0

- Added documentation governance, ISO/IEC 25010, process tailoring, and AI-agent development.

## 1.0.0

- Initial architecture-review, framework-design, and code-review skills.
