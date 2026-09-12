---
id: site-question-at-every-branch
initiative: ui
kind: build
depends_on: [site-layout-visibility]
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

## Verification

Build; the view JSON has no edge from a junction directly to a junction. Browser
captures of a family opened, desktop and phone, in the pull request.
