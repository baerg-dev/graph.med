---
id: WP-0002
title: "Nothing overlaps: every node and answer readable"
status: open
created: 2026-09-12
updated: 2026-09-12
depends_on: []
blocks: [WP-0003]
owner: unassigned
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

None yet. Append only; architectural ones go to `docs/adr/`, knowledge-model ones to `.claude/memory/design/`.

## Open questions

None.

## Verification

Browser captures before and after, desktop and phone, of the two families named
above fully open, in the pull request. `uv run tools/build.py` succeeds.
