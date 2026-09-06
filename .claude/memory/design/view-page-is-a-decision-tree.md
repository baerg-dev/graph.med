---
name: view-page-is-a-decision-tree
description: The view page is one decision tree — which patient group? → which condition? → recommendation (coloured by grade) → aim, answers on the edges — drawn top-down by Cytoscape.js + dagre; not chapters, not an outline, not an all-at-once drawing.
metadata:
  type: project
---

A view page on the site is **one decision tree**: a root, a question "Which patient
group?" whose answers sit on the edges, a junction per group, an optional "Which
condition?" with its answers on the edges, the recommendations as boxes coloured
by the guideline's grade, aims as tags. Drawn top-down by Cytoscape.js with the
dagre layout, self-hosted; a node's details in the section below the graph.
Decided 2026-09-06 after three rejected forms; applied in `docs/publication.md`
§3 and `tools/build.py`.

**Why:** The maintainer read the earlier forms on a phone. The force-directed
drawing of everything was "too dense"; the outline tree was "more like a table of
contents"; the per-chapter layered graph was close but they wanted "one graph, no
chapters", asked "why is it not a decision tree like structure? it's a leitlinie",
expected labels on the edges, and saw labels that did not fit the boxes — "is
there no library we can use to solve all this". They liked the 2D pan-and-zoom
view where "nothing is dense, nothing overlays", and the detail section below the
graph throughout. A library that measures text, lays out a DAG without overlaps,
and places edge labels answers all of it; self-hosting keeps the site free of
third-party requests.

**How to apply:** Keep one tree for the whole view; keep the answers on the
edges and the questions as the only text the build adds; keep the grade colours
and the node forms; keep Cytoscape.js + dagre vendored and pinned. Do not split
the page by chapter, reintroduce an outline, or hand-write layout again. The tree
is *derived* from slots until pathways are authored (`docs/open-questions.md` →
decision-graph-derivation); never invent yes/no branches or an ordering the data
does not carry. Add information to the section below the graph rather than to
the graph.
