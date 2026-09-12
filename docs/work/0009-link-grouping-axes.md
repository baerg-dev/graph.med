---
id: link-grouping-axes
initiative: groupings
kind: linking
depends_on: [schema-grouping-axes]
---

## Outcome

The second axis decided in `grouping-axes-decision` is asserted on every patient
group of `pomgat-lv-1.0` that the rule places: edges with a `modelling` rationale
in `data/edges/pomgat-lv-1.0/grouping-axes.yaml`, family concepts minted where the
axis needs them (with facet and label, source language), no statement moved. A
group the rule cannot place is listed in the PR, not forced.

## Scope

In: `data/edges/pomgat-lv-1.0/`, new files under `data/concepts/` for families.
Out: the first axis (already asserted as `broader`) except where the decision
re-reads it; the site.

## Constraints

Spec §11 (search before minting, nothing inherited, no review status written);
memory `concept-hierarchy-depth` (as deep as subsumption goes; families are
concepts without a parent on that axis); short labels above ~45 characters
(memory `short-label-limit`).

## Verification

Validator passes; the PR lists every group with its family per axis as a table,
and the groups left unplaced with the reason.
