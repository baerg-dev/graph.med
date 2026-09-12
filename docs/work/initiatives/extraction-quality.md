---
id: extraction-quality
title: Extraction quality
---

From the physician's review: the body-text relations (`refines`, `supplements`,
`limits`) are read heterogeneously across chapters, contextual criteria are
sometimes incomplete (the amylase criterion refining 6.7 lacks the alternatives
the text gives beside it), and recommendations of a structural or organisational
kind — which a physician on the ward cannot act on — are not told apart.

**Scope.** A written rule per body-text relation in the spec, then linking passes
over the existing claims and edges of `pomgat-lv-1.0`, chapter by chapter, each
change `modelling` and checked against the quotes; the marker for structural
recommendations once `docs/open-questions.md` → structural-recommendations is
settled. Claims are immutable: a correction is a new claim and an edit with
history (spec §7), never a rewrite.

**Out of scope.** New sources; evidence profiles and quality indicators
(`LATER.md`); anything on the site — the site reads what these packages fix.
