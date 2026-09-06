---
name: view-page-is-a-decision-graph
description: The view page is a decision graph per chapter — patient group → condition → recommendation (coloured by grade) → aim — laid out top-down; never an all-at-once drawing and not an outline.
metadata:
  type: project
---

A view page on the site is a **decision graph, one per chapter**: diamonds for
patient groups (population slot), hexagons for conditions, boxes for
recommendations coloured by the guideline's grade, tags for aims; laid out
top-down by the build; one chapter open at a time; a node's details in the
section below the graph. Decided 2026-09-06 after two rejected forms; applied in
`docs/publication.md` §3 and `tools/build.py`.

**Why:** The maintainer read the first two published forms on a phone. The
force-directed drawing of all 209 members was "too dense to read". The outline
tree that replaced it was "more like a table of contents". What they asked for,
with an example page in hand, was "a decision tree like representation that
helps physicians and academics": shapes by node type, colour by recommendation
class, a layered top-down flow with branches, details on tap. The section below
the graph was kept as it was — it "really works well on the phone".

**How to apply:** Keep the page a decision graph read top-down; keep the node
forms and the grade colours; keep one chapter at a time as the entry point. Do
not reintroduce an all-at-once layout, a client-side simulation, or a list-shaped
page. The graph is *derived* from slots until pathways are authored
(`docs/open-questions.md` → decision-graph-derivation); do not invent branch
labels or ordering the data does not carry. Add information to the section below
the graph rather than to the graph.
