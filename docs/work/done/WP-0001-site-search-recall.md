---
id: WP-0001
title: The search finds every node the chapter tree finds
status: done
created: 2026-09-12
updated: 2026-09-12
depends_on: []
blocks: []
owner: agent
initiative: ui
kind: build
slug: site-search-recall
---

## Outcome

Every node the chapter tree can reach, the search box finds: a statement by its
label, short label, any slot concept's label or a word from a claim's quote; a
patient group by its label; a condition by its answer on the edge. Matching ignores
case and diacritics ("osophagus" finds Ösophagus). The counter and the fading are
unchanged.

## Scope

In: the search index the build writes into the view JSON (`text` on nodes, and on
answer edges), and the matching in `tools/site/static/graph.js`.
Out: the chapter tree, the facet filter, any change to what fades or how; a search
inside the chapter tree (`docs/open-questions.md` → chapter-search).

## Constraints

- `docs/publication.md` §3 "A search box" is the specification: a soft highlight,
  never hiding.
- No data change: everything comes from labels, short labels and claim text
  already in the pool.

## Decisions

- 2026-09-12 (agent): case and diacritics are folded in the browser, on both the
  index and the query (NFD, combining marks stripped, ß as ss, lowercased), so the
  rule lives in one place and the view JSON keeps the text as written; the build no
  longer lowercases `text`.
- 2026-09-12 (agent): an answer on an edge matches the node it leads to — a node
  matches by its own text or by the text of an answer edge into it. The counter
  goes on counting nodes and the fading is unchanged: the edge keeps its colour as
  a connected edge of a match.
- 2026-09-12 (agent): the statement's index carries its slot concepts' short
  labels (the words on the box and the edge) and its claims' quotes in addition to
  their sentences, so every word a reader can see or cite is found.

## Open questions

None.

## Verification

1. Before changing anything, reproduce: for each statement, search its short
   label, each slot concept's label and one word of its quote; list every miss and
   its cause in the pull request.
2. After: the same list, empty. `uv run tools/validate.py`, `uv run tools/build.py`,
   and a browser capture of a search that used to miss (the `screenshot` skill).
