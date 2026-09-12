---
id: body-text-relations-rule
initiative: extraction-quality
kind: docs
depends_on: []
---

## Outcome

`docs/graph-representation.md` §5 states, for each of `refines`, `supplements`
and `limits`, a rule an extraction session can apply without judgment calls:
what kind of passage earns which relation, what its claim's `kind` is, how a
criterion with alternatives is captured (one claim per alternative, or one claim
quoting the whole criterion — decided here), and what is *not* a body-text
relation. The rule is checked against the 101 existing claims of
`pomgat-lv-1.0`: the PR lists every existing edge the rule would change, as the
brief for the two relinking packages.

## Scope

In: `docs/graph-representation.md` §5 (and §3.1 if the claim kinds need a word),
the `next-work-package` skill's extraction section if it must say more.
Out: any change under `data/` — that is `relink-body-text-a` and `-b`.

## Constraints

Claims are immutable and never merged (spec §3.1); a wrong relation is fixed by
a new edge and an edit with history, never by rewriting a claim. Underestimate,
never upgrade (spec §11).

## Verification

The rule fits on one screen; a second reader applying it to chapter 6 gets the
same edges — say in the PR how you checked that. Validator passes.
