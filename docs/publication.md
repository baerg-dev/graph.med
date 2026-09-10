# Publication — how the pool is served at graph.med

> **Status: design, built in part.** The build (`tools/build.py`, `CLAUDE.md`
> "Build") renders §2–§5 for `selection` views over sources: the URL layout, the
> graph-and-sheet page, entity pages and JSON, source links. Not built yet, and
> registered as chunks of the current pass in `data/PROGRESS.yaml`: the chapter
> tree and the search (§3, "Chapters and search"), short labels in the boxes, the
> direction legend and the order of the detail section (§3, "What the section
> shows"), and the grouping of patient groups by `broader` edges. Not built and
> not registered: the deploy workflow until a person commits it (§6), cuts (§7),
> pathway views, and everything under §8. The domain `graph.med` points at GitHub Pages. This document fixes what
> the site is *meant* to be so that the build is written to it, not the other way
> round. It is the design-level counterpart of
> `graph-representation.md`: that file says how knowledge is stored; this one says
> how it is shown.

---

## 1. One sentence

The pool is published as a **static site**: every **view** is a page at
`graph.med/<view-id>`, every **entity** is a page and a JSON document at its own
identifier, both generated from `data/` by a build script on every change to `main`
and served by GitHub Pages behind the `graph.med` domain; the primary page is a
**graph** that is read on a **phone first**, where tapping a node opens its details
in a **section below the graph**.

---

## 2. URLs are the identifiers

`graph-representation.md` §2 says identity is the URL and the schema's `$id` already
begins with `https://graph.med/`. Publication makes that literal: every identifier in
the pool resolves.

```
graph.med/                          index: the views, the sources they draw on
graph.med/<view-id>                 a view, floating — the filter as of the last build
graph.med/<view-id>@<n>             a cut of that view (deferred, §7)
graph.med/<namespace>/<entity-id>   any entity: statements/…, concepts/…, claims/<source>/<hash>, sources/…
graph.med/<namespace>/<entity-id>.json   the same entity as data
graph.med/schema/schema.yaml        the schema, at its $id
```

Views live at the root because they are the citable things and the pages people
share. Entities live under their namespace exactly as in the pool. The one rule
this adds to the data model: **a view id must not equal a namespace name**
(`sources`, `claims`, `concepts`, `statements`, `pathways`, `views`, `agents`,
`attestations`, `schema`, or a terminology namespace). The validator enforces it.

**Base path.** The site can also be served without the domain, at
`baerg-dev.github.io/graph.med/`. The build takes the base path as a parameter and
generates every internal link from it, so moving between the two is configuration,
never a content change.

A **graph id**, as the maintainer calls it, is therefore a view id. The first views
are one per source document, e.g. `graph.med/pomgat-lv-1.0` for the POMGAT guideline:
a `selection` view whose filter is that one source. A view is a data entity
(`data/views/<view-id>.yaml`, schema `view`); adding a graph to the site is a reviewed
data change, never a change to the build.

---

## 3. A view page: a graph and a sheet

The view page is designed for a phone first and kept minimal: one graph, one
detail section, nothing else competing for the screen. Desktop gets the same page
with more room.

**The graph is one decision tree.** The page is for physicians and academics, who
read a guideline as decisions: which patients, under which condition, which
recommendation, to what end. So the whole view is drawn top-down as a decision
tree, derived from the statements' slots — the pool has no authored pathways yet,
and this derivation is the stand-in until it does (`open-questions.md` →
decision-graph-derivation):

```
   ┌─────────────────────┐
   │ the guideline       │                       root
   └─────────┬───────────┘
        ◇ Which patient group?                   question (ours)
       ╱ Gastrektomie ╲ Kolorektale Resektion …  answers on the edges (population slot)
      ●                ●                          junction per group
      │                ├──── ◇ Which condition?  question (ours)
      │                │       ╲ Amylase < …     answer on the edge (condition slot)
   ┌──┴────────┐   ┌───┴───────┐ ┌───┴───────┐
   │ recommend.│   │ recommend.│ │ recommend.│    the statements — boxes coloured by
   └─────┬─────┘   └───────────┘ └───────────┘    grade (A · B · 0 · EK), red border
         ┆ (dashed)                               when *against*, dashed red when contested
         ▷ aim                                    outcome slot
```

- **The questions are ours; every answer is data.** "Which patient group?" and
  "Which condition?" are the only text the build adds. Each answer on an edge is a
  population or condition concept; each box is a statement with its claims' grade;
  each aim an outcome concept. Nothing else is invented — in particular no yes/no
  branches and no ordering between conditions, which is what authored pathways will
  add (`graph-representation.md` §5, `branch` edges with a `guard`).
- **Patient groups converge.** Statements sharing a population hang from one
  junction, so the tree shows at a glance what the guideline says for, say,
  colorectal resection. A condition is asked within its group.
- **Forms tell the types apart, colour tells the grade.** Diamond, box, tag for
  question, recommendation, aim; the answers are bold edge labels, the aim a dashed
  edge; the grade colours are the guideline's own scale. Legend under the graph.
  Claims are not nodes; they are the evidence and appear in the section.

**Drawn by a library, left to right, folded.** The page uses Cytoscape.js with the
dagre layout, self-hosted under `assets/vendor/` (MIT, pinned, no third-party
request): boxes have a fixed width and grow to their wrapped text, the layered
layout has no overlaps, edge labels are placed, and touch pan and pinch come with
it. Three choices keep the tree readable at ninety recommendations:

- **Left to right.** A rank is a column, so the widest rank becomes a tall column
  that pans vertically — natural on a phone and on a desktop — and the whole tree is
  seven columns wide.
- **Folded by default.** The page opens with the root, the first question and its
  answers, one junction per patient group carrying the number of recommendations
  behind it. Tapping an answer or its junction unfolds that group's conditions and
  recommendations; tapping again folds it. Only what the reader opened takes space.
  A deep link unfolds the group its target is in.
- **Answers in order of weight.** The patient groups with the most recommendations
  come first, so the general ones lead and the single-use ones trail. A real
  hierarchy of groups — organ, then procedure — shrinks the fan-out further: once
  concepts carry `broader` edges (`graph-representation.md` §5), an answer is a
  family (*Leberresektion*) that unfolds into its members, and the thirty-odd
  groups become eight to ten. The edge only groups and folds; it never moves a
  recommendation from a family to a member.

**Boxes show the short form.** A box shows a statement's `short_label` when it
has one and its `label` otherwise; the section always shows the full label. The
same holds for the answers on the edges (concepts). Short labels are data, reviewed
like everything else, never truncated by the build.

The data carries no positions; the layout is deterministic for a given set of open
groups. This replaces the earlier hand-written renderer, whose fixed boxes could not
fit the labels.

**The interaction.** Pan by one finger, pinch or wheel to zoom, a fit button for
what is open. Tapping a node or an answer selects it: what leads to it and what
follows it stay, everything else fades, and its details open in the **section
below the graph** — on a wide screen, in a **column beside it**, the graph taking
the full height; the graph stays where it is either way, so the reader keeps their
place. Tapping the background clears. Tapping a neighbour listed in the section
moves there. Deep links carry `#<entity id>`. There are no modal dialogs and no page
loads needed to read a view; the entity pages (§4) exist for linking, not for reading.

**Chapters and search.** Two ways to narrow the tree, deliberately different in
kind:

- **A chapter tree beside the graph**, built from the source's `outline` and the
  claims' `section` (`graph-representation.md` §6.7). Tapping a section is a
  *hard filter*: the tree shows only the statements supported from that section
  and its subsections, plus their groups, conditions and aims; nothing is redrawn
  and no edge is computed, the rest is simply not shown. Sections without a claim
  are listed greyed, so the reader sees what the pool has not extracted. The
  chapter tree is a control, not the graph: the graph stays the one decision tree,
  and the tree of headings never becomes its shape.
- **A search box** is a *soft highlight*: it matches the label, short label and
  claim text of statements and concepts; matches keep their colour and everything
  else fades without disappearing, so "Leber" shows every branch the liver occurs
  in and, just as usefully, where it does not. A counter reads "n matches in m
  sections". Hiding would destroy the overview the search exists to give; fading
  keeps the structure.

Once concepts carry a `facet`, the search gets facet filters (only procedures,
only outcomes). Everything here runs in the browser on the view's JSON.

**Direction, in four words.** The legend shows a recommendation's direction as one
of *für*, *gegen*, *abwägen*, *Lücke* — derived at build time from the supporting
claims (`direction: against` → gegen; `kind: gap_notice` → Lücke; the mapping of
`kann` to *abwägen* is open, `open-questions.md` → direction-legend) — next to the
grade colours. Timing ("innerhalb von 24 Stunden") is not a direction; it stays in
the label.

**What the section shows.**

- *statement*, in this order: the direction as a banner, so the clinical answer is
  read in a second; the full label, in its source language; the slots with their
  concepts; every claim linked to it by `supports` or `contests` — each with
  **its own grade** highlighted, then verb, direction and consensus, its
  recommendation number, page and section, the verbatim quote, and a link to the
  cited page of the source (§5); last, what the body text adds, grouped by
  relation — *refines*, *supplements*, *limits* — each with its page. The order
  goes from the answer to its evidence to its limits.
- *concept*: the label and definition, the statements that use it and in which slot,
  and its codes (`codes_as`) once terminology imports exist.
- *structural node*: its label, its branches or outcomes, and the statements it is
  about.

**Grades are shown, never composed.** A statement's effective grade is an open
question (`open-questions.md` → grade-derivation) leaning toward showing the
distribution. The page shows each claim's grade next to that claim and nothing on
the statement. When the question is settled, the page follows the schema.

**Language.** Content is rendered in its source language with the `lang` attribute
set; nothing is translated. Chrome (navigation words) is English. Translation is a
build-layer concern and can be added without a data change
(`graph-representation.md` §2).

---

## 4. Entity pages and JSON

Every entity gets a page whose content is the same as its sheet section, so that
`graph.med/statements/<id>` is a working link from anywhere, and a JSON document
next to it that carries the entity as stored plus its incoming and outgoing edges
resolved to ids. The JSON is what a program uses; the page is what a person lands
on. Both are generated; neither is authored.

---

## 5. Sources are linked, never served

The site never hosts a source document
(`.claude/memory/design/sources-referenced-never-rehosted.md`). A claim's locator
becomes a link to the source's public URL with the page fragment,
`<url>#page=<N>`, so a reader lands on the cited physical page; the verbatim quote
is shown beside it so the passage can be found. The source's license line, as
recorded on the source entity, is shown on its page and on every view drawn from it.

---

## 6. The build

The build is a script in the repository, `tools/build.py`, run with `uv` like the
validator. It reads `data/` and `schema/schema.yaml`, writes a `site/` directory
(gitignored), and takes the base path and output directory as parameters. It runs
offline, needs nothing beyond the dependencies in `pyproject.toml`, and is
deterministic. A contributor runs it locally and opens `site/index.html` to see a
change before proposing it — the same habit as the validator.

Publication is a workflow: on every push to `main`, validate, build, deploy to
GitHub Pages. The deploy step never runs on a pool that fails validation. Workflow
files are human-only (`.claude/rules/environment/git-identity.md`), so the build
tooling arrives in a pull request and the workflow that calls it is committed by a
person from the pull request's description. The build emits the `CNAME` file for the
domain and a `.nojekyll` marker so that paths are served untouched.

---

## 7. Floating first, cuts later

A floating view is rebuilt on every change to `main`; its page says which commit it
was built from. A **cut** (`graph-representation.md` §4) is a frozen, validated
member list recorded on the view entity, and `graph.med/<view-id>@<n>` serves that
cut from its `as_of` commit forever. Cuts are what get cited. They are deferred until
someone needs to cite one; how the build serves old cuts, and whether a cut also
gets a single-file export such as a PDF, are open (`open-questions.md` →
cut-publication).

---

## 8. Left open

- **Cut publication** — how cuts are built and served alongside the floating view;
  whether a cut has a PDF export.
- **Branch guards** — yes/no and value-range branches come with authored pathways
  (`branch` edges carry a `guard`); the derived tree has only slot answers.
- **Translation** — a build-layer projection, not started.
- **Other projections** — FHIR, RDF, diagram formats (`graph-representation.md` §13).
