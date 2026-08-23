# Human-Readable HTML Overview Views

This governs an optional static HTML page that presents a governed Markdown
domain (product direction, art governance, or an equivalent decision area)
for human reading — not a second source of authority, and not a build
artifact that needs a server, framework, or external dependency.

## Rules

1. **Markdown stays authoritative.** The HTML page is a view over the
   existing governed Markdown documents and decision records; it never
   introduces a fact, decision, or status that isn't already recorded in
   Markdown. If the two disagree, the Markdown is correct and the HTML page
   is stale.
2. **One stable entry page per governed domain**, named `index.html` at
   that domain's own root (for example `product/index.html`,
   `art/index.html`) so it stays discoverable and diffable next to the
   Markdown it summarizes, and reachable by opening the file directly in a
   browser — no build step, no server, no external stylesheet or script.
3. **Content requirements per domain type:**
   - Product view: legacy baseline, current product definition, invariant
     core loop, variable presentation profiles, scope tiers, and the
     current stop condition.
   - Art view: Art Bible rules, draft/selected/final/runtime lifecycle
     gates, visual candidate previews, profile/case matrices, and known
     technical or legibility limitations.
   - Every entry page: current status, scope, decisions, open questions,
     evidence boundaries, and relative links back to the authoritative
     Markdown documents.
4. **Portable and local-first**: relative links only, local visual assets
   only (no remote image/font/script dependency), and an explicit note that
   a static preview is not runtime or release evidence — it summarizes
   governance state, it does not prove a build, install, or platform gate
   passed.
5. **Commit together.** The HTML page and the documentation change it
   summarizes land in the same commit; an HTML page that silently drifts
   out of sync with the Markdown it claims to summarize is worse than no
   page, because it looks authoritative while being wrong.
6. **Link the entry page from the domain's own `README.md`** (a short
   "human-readable overview" pointer) so a reader who lands on the
   directory listing first can still find it.

## What this is not

Not a documentation site generator, not a replacement for the Markdown
files, not evidence of runtime/platform/release readiness, and not
required for every governed domain — build one only when a domain has
accumulated enough decision history that a human-reading entry point is
actually worth maintaining and keeping in sync.
