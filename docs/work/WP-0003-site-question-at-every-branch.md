---
id: WP-0003
title: A question diamond at every branching of the tree
status: open
created: 2026-09-12
updated: 2026-09-12
depends_on: [WP-0002]
blocks: [WP-0004]
owner: unassigned
initiative: ui
kind: build
slug: site-question-at-every-branch
---

## Outcome

Wherever the tree forks, the reader passes a question. An opened family shows
"Welche Population?" between its junction and its member groups; today it fans
straight into them with answers on the edges and no diamond, which the physician
read as a branch without a decision. The family's own recommendations keep hanging
from its junction, through "Welche Bedingung?" where they have a condition. Folding,
the counts on junctions and deep links behave as before; the question folds with
the family.

## Scope

In: the tree derivation in `tools/build.py` (`decision_tree_of`) and the folding
logic in `tools/site/static/graph.js`.
Out: any new question text — "Welche Population?" is reused; a different wording
("Welcher Eingriff?") is a design decision for the maintainer, not this package.

## Constraints

- `docs/publication.md` §3 "Every branching is a question" and "The questions are
  ours; every answer is data".
- The build adds no text it does not already have (`QUESTIONS` in `build.py`).

## Decisions

None yet. Append only; architectural ones go to `docs/adr/`, knowledge-model ones to `.claude/memory/design/`.

## Open questions

None.

## Verification

Build; the view JSON has no edge from a junction directly to a junction. Browser
captures of a family opened, desktop and phone, in the pull request.
