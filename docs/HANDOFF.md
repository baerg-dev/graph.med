---
updated: 2026-09-12
---
# Handoff

**Where we are.** Sixteen packages, WP-0001 to WP-0016, in four initiatives
(`ui`, `groupings`, `extraction-quality`, `review`). WP-0001 is merged (search
recall) but its file still says `review` in `docs/work/`: the commit that sets
`done` and moves it to `done/` has not been asked for. WP-0002 is done on its
branch and awaits review.

**Claimed.** WP-0002 (`status: review`, branch
`agent/2026-09-12-site-layout-visibility`, pull request open).

**Next agent's first move.** WP-0003 depends on WP-0002 and waits for it to
reach `done/`. Until then claim WP-0005 (the detail section by the six
questions), WP-0007 or WP-0011 — all open with no dependencies. Check
`git ls-remote --heads origin 'agent/*'` first.

**Blocked, and why.**
- WP-0006 — waits on `docs/open-questions.md` → box-colour (the maintainer's call).
- WP-0014 — waits on `docs/open-questions.md` → structural-recommendations.

**Watch out.** `uv run tools/screenshot.py <view> --do all --do fit` now prints
the overlapping pairs; a build package should end with 0 in the fully open state.
Every pull request links its preview as a complete clickable URL
(`https://graph.med/preview/pr<N>/<view-id>/`).
