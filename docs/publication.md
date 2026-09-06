# Publication — how the pool is served at graph.med

> **Status: design, built in part.** The build (`tools/build.py`, `CLAUDE.md`
> "Build") renders §2–§5 for `selection` views over sources: the URL layout, the
> graph-and-sheet page, entity pages and JSON, source links. Not built: the deploy
> workflow until a person commits it (§6), cuts (§7), pathway views, and everything
> under §8. The domain `graph.med` points at GitHub Pages. This document fixes what
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

**The graph is an outline tree**, opened step by step. The first published page drew
every member of the view at once — 209 nodes — and was unreadable on a phone; a graph
that is browsed has to disclose itself progressively. So the page is a tree:

```
▢ source
  ⬡ chapter · count
    ● statement
      ◆ population · concept
      ◆ action · concept
    ● statement …
```

- **Root and chapters.** The source is the root; its chapters are the first level. A
  statement's chapter is derived from the recommendation numbers of its claims
  (6.3 → chapter 6) — a display grouping for one-source views, computed by the
  build, never stored.
- **Statements** sit under their chapter, ordered by recommendation number; a
  contested statement is drawn red. **Concepts** sit under each statement that uses
  them, with the slot named on the connector, so a concept shared by several
  statements appears under each of them; its section lists all its uses.
- **Cross-statement relations** (`specializes`, `complements`, `conflicts`) are drawn
  as dashed arcs on the right when both statements are open. Claims are not nodes;
  they are the evidence and appear in the section.
- **Forms tell the types apart**, not colour alone: source a square, chapter a
  hexagon, statement a circle, concept a diamond; containment a solid grey
  connector, a slot fill a solid green one, a relation a dashed blue one. A legend
  sits under the graph.

The layout is the outline order — row is y, depth is x — computed at render from
what is open; no simulation, no positions in the data, so two builds of the same
commit draw the same picture and the client script stays small and dependency-free.

**The interaction.** The page opens with the source and its chapters. Tapping a
shape opens or closes it; tapping a label selects the node and opens its details in
the **section below the graph**; the graph stays where it is, so the reader keeps
their place. Each step animates the viewport to fit what just opened. Pan by one
finger, pinch or wheel to zoom, and two buttons — fit to what is open, collapse to
the chapters. Tapping a neighbour listed in the section moves the selection and
reveals the path to it. There are no modal dialogs and no page loads needed to read
a view; the entity pages (§4) exist for linking, not for reading.

**What the section shows.**

- *chapter*: its statements, each a link into the outline.
- *statement*: the label, in its source language; the slots with their concepts;
  every claim linked to it by `supports` or `contests` — each with its
  recommendation number, **its own grade**, verb and direction, the verbatim quote,
  and a link to the cited page of the source (§5).
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
- **Search** — the outline gives an entry point by chapter; finding a statement by
  word is not built.
- **Translation** — a build-layer projection, not started.
- **Other projections** — FHIR, RDF, diagram formats (`graph-representation.md` §13).
