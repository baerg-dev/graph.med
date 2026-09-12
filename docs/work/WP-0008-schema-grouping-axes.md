---
id: WP-0008
title: Schema and validator for grouping axes
status: open
created: 2026-09-12
updated: 2026-09-12
depends_on: [WP-0007]
blocks: [WP-0009]
owner: unassigned
initiative: groupings
kind: schema
slug: schema-grouping-axes
---

## Outcome

`schema/schema.yaml` and `tools/validate.py` express the decided shape of
grouping axes (spec §5 as settled by `grouping-axes-decision`): an axis on
`broader`, or one edge kind per axis, with the validator rejecting a cycle within
an axis and an edge whose axis is not declared. The existing data stays valid
without change.

## Scope

In: `schema/schema.yaml` (version bump), `tools/validate.py`, `data/README.md`
if the layout gains anything, the schema's own `x-` conventions.
Out: asserting any edge; the site.

## Constraints

- Additive: every existing `broader` edge remains valid, read as the anatomical
  axis or whatever the decision names as the default.
- The schema commit lands before any data that uses it (spec §7).

## Decisions

None yet. Append only; architectural ones go to `docs/adr/`, knowledge-model ones to `.claude/memory/design/`.

## Open questions

None.

## Verification

`uv run tools/validate.py` passes on the unchanged data; a deliberately wrong
edge (undeclared axis, a cycle within one axis) is rejected — show both in the
PR.
