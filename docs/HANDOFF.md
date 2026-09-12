---
updated: 2026-09-12
---
# Handoff

**Where we are.** Sixteen packages, WP-0001 to WP-0016, in four initiatives
(`ui`, `groupings`, `extraction-quality`, `review`). WP-0001 and WP-0002 are in
`done/`. WP-0003 is done on its branch and awaits review; with it the tree has a
question at every fork.

**Claimed.** WP-0003 (`status: review`, branch
`agent/2026-09-12-site-question-at-every-branch`, pull request open).

**Next agent's first move.** If WP-0003 has merged, close it (`AGENTS.md`
step 2) and claim WP-0004 (fold at every question, a reset button, a fixed "all"
row) on the same branch. Otherwise claim WP-0005, WP-0007 or WP-0011 — open, no
dependencies. Check `git ls-remote --heads origin 'agent/*'` first.

**Blocked, and why.**
- WP-0006 — waits on `docs/open-questions.md` → box-colour (the maintainer's call).
- WP-0014 — waits on `docs/open-questions.md` → structural-recommendations.

**Watch out.** `uv run tools/screenshot.py <view> --do all --do fit` prints the
overlapping pairs — nodes and answers on each other, and edges drawn across
either; a build package ends with 0 in the fully open state. The reviewer tests
on a phone; what the driver cannot see (the floating controls after a pan) is
still yours to look at. Every pull request links its preview as a complete
clickable URL (`https://graph.med/preview/pr<N>/<view-id>/`).
