---
id: WP-0010
title: Axis switch and the first specialised views on the site
status: open
created: 2026-09-12
updated: 2026-09-12
depends_on: [WP-0009, WP-0004]
blocks: []
owner: unassigned
initiative: groupings
kind: build
slug: site-grouping-views
---

## Outcome

The reader can choose the axis the first question's answers are grouped by
(anatomical region, operative phase, … as decided), and the site offers the
specialised views the initiative asked for as fixed filter forms
(`docs/graph-representation.md` §4, open question view-filter-language): a view
that hides an aspect is a view entity under `data/views/` with its own page,
never a query typed into the page. `docs/publication.md` §3 says how the axis
switch looks and where it sits.

## Scope

In: `tools/build.py` (the tree derivation takes the axis), `tools/site/`,
`docs/publication.md` §3; one or two view entities under `data/views/` as the
first specialised views, agreed in the PR.
Out: a query language; the search and facet filters beyond what they do.

## Constraints

Memory `view-page-is-a-decision-tree`: one tree, left to right, folded; the axis
changes which concepts are families, never the shape. Views are data
(memory `pool-and-views`).

## Decisions

None yet. Append only; architectural ones go to `docs/adr/`, knowledge-model ones to `.claude/memory/design/`.

## Open questions

None.

## Verification

Browser captures on desktop and phone of the tree under each axis and of one
specialised view; the PR links the previews. Build and validator pass.
