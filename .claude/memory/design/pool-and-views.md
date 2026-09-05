---
name: pool-and-views
description: The repository is one pool of entities and edges; graphs are versioned views (filter + as-of commit), and one schema governs everything.
metadata:
  type: project
---

The repository is a single pool of entities and typed edges — not a set of
owned, self-contained graphs. What v0.1 of the spec called "a graph" is a
**view**: a named filter over the pool, versioned by *cuts* (filter + as-of
commit + frozen member list, validated when cut). There is exactly one schema
(`schema/schema.yaml`) for the whole pool, because views own nothing a per-view
schema could govern. Decided 2026-09-05; applied in spec v0.2.

**Why:** Owned graphs forced a choice the maintainer rejected: a new document
either spawned a parallel graph or required cross-graph ceremony to add
evidence to existing knowledge. In the pool, new evidence attaches to existing
nodes natively. The change also dissolved the graph-versioning open question
(repository-wide tags vs. per-graph tags): the git commit is the pool-wide
as-of point, a cut records (filter, commit), and no per-item or per-graph
version bookkeeping exists — nothing about versioning depends on git tags, so
the scheme survives the planned migration of the data out of this repository.
Completeness — v0.1's "a graph is complete and valid on its own" — moved to the
only object that can honour it: a cut fails validation if its filter amputates
structure, and once made it is immutable, so it stays complete forever.

**How to apply:** Treat "graph" in older material as "view". Never introduce
per-view schemas, per-graph version tags, or `@version` pins on entity URLs —
staleness runs on content hashes (edges and attestations record the hashes
they were asserted against), and citation runs on view cuts
(`views/<id>@<n>`). Views are cheap; when someone needs "everything from
sources L1 and L2 since 2017", that is a new view filter, not a new graph.
