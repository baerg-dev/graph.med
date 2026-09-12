---
id: WP-0003
title: A question diamond at every branching of the tree
status: review
created: 2026-09-12
updated: 2026-09-12
depends_on: [WP-0002]
blocks: [WP-0004]
owner: agent
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

- 2026-09-12 (agent): the question is a node of the build, not of the browser:
  `decision_tree_of` inserts `q:<junction>:population` (a `question` node with
  the view's own "Welche Population?") between a junction and its member groups
  whenever it has any; the condition question is `q:<junction>:condition` for
  symmetry (it was `q:<junction>`). No id of a question is linked from anywhere.
- 2026-09-12 (agent): a junction is built once and its question and members
  with it; a group with two parents gets a second answer edge into the same
  junction, never a second question or subtree.
- 2026-09-12 (agent): folding stops at a question whose answers are groups: an
  open junction shows its own question with the member junctions folded behind
  it, and follows a condition question through to its recommendations and aims
  as before.

## Open questions

None.

## Verification

Build; the view JSON has no edge from a junction directly to a junction. Browser
captures of a family opened, desktop and phone, in the pull request.
