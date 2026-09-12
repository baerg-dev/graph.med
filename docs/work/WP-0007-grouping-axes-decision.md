---
id: WP-0007
title: Decide the grouping axes and their schema shape
status: open
created: 2026-09-12
updated: 2026-09-12
depends_on: []
blocks: [WP-0008]
owner: unassigned
initiative: groupings
kind: docs
slug: grouping-axes-decision
---

## Outcome

`docs/open-questions.md` → grouping-axes is settled and gone: the spec
(`docs/graph-representation.md` §5) says which axes group patient groups into
families, the rule for each, and the schema shape — an `axis` on `broader`, or
one edge kind per axis — with a memory under `.claude/memory/design/` recording
why. If the operative phase is an axis, → phase-vocabulary is settled with it.
The follow-up packages of this initiative are checked against the decision and
the pull request says which of them change.

## Scope

In: `docs/graph-representation.md` §5 and §3.2, `docs/open-questions.md`, one
memory and its index row; the 36 patient-group concepts and 10 families of
`pomgat-lv-1.0` as the test material (read them; change nothing under `data/`).
Out: the schema, the validator, any edge — those are `schema-grouping-axes` and
`link-grouping-axes`.

## Constraints

- `broader` is first class: an edge with provenance, never a field (memory
  `relations-are-edges-not-fields`); it inherits nothing.
- The outline is provenance and a filter, never an axis (memory
  `document-structure-is-provenance`).
- One hierarchy per axis is the current leaning; overturn it only with a
  reason stated in the memory.

## Open questions

`docs/open-questions.md` → grouping-axes (this package settles it);
→ phase-vocabulary (settled with it if the phase becomes an axis);
→ view-filter-language (respected, not settled).

## Decisions

None yet. Append only; architectural ones go to `docs/adr/`, knowledge-model ones to `.claude/memory/design/`.

## Verification

The entry is deleted, the spec section reads as a rule a linking session can
apply without asking, the memory is indexed, the validator passes. The PR names
the two candidate concepts hardest to place under each axis and where the rule
puts them.
