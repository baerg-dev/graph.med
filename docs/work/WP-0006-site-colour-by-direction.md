---
id: WP-0006
title: Boxes coloured by direction, grade as a letter
status: blocked
created: 2026-09-12
updated: 2026-09-12
depends_on: [WP-0005]
blocks: []
owner: unassigned
initiative: ui
kind: build
slug: site-colour-by-direction
---

## Outcome

Boxes are coloured as `docs/open-questions.md` → box-colour decides. If the
decision is colour by direction: a box takes the four direction colours (the
banner's), the grade is written in the box after the glyph (A · B · 0 · EK), an EK
box is coloured by its direction like every other recommendation and carries "EK"
as its grade text, and the legend explains colours as directions and letters as
grades.

## Scope

In: `tools/site/static/site.css`, `tools/site/static/graph.js`, the legend in
`tools/site/templates/view.html`; the memory `view-page-is-a-decision-tree` and
`docs/publication.md` §3 amended in the same pull request.
Out: the direction derivation itself (memory `direction-legend`).

## Constraints

- Do not start until box-colour is settled; if the decision goes another way, do
  what it says instead.
- Colours light enough for dark text in both themes (see the variables in
  `site.css`).

## Open questions

`docs/open-questions.md` → box-colour (gates this package).

## Decisions

None yet. Append only; architectural ones go to `docs/adr/`, knowledge-model ones to `.claude/memory/design/`.

## Verification

Browser captures of a family open, desktop and phone, light and dark, in the pull
request; the legend readable on a phone. Build succeeds.
