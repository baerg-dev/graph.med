---
id: WP-0002
title: "Nothing overlaps: every node and answer readable"
status: done
created: 2026-09-12
updated: 2026-09-12
depends_on: []
blocks: [WP-0003]
owner: agent
initiative: ui
kind: build
slug: site-layout-visibility
---

## Outcome

Nothing overlaps in any state the reader can reach. With a large family open
(Operation eines gastrointestinalen Tumors, Kolorektale Chirurgie) every answer on
an edge is legible and every box is clear of its neighbours. Today, answers written
at the end of their edges run into each other and into the boxes beside them.

## Scope

In: the layout parameters and label placement in `tools/site/static/graph.js` and
the styles in `tools/site/static/site.css`; if placing text on the edge cannot hold,
answers drawn as nodes of their own.
Out: the shape of the tree (one tree, left to right, folded by default), the node
forms, the colours.

## Constraints

- `docs/publication.md` §3 "Everything readable" and the memory
  `view-page-is-a-decision-tree`: the tree stays one tree; do not hand-write layout.
- Cytoscape.js and dagre stay vendored and pinned.

## Decisions

- 2026-09-12 (agent): the answers stay on the edges; the fallback of answers as
  nodes of their own was not needed. The overlaps had one cause: the answer is
  anchored where the arrow meets the target's boundary, but its offset was
  computed as if anchored at the target's centre, so every answer sat 130 px too
  far left, over the rank before. The offset is now half the label's estimated
  width plus a 10 px gap, so the label ends just before the arrow and, with the
  rank separation of 230 px, never reaches the previous rank.
- 2026-09-12 (agent): a group reached from two open parents (Minimalinvasive
  kolorektale Resektion) names its answer once; the second edge's label is blank
  while both are shown, since both would sit on the same spot.
- 2026-09-12 (agent): "fit" fits into the part of the canvas the floating
  controls do not cover — below the search row, above the legend — so no node
  sits under a control after a fit, on the phone in particular.
- 2026-09-12 (agent): "nothing overlaps" is checked mechanically: the screenshot
  driver reports every pair of shown nodes and answers whose boxes intersect, and
  gained `all` (every group open, one tap at a time) and `fit` actions to reach
  the extreme states.

## Open questions

None.

## Verification

Browser captures before and after, desktop and phone, of the two families named
above fully open, in the pull request. `uv run tools/build.py` succeeds.
