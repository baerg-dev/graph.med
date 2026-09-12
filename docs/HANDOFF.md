---
updated: 2026-09-12
---
# Handoff

**Where we are.** Sixteen packages, WP-0001 to WP-0016, in four initiatives
(`ui`, `groupings`, `extraction-quality`, `review`). WP-0001 and WP-0002 are in
`done/`; WP-0003 is merged (#49) and still reads `review` — the next session
closes it. The live site has a question at every fork, answers beside what they
lead to, and every edge routed in the gap between columns; the physician's
review of a build change is done on a phone.

**Claimed.** Nothing.

**Next agent's first move.** Close WP-0003 (`AGENTS.md` step 2), then claim
WP-0004 (fold at every question, a reset button, a fixed "all" row) on the same
branch. WP-0005, WP-0007 and WP-0011 are also open with no dependencies. Check
`git ls-remote --heads origin 'agent/*'` first.

**Blocked, and why.**
- WP-0006 — waits on `docs/open-questions.md` → box-colour (the maintainer's call).
- WP-0014 — waits on `docs/open-questions.md` → structural-recommendations.

**Watch out.** `uv run tools/screenshot.py <view> --do all --do fit` prints the
overlapping pairs — nodes and answers on each other, edges across either; a
build package ends with 0. It cannot see a pan that pushes nodes under the
floating controls on a phone; look for that yourself. Deploys to `main` without
an open pull request were silently skipped until the deploy job got its own
condition on 2026-09-12 (`docs/publication.md` §6). Every pull request links
its preview as a complete clickable URL (`https://graph.med/preview/pr<N>/<view-id>/`).
