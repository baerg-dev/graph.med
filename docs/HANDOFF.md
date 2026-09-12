---
updated: 2026-09-12
---
# Handoff

**Where we are.** The work-package convention (`docs/work/README.md`, ADR-0001)
is in place with sixteen packages, WP-0001 to WP-0016, in four initiatives
(`ui`, `groupings`, `extraction-quality`, `review`). WP-0001 is done on its branch
and awaits review; nothing else has been worked.

**Claimed.** WP-0001 (`status: review`, branch `agent/2026-09-12-site-search-recall`,
pull request open). After approval its last commit moves it to `done/`.

**Next agent's first move.** Claim WP-0002 (nothing overlaps: every node and
answer readable). WP-0007 and WP-0011 are also open with no dependencies and can
run in parallel with it. Nothing depends on WP-0001.

**Blocked, and why.**
- WP-0006 — waits on `docs/open-questions.md` → box-colour (the maintainer's call).
- WP-0014 — waits on `docs/open-questions.md` → structural-recommendations.

**Watch out.** The pull-request preview (`graph.med/preview/pr<N>/`) is new; a
build package's PR should link it. The search index in the view JSON (`text` on
nodes and on answer edges) is no longer lowercased: the browser folds case and
diacritics on both sides (WP-0001, Decisions).
