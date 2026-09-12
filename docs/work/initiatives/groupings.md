---
id: groupings
title: Grouping axes and specialised views
---

From the physician's review: the `broader` hierarchy is to be *defined*, not to
emerge; families should be choosable by more than one axis — the outline, the
anatomical region, the operative phase; and there should be specialised looks
that hide aspects ("show me every node that …").

**Scope.** First a design decision (`docs/open-questions.md` → grouping-axes,
view-filter-language), then the schema shape it needs, then the axes asserted on
the first source, then the site. `broader` stays an edge with provenance (memory
`relations-are-edges-not-fields`); the outline stays provenance and a filter, never
an axis (memory `document-structure-is-provenance`); views stay fixed filter forms
(open question view-filter-language).

**Out of scope.** A query language; authored pathways (open question
decision-graph-derivation); the phase vocabulary as such (open question
phase-vocabulary — decided inside the first package here if the operative phase is
chosen as an axis).
