---
name: staleness-and-verification
description: One content-hash mechanism serves review, quote verification and cross-references; stale downgrades and reports, only invalid blocks; verification is recorded as an attestation.
metadata:
  type: project
---

Review staleness, quote verification and reference staleness are one mechanism,
not three: everything compares content hashes of canonical forms. An edge or
attestation records the hash of what it was asserted against; when the current
hash differs, the assertion is **stale** — its derived status drops and it
lands in a report, but nothing blocks. Only **invalid** blocks: a quote that
fails verification against a source at hand, a schema violation at edit time, a
view cut that fails completeness. Quote verification itself is discharged as a
`validated` attestation, made when an agent has the downloaded source bytes (at
extraction, or on re-fetch), pinning the source's content hash; it may be
signed by a software agent's own key, unlike `expert_reviewed`. Decided
2026-09-05, resolving the quote-verification, stale-severity and
attestation-scope questions together; applied in spec v0.2 (§5, §8).

**Why:** Sources are referenced, never rehosted ([[sources-referenced-never-rehosted]]),
so a fresh clone can verify nothing directly — the attestation is the durable
evidence, and if a public source vanishes the graph degrades to "verified, on
record", never to unfalsifiable. Stale-blocks was rejected because any update
to a shared statement or source would freeze everything referencing it; stale
must be survivable for the pool to evolve. Attestation scope is explicit
(`content` vs `with_evidence`) because an expert vouches for a conclusion
*given its evidence basis*: with `with_evidence`, a new contesting claim stales
the expert review — silently rewiring evidence under a standing attestation was
the failure mode to prevent.

**How to apply:** Never treat a staleness report as a merge blocker, and never
"fix" staleness by deleting the stale attestation — re-verification or
re-review is the only cure. When emitting `validated` attestations, always pin
`source_hash`. When an expert review should cover a statement's evidence
basis, use `scope: with_evidence`; plain `content` covers only the entity's own
canonical form.
