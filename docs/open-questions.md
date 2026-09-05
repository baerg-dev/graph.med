# Open questions

What is still undecided. One entry per question, newest concerns last. This
registry is the handover between sessions: git records the code, pull requests
record uncertainty about a diff, `.claude/memory/` records what was settled —
what is *not yet* settled lives here, with the options considered and the
current leaning, so that no session re-derives it from scratch.

When a question is settled it leaves this file: the decision lands where it
belongs (usually the spec), and the why becomes a memory under
`.claude/memory/design/`. The `handover` skill
(`.claude/skills/handover/SKILL.md`) maintains this file at the end of a
session; editing it by hand is just as valid.

---

## quote-verification  (graph-representation.md §5.2, §13)
**Question:** How is quote verification discharged when source documents cannot be committed to the repository?
**Options:** best-effort validator check wherever the source happens to be present · a committed quote-index per source (hashes of normalized spans, verifiable offline) · verification as a signed attestation (§6) by an agent that had the source
**Leaning:** verification-as-attestation, sharpened by the hosting decision (see
`inbound-documents`): the attestation is the record, and the validator checks directly
whenever the bytes are at hand — which the hosting regime decides. For mirrored
sources anyone can re-run the check, so attestations are re-derivable; for
in-the-wild sources the attestation is the *primary* durable evidence, because the
AWMF register removes superseded documents — the graph then degrades from
"verifiable by anyone" to "verified, on record", never to unfalsifiable. Two
refinements: the attestation should record the source content hash it verified
against (a corrected source entity must not leave silently orphaned verifications),
and `validated` may be signed by a software agent's own key — it is a mechanical
claim, unlike `expert_reviewed`. A quote-index can still be added later if offline
re-verification is needed. (2026-09-05)
**Settled by:** spec v0.2.

## graph-versioning  (graph-representation.md §3)
**Question:** §3 says graphs are "independently versioned" and that a version is "a tag on the repository" — which is it, and how does `003-001@2.0` resolve?
**Options:** repository-wide tags (graphs are not independently versioned) · per-graph tags `<graph-id>/v<version>` · version only as a property on the graph metadata entity
**Leaning:** per-graph tags, `<graph-id>/v<version>` (git allows slashes in tag names), with the version also declared on the graph metadata entity and the validator checking the two agree. Gives §10.7 its changelog home on the metadata entity. (2026-09-05)
**Settled by:** spec v0.2.

## attestation-scope  (graph-representation.md §6)
**Question:** What does an attestation's content hash cover — can an expert-reviewed node have its outgoing edges rewired without the attestation going stale?
**Options:** node content only, stated explicitly · node plus outgoing edges · whole-graph coverage via the graph metadata entity's hash (Merkle-style) · subgraph/pathway-level subjects
**Leaning:** node attestations cover only the node's own content (say so, so nobody assumes more); the graph metadata entity's canonical hash covers all member entities and edges, so attesting `<graph-id>@<version>/` is whole-graph review; pathway-level subjects deferred as a named open problem. (2026-09-05)
**Settled by:** spec v0.2.

## edge-identity  (graph-representation.md §4)
**Question:** Edges identified only by their triple cannot be attested, disputed, or pointed at — and a `conflicts` edge is precisely what someone will want to dispute.
**Options:** keep triple-identity with optional explicit ids · give every edge a deterministic derived id
**Leaning:** deterministic derived id for every edge, owned by the graph that asserts it (normally the `from` side; a link graph owns its own edges); explicit ids remain for parallel edges. (2026-09-05)
**Settled by:** spec v0.2.

## stale-severity  (graph-representation.md §7 vs §8)
**Question:** §7 says a stale version-pinned edge is "surfaced for re-evaluation"; §8 says a change that fails validation is not merged. Is staleness an error or a warning?
**Options:** stale blocks the merge · stale downgrades the derived status of the stale item and lands in a report, only *invalid* blocks
**Leaning:** the second — otherwise bumping any graph's version freezes every graph that pins it. Same semantics as attestation staleness: one mechanism. (2026-09-05)
**Settled by:** spec v0.2.

## spec-v0.2-consistency  (graph-representation.md, several sections)
**Question:** Consistency fixes agreed in review, pending application.
**Options:** — (agreed, not controversial)
**Leaning:** do all of them in v0.2: sources get a namespace like every other entity (`sources/pomgat-lv-1.0#page=61`); §9 declares `drain_panc_removal_q`, which two of its edges reference; state the key-language rule (keys English, controlled-vocabulary values may stay source-language — `klasse:` is the lone violation); keep the two-key `source:`/`provenance:` form as defined in §5.4. Added 2026-09-05, after checking the POMGAT Langversion 1.0 itself: correct the example quotes against the document — §5.2 quotes "Nach Pankreasresektionen sollte eine intraabdominelle Drainage", but PDF p. 61 says "Nach Pankreasresektion **kann** die Einlage einer intraabdominellen Drainage **erwogen werden**" (a recommendation-grade error, precisely the class quote-verification exists to catch; the §5.4 criteria quotes are also paraphrases and sit on p. 64, not 63); state that a quote must be a *verbatim substring* of the source's extracted text — it is the highlight target, the reviewer's check and the validator's match at once, so paraphrase breaks all three; state that `#page=` counts physical PDF pages (what browser viewers navigate by), not printed page numbers. (2026-09-05)
**Settled by:** spec v0.2.

## inbound-documents  (README.md "Source documents")
**Question:** How do source documents reach a working copy — and the viewer, and the validator — now that the agent-inbox drop directory is removed and sources are never committed?
**Options:** cloud drop folder synced by the maintainer (the removed design) · maintainer-managed sync outside the repo · per-source fetch with an egress allowlist entry · two hosting regimes decided per source by its licence
**Leaning:** two regimes, chosen per source by the licence on its source entity; node
data stays regime-agnostic (locator + quote only — the URL lives on the source
entity, so a source changes regime in one place).
*Mirrored:* a content-addressed copy (object key = the source entity's sha256) in a
project bucket (Cloudflare R2 is the candidate), rendered by a project PDF.js viewer
that turns locator + quote into page navigation with the quote highlighted.
Licence-checked 2026-09-05 against BfArM's Downloadbedingungen (Stand 2025-08-01):
ICD-10-GM, OPS and ICD-10-WHO are "andere amtliche Werke" (§ 5 Abs. 2 UrhG) —
redistribution is permitted unmodified (§ 62), with the annex attribution texts
(§ 63), and without commercial advertising; ICD-O-3 and ICF carry extra WHO purpose
restrictions, and Alpha-ID-SE embeds INSERM-licensed Orpha codes.
*In the wild:* AWMF/OL guidelines cannot be rehosted without written permission —
copyright sits collectively with the guideline group, and the OL notice requires
written consent for any electronic storage. They are referenced at their public URL;
extracting facts plus short verbatim quotes needs no permission (§ 51 UrhG
quotation right; §§ 44b/60d UrhG text-and-data-mining). The build layer emits one
link for both regimes and every browser: `<resolved-url>#page=N&search=<quote>` —
PDF.js-based viewers highlight, others ignore `search` and land on the page.
Accepted costs of the wild regime: the register removes superseded documents and
its responses carry no CORS headers, so no in-app highlighting. Mitigations: the
content hash detects drift loudly; verification attestations (see
`quote-verification`) are the durable evidence; a private, never-published
preservation copy under the TDM exceptions; and written permission from the
OL-Redaktion as the upgrade path into the mirrored regime — the GGPONC project
shows they grant research use. (2026-09-05)
**Settled by:** creating the bucket and mirroring the first source (ICD-10-GM), and a
permission request to the OL-Redaktion. Still open inside this leaning: how the
sandbox reaches the bucket (host-injected credential vs. allowlisted gated domain)
and who curates uploads. Touches `README.md` and likely a new environment rule.
