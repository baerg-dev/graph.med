---
id: relink-body-text-a
initiative: extraction-quality
kind: linking
depends_on: [body-text-relations-rule]
---

## Outcome

Chapters 4–6 of `pomgat-lv-1.0` (claim files `ch04`, `ch05`, `ch06`) follow the
body-text rule: every `refines`, `supplements` and `limits` edge is one the rule
produces, missing ones are added with their claims, wrong ones are superseded
with history. The amylase criterion refining box 6.7 (p. 64) carries the
alternatives the text gives beside it (day 1 and 3 with the drain volume, three
times the serum concentration on day 3) in the shape the rule prescribes.

## Scope

In: `data/claims/pomgat-lv-1.0/ch04.yaml`, `ch05.yaml`, `ch06.yaml`,
`data/edges/pomgat-lv-1.0/` for those chapters; pages 26–74 of the source.
Out: chapters 7–9 (`relink-body-text-b`); the site.

## Constraints

Every quote verbatim on its physical page (`uv run tools/validate.py
--verify-quotes` must pass); claim ids hashed by script; every new edge
`modelling` with a rationale; nothing the text does not state.

## Verification

Both validator forms pass; the PR lists each edge added, superseded or kept,
with the rule clause that decided it.
