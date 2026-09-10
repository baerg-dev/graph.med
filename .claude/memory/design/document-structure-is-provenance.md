---
name: document-structure-is-provenance
description: A source's chapters are provenance (`section` on the claim, `outline` on the source) and filters, never nodes; the proposed `outlines/` namespace was rejected because the pool models knowledge, not documents.
metadata:
  type: project
---

Where a claim sits in its document is recorded on the claim (`section`, next to
`recommendation_no`) and the document's table of contents on the source
(`outline`, complete, including sections with no recommendation). A chapter
reaches the reader as a view filter and as a tree beside the graph. There is no
`outlines/` namespace, no chapter node and no edge to a chapter. Decided
2026-09-10; applied in `docs/graph-representation.md` §6.7 and §4,
`docs/publication.md` §3.

**Why:** A physician's feedback asked for chapters as navigable objects with
their own namespace, so that a click on "7.4" shows that chapter's subgraph and
uncovered sections show as gaps. The maintainer's position: "I do not want to
model the document but the knowledge." Both needs are met by provenance: the
section on the claim gives the filter, the outline on the source gives the
coverage count, and the validator makes the section a controlled reference by
checking it against the outline. What a chapter *means* clinically (an organ
family, a perioperative phase) is knowledge and goes onto concepts and statements,
which is also the only form that survives a second guideline with a different
outline. Statements and concepts never carry a section, because a statement can
be supported from two chapters and a concept used in five.

**How to apply:** Write `section` on claims and `outline` on sources; never
mint an entity for a chapter or draw one in the graph. When a source's headings
carry clinical meaning, express that meaning as `broader` edges, facets or a
phase vocabulary, using the heading as the hint and never the section number as
the key. Related: [[relations-are-edges-not-fields]],
[[view-page-is-a-decision-tree]].
