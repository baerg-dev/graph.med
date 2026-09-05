---
name: two-layer-identity
description: Claims carry deterministic source-anchored identity and are never merged; semantic nodes are minted, and sameness is an edge, not an identity decision.
metadata:
  type: project
---

Node identity is layered. **Claims** — source-anchored extraction units — get
deterministic ids derived from (source, locator, verbatim quote); terminology
concepts get their id from the classification code. Neither is ever minted by
judgment, so duplicates are impossible by construction and claims are never
merged. **Semantic nodes** (uncoded concepts, statements) are minted — opaque
stable ids, created only after searching for an existing or codable entity.
Whether two things are the same is expressed by *edges* (`supports`,
`contests`, linking claims to statements), never by merging identities.
Decided 2026-09-05, resolving the question "is node identity defined by source
or sources?"; applied in spec v0.2 (§2 identity cascade, §3).

**Why:** Identity-by-accumulating-sources is a mutable key — it breaks every
reference each time evidence arrives, contradicting the requirement that a new
document "adds to a node's sources but reuses it otherwise". Identity-by-single-
source is perfect but only for the layer frozen to its passage. Splitting the
layers moves all heavy, sourced content into the layer that never merges, and
makes sameness a reviewable, reversible link: a wrong `supports` edge is
rerouted or deleted, whereas a wrong identity merge (the Wikidata/UMLS failure
mode) joins two edit histories that must be surgically unpicked. The thin
minted layer is the only place judgment can err, and its errors are cheap.

**How to apply:** Extraction is two phases with different risk profiles: phase
one mints claims mechanically (verifiable line-by-line against the source);
phase two links them to the semantic layer (all `modelling`, where review
attention belongs) — keep them separately reviewable. Never merge claim nodes;
never mint a concept without searching existing entities and terminologies
first; flag near-duplicate statements for review instead of deciding sameness
silently. A statement stores no evidence properties — sources, conflict status,
effective grade and review state are derived from its incoming edges.
