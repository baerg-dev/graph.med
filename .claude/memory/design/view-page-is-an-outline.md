---
name: view-page-is-an-outline
description: The view page is an outline tree opened step by step (source → chapters → statements → concepts), not a force-directed drawing of every member; types differ by form.
metadata:
  type: project
---

A view page on the site is an **outline tree** — source, chapters, statements,
concepts — opened one level at a time by tapping, with a node's details in the
section below the graph. It is not a drawing of every member of the view at once.
Node types differ by **form** (square, hexagon, circle, diamond) and edge types by
line style, not by colour alone. Decided 2026-09-06; applied in
`docs/publication.md` §3 and `tools/build.py`.

**Why:** The first published page drew all 209 members of the POMGAT view as one
force-directed graph. The maintainer read it on a phone and found it too dense to
read, and asked for a minimal, browsable, zoomable page with a tree-like outline
and types told apart by form. Progressive disclosure answers the density; the
outline gives an entry point (the chapter) without adding chrome; forms survive
colour-blindness and dark mode. The detail section below the graph was kept as it
was — the maintainer said it "really works well on the phone".

**How to apply:** Keep the page an outline that discloses progressively; do not
reintroduce an all-at-once layout or a layout simulation in the client. Add
information to the section below the graph rather than to the graph. A chapter is a
derived display grouping for one-source views (from the claims' recommendation
numbers), computed by the build and never stored in the pool.
