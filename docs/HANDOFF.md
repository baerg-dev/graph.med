---
updated: 2026-09-12
---
# Handoff

**Where we are.** The work-package convention (`docs/work/README.md`, ADR-0001)
has just been set up and every initiative from the physician's review of the live
site is registered: sixteen packages, WP-0001 to WP-0016, in four initiatives
(`ui`, `groupings`, `extraction-quality`, `review`). Nothing has been worked yet.

**Claimed.** Nothing.

**Next agent's first move.** Claim WP-0001 (the search misses nodes the chapter
tree finds). WP-0007 and WP-0011 are also open with no dependencies and can run in
parallel with it.

**Blocked, and why.**
- WP-0006 — waits on `docs/open-questions.md` → box-colour (the maintainer's call).
- WP-0014 — waits on `docs/open-questions.md` → structural-recommendations.

**Watch out.** The pull-request preview (`graph.med/preview/pr<N>/`) is new; a
build package's PR should link it. The lone note "Kein Entscheidungsknoten" from
the review is WP-0003, not a mystery any more.
