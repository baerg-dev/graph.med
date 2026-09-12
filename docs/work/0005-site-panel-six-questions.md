---
id: site-panel-six-questions
initiative: ui
kind: build
depends_on: []
---

## Outcome

A statement's detail section is organised by the six questions a reader brings,
each a heading in the chrome language, in this order: what should I do; does this
apply to my patient; how binding and how well supported is it; what could change
the answer; where exactly is it written; would the answer be different in a
neighbouring situation. The same template renders the entity page. Concepts and
claims keep their sections.

## Scope

In: `tools/site/templates/details.html`, the `details()` data in `tools/build.py`
(the sixth question needs the statements under the same group and condition, the
same action in other groups, and the specializes / complements / conflicts edges),
`tools/site/static/site.css`.
Out: an evidence level per claim — the schema has none; it arrives only with
`docs/open-questions.md` → evidence-profiles. The colour of anything.

## Constraints

`docs/publication.md` §3 "What the section shows" is the specification, item by
item; grades are shown per claim, never composed. Chrome is English, content stays
in its source language with `lang` set.

## Verification

Browser captures of one statement's section on desktop and phone, and of its entity
page, in the pull request. Build succeeds; every statement page renders all six
headings.
