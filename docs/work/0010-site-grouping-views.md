---
id: site-grouping-views
initiative: groupings
kind: build
depends_on: [link-grouping-axes, site-fold-and-reset]
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

## Verification

Browser captures on desktop and phone of the tree under each axis and of one
specialised view; the PR links the previews. Build and validator pass.
