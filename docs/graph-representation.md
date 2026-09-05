# Graph Representation — how knowledge is stored in this repository

> **Status: design intent (v0.2).** A first schema exists (`schema/schema.yaml`),
> but no validator and no CI exist in this repository yet. Statements below that a
> check runs, or that a change "does not pass", describe the model this repository
> is being built to — not behaviour anyone can rely on today.

This file explains the approach behind the knowledge in this repository. It is
written for humans who review changes and for AI agents that read or write graph
data. It fixes *concepts and rules*; the one schema (`schema/schema.yaml`, §9) is
the authority on syntax.

If you are an agent about to add or change content: read this file, then the
schema, then the existing entities in the namespaces you are working in. Never
invent structure that neither this file nor the schema describes.

---

## 1. One sentence

Everything is an **entity with a URL** in **one pool**; knowledge lives in two
layers — source-anchored **claims** with deterministic identity, and a **semantic
layer** of concepts, statements and structure that claims *support* or *contest*;
relations are **typed tuples**; every statement carries **provenance**; a
**graph is a versioned view** over the pool — a filter plus an as-of point,
validated when a version is cut; review is a **signed attestation** by an agent
over a content hash; **one schema** governs the whole pool.

---

## 2. Entities and URLs

An entity is anything we want to talk about or point at: a claim extracted from a
source, a medical concept, a statement, a decision point, a source document, an
agent, a view. Every entity has exactly one identifier of the form

```
<namespace>/<entity-id>
```

Namespaces exist to mint identity, not to own content. The pool has a fixed set
of them, declared in the schema:

```
sources/         source documents                       identity: chosen slug + version
claims/          source-anchored extraction units       identity: derived (see cascade)
concepts/        uncoded medical concepts               identity: minted
statements/      propositions claims bear evidence on   identity: minted
pathways/        structural nodes of one composition    identity: minted within the pathway
views/           view definitions and their cuts        identity: chosen slug
agents/          people, organisations, software runs   identity: chosen slug
attestations/    signed review records                  identity: sequential
<terminology>/   one namespace per classification release (icd10gm-2026/, ops-2026/)
                                                        identity: the code itself
```

**The identity cascade.** Identity is deterministic wherever it can be, minted
only where it must be — because deterministic identity makes duplicates
impossible by construction, while minted identity requires judgment and review:

1. **Terminology concepts** take their id from the classification release:
   `icd10gm-2026/K57.3`. Two agents cannot mint duplicate nodes for a coded
   concept; the code is the id.
2. **Claims** derive their id from what anchors them:
   `claims/<source-id>/<hash>` where the hash is computed (by the validator, never
   by hand) over the locator and the verbatim quote. Two agents extracting the
   same passage produce the same claim.
3. **Edges** derive their id from `(from, kind, to)` plus an explicit
   discriminator only when parallel edges of the same kind exist.
4. **Uncoded concepts and statements** are minted — opaque, stable, ASCII slugs
   that never encode meaning that might change. Minting is preceded by search:
   an agent must look for an existing entity, and for a codable one, before
   inventing an id (§11).
5. **Structural nodes** are minted freely within their pathway namespace;
   duplication there is harmless because they carry no evidence.

Finer things are addressed by extending the path, and view cuts are addressed
with `@`:

```
<namespace>/<entity-id>              an entity
<namespace>/<entity-id>/<property>   one property of that entity
views/<view-id>                      the view, floating: evaluated as of now
views/<view-id>@<cut>                a cut: the frozen, validated version
```

The property-level address is what feedback, provenance and reviews point at
("the grade of this claim is wrong", not "this claim is wrong"). Nothing is
stored under a property address; it is an address the resolution rules in §6
answer for.

Identity is the URL, never the file. How entities are distributed over files is
a storage and diff-ergonomics decision that the model does not depend on.

**Language.** Content stays in the source language — labels, quotes, statement
texts are never translated at extraction. Every entity and edge that carries
text declares `lang` (BCP 47, e.g. `de`). Structural keys are English (they are
ours, not content); enum values are schema vocabulary slugified from the source
language (`soll`/`sollte`/`kann`, `konsens`/`starker_konsens`). Translation is
a build-layer concern, never a data concern.

**Canonical form.** Every entity has exactly one canonical serialisation
(deterministic key order and encoding, fixed by the validator and never changed
without a migration). The hash of that form identifies the entity's content at a
point in time and is what signatures cover (§8) and what staleness detection
compares (§5, §8). Authors never compute it; the validator does.

---

## 3. Two layers: claims and semantics

The pool separates *what sources say* from *what we hold to be the knowledge*.

### 3.1 Claims — the evidence layer

A **claim** is a source-anchored extraction unit: one place in one source,
carrying the locator, the verbatim quote, and the structured content readable at
that place — a recommendation's grade, verb and direction, a criterion's
threshold, a definition. Claims are **immutable** once extracted (a correction
is an edit with history, §7; the source said what it said), their identity is
deterministic (§2), and they are **never merged**. A claim asserts nothing on
its own about what is true; it asserts what a source states at a location.

### 3.2 The semantic layer

Three kinds of entity, kept apart because different edges attach to them:

- **Concepts** — the vocabulary: *pancreatic resection*, *intraabdominal
  drainage*. Thin: labels, a definition, and `codes_as` edges into terminology
  namespaces. A concept cannot be contested; it means, it does not claim.
- **Statements** — propositions with a truth claim: "after pancreatic
  resection, the drain can be removed early when the drain amylase indicates a
  low fistula risk." Statements are what claims *support* or *contest*. A
  statement has a **slot shape** declared by the schema (population, action,
  condition, outcome — filled with concept URLs), which makes "is this the same
  statement?" an almost-computable question and keeps granularity honest: **a
  statement is the smallest unit that can be independently supported or
  contested.**
- **Structure** — decision questions, branches, outcomes, explicit gaps: the
  pathway machinery. Structural nodes assert nothing about the world; they
  arrange statements into something navigable, and they are pure modelling.

### 3.3 Stored versus derived

A semantic entity stores almost nothing: labels, definition, type, slots.
Everything evidential is **derived** from its claim links and never written by
hand: its source set (via `supports`), its conflict status (via `contests`), its
effective grade (computed from supporting claims by a schema-declared policy —
a grade always originates in a document, §6.5), and its review state (via
attestations, §8). A hand-written evidence property on a statement is the same
violation as a hand-written review status.

### 3.4 How new evidence arrives

A new document produces new claims — deterministically, without judgment. The
editorial act is linking: each claim gets a `supports` or `contests` edge to the
statement it bears on, or a new statement is minted when none fits. Where a
claim agrees, the statement's evidence grows and the statement itself is
untouched. Where it disagrees, the conflict is *surfaced*, never resolved by
recency (§7). Sameness is an edge, not an identity decision: a wrong link is
rerouted or deleted under review; there is no merge that has to be unpicked.

---

## 4. One pool, many views

There is no monolith and there are no owned graphs; there is one pool, and there
are **views**: named selections over it. What v0.1 called "a graph" is a view.

A view is an entity (`views/<view-id>`) whose definition is a **filter** — a
membership rule over the pool: by pathway namespace, by source set, by concept
subtree, by schema compliance, or an explicit list. How filters are expressed is
schema-governed and deliberately minimal for now (§13).

**Versioning.** The unadorned view URL is *floating*: the filter evaluated
against the pool as of now. A **cut** freezes it:

```
views/<view-id>@<n>  =  filter + as-of commit + frozen member list + validation
```

Because the pool's history is append-only through git (§7), a cut is stable
forever: its member list, the members' content hashes, and therefore the cut's
own canonical hash never change. Cuts are what get cited, exported, and attested
(§8). The repository commit is the pool-wide as-of point; no per-item version
bookkeeping exists.

**Completeness lives at the cut.** A view intended as a decision pathway must
pass the structural validation for pathways *at cut time* — every branch has its
outcomes, every referenced statement is a member, nothing dangles. A filter that
amputates a branch fails validation and the cut is not made. This is where
v0.1's "a graph is complete and valid on its own" guarantee now lives — on the
only object that can actually honour it.

---

## 5. Edges are typed tuples

An edge is

```
(from-URL, kind, to-URL, properties?)
```

with a derived id (§2). `kind` comes from the schema's vocabulary, which keeps
the different jobs of edges apart:

- **evidence** — `supports`, `contests`: claim → statement. The only edges that
  carry evidential weight.
- **body-text relations** — `refines`, `supplements`, `limits`: claim → claim.
  Body text never inherits a recommendation's grade; the edge says how they
  relate.
- **coding** — `codes_as`: concept → terminology concept. Codes are never bare
  strings inside a property; a code is a node and coding is an edge, so the link
  carries provenance and dangles visibly when a classification changes.
- **structure** — `sequence`, `branch` (with a `guard` property), `about`:
  among structural nodes and from them to the statements they arrange.
- **cross-source semantics** — `specializes`, `complements`, `conflicts`:
  statement → statement. Our assertions, always `modelling`, with rationale and
  date.

**Staleness without version pins.** An edge whose meaning depends on its
endpoints' content records the endpoints' content hashes at assertion time. When
an endpoint's current hash differs, the edge is **stale**: surfaced for
re-evaluation, its derived weight downgraded — not silently applied, and not a
blocker (§8). This replaces v0.1's `@version` pinning of cross-graph edges; the
mechanism is the same one attestations use.

---

## 6. Provenance

Provenance answers "where does this statement come from". It is the central
guarantee of this repository: a human must be able to jump from any statement to
the exact passage that justifies it, and a machine must be able to verify that
the passage exists.

### 6.1 Sources are entities

Every source document — a PDF, a web page, a classification release — is an
entity in `sources/` with a version, its public URL, a content hash and licence
information. Sources are **referenced, never rehosted**: the repository and its
links are the only assets (see `README.md`, "Source documents"). Provenance
points *into* sources with a locator whose syntax depends on the media type:

```
sources/pomgat-lv-1.0#page=61        a PDF page — physical page, what viewers navigate by
sources/bfarm-icd10gm-2026#code=K57.3 a code in a classification
sources/some-website#:~:text=exact%20phrase   an HTML text anchor
```

The build layer turns these into links using the fragment conventions of the
target format (`#page=N&search=<quote>` for PDFs — viewers that understand
`search` highlight the quote, the rest land on the page). Authors never write
the final link; they write the locator.

### 6.2 A reference is a locator plus a verbatim quote

```yaml
{at: sources/pomgat-lv-1.0#page=61, quote: "kann die Einlage einer intraabdominellen"}
```

The quote is short (a clause, not a paragraph) and **must be a verbatim
substring of the source's extracted text** — it is three things at once: the
highlight target for a reader, the reviewer's at-a-glance check, and the
validator's exact match. A paraphrase breaks all three. A statement whose quote
cannot be found where it claims to be is invalid. Provenance values are lists; a
single reference is shorthand for a list of one.

### 6.3 Two kinds of provenance value

- a reference (or list of references) into a source — "the source says this";
- the marker **`modelling`** — "no source states this; it was asserted by the
  person or agent who built it".

Claims carry references by construction — a claim *is* its anchor plus content.
Semantic and structural entities are typically `modelling`: a statement's
wording, a slot assignment, every structural node, every cross-source edge.
`modelling` is never a way to skip provenance; it is provenance of a different
kind, recorded as attribution to an agent instead of derivation from a passage.

### 6.4 Default on the entity, override per property

Every entity and every edge carries a default `source`. Any property whose
origin differs gets its own entry under `provenance`, keyed by the property
name. Resolution for `claims/pomgat-lv-1.0/ab12cd34/grade`: the override if
present, otherwise the entity default.

### 6.5 The schema decides which properties need provenance

Not every property has a source. Identifiers, types and labels are ours. The
schema states, per type and property, whether provenance is **required** (must
resolve to a passage, never `modelling`), **optional**, or **not applicable**.
Domain rules such as "a recommendation grade must always come from the
document, never from the extractor" are enforced here mechanically — which is
also why a statement's effective grade is *derived* from its supporting claims
(§3.3) and never written on the statement.

### 6.6 Who did it

Which extraction run produced which claims is recorded as attribution to an
agent (§8). Who reviewed what is recorded as attestations, never as a
hand-written field. Review state is derived.

---

## 7. History, editing and schema evolution

**Files hold current state; git is the edit history.** The commit is the
timestamp, the author and the atomic as-of point for the whole pool — no
in-data timestamps duplicate it. The data is laid out so that this history can
be *extracted* later (one entity per file, property-level diffs legible) when
the pool moves out of git.

**Supersede versus contest.** Two very different events must never be
conflated:

- **Supersede** — a correction within the same editorial line: an extraction
  error fixed, a label improved. This is an *edit*: the file changes, the old
  value lives in git history, attestations on the old content go stale.
- **Contest** — a source that disagrees. This is *new data*: a new claim and a
  `contests` edge. Both sides stay visible with their evidence; the conflict is
  surfaced on the statement. **Recency never resolves disagreement** — a newer
  document does not overwrite a stronger one (§11.4).

An agent asserting a change chooses which of the two it is, and the choice is
reviewable in the diff: an edit to an existing entity claims "same editorial
line"; new entities and edges claim "new evidence".

**Schema evolution.** The schema is edited first, in its own change; data edits
then comply with the schema as of their commit. Nothing is retroactively
invalid: an entity untouched since an older schema version remains valid *as of
its last edit*. The drift this creates is deliberate and **visible**: a view can
demand "compliant with the current schema", and the entities that fall out of it
are precisely the migration worklist. Migrations are explicit, reviewed edits —
never silent rewrites.

---

## 8. Agents, attestations and review

People, organisations and software runs are entities in `agents/`. An agent
entity has an opaque, stable id; how the agent authenticates — a repository
login, an ORCID, a signing key — is a set of *identity claims* and
*verification methods* attached to the agent, replaceable without touching
anything that refers to it.

An **attestation** records that an agent makes a claim about a subject at a
specific content state, and signs it:

```yaml
- id: attestations/0001
  type: attestation
  subject: statements/drain-early-removal-low-risk
  subject_hash: "sha256:9f2c…"        # hash of the subject's canonical form (§2)
  scope: with_evidence                 # content | with_evidence (statement + its current claim set)
  claim: expert_reviewed               # expert_reviewed | validated | disputed | …
  by: agents/mkoch
  date: 2026-09-05
  proof: {type: …, verification_method: agents/mkoch#key-1, value: "…"}
```

Rules that follow:

- **Review state is derived, not asserted.** An entity's status is whatever its
  valid attestations support. Nobody writes `validated` into an entity.
- **A changed subject invalidates its attestations.** If the canonical hash no
  longer matches, the attestation is *stale* and the derived status drops until
  someone re-attests. With `scope: with_evidence`, the hash covers the composed
  snapshot of the statement *plus its evidence edges*, so a new contesting claim
  stales an expert review — the expert vouched for a conclusion given its
  evidence basis.
- **Verification is an attestation.** The `validated` claim records that a quote
  was checked against the source — made at extraction time while the downloaded
  copy is at hand, or whenever a source is re-fetched. It additionally records
  the **source's content hash** it verified against, so a changed source never
  leaves silently orphaned verifications. `validated` is a mechanical claim and
  may be signed by a software agent's own key; `expert_reviewed` may not.
- **Stale downgrades; invalid blocks.** Staleness — of an attestation or an
  edge (§5) — lowers the derived status of the affected item and lands in a
  report. It never blocks an unrelated change, otherwise any source or
  statement update would freeze everything that references it. *Invalid* —
  a quote that fails verification against a source at hand, a schema violation
  at edit time, a cut that fails completeness — blocks.
- **Authority is governance, not data.** Which agents may issue which claims is
  a role on the agent, granted through the repository's governance process and
  checked by the validator.
- **A service acting for a human** is itself an agent acting *on behalf of* the
  human; the human's key signs the attestation, the service's key signs the
  commit. Signed commits protect the changesets; attestations protect the
  statements.

---

## 9. One schema

`schema/schema.yaml` is the single schema for the whole pool. v0.1 had a schema
per graph kind because graphs owned their nodes; views own nothing, so there is
nothing for a per-view schema to govern. Instead:

- the schema declares the **namespaces**, the **node types** with their
  properties and provenance requirements (§6.5), the **edge kinds** with the
  types they may connect, the **slot shapes** of statement types, and the
  **structural validations** a view kind must pass at cut time (§4);
- schema changes land **before** the data that uses them (§7);
- the schema is versioned by its own history like everything else.

What a pathway needed a "graph kind" for — its node types, its edge vocabulary,
its completeness rules — is now a *view kind* inside the one schema.

---

## 10. Illustration: a guideline's drainage recommendations

A slice of real content in the shape the rules above imply — the source is the
POMGAT S3 guideline (AWMF 088-010OL), quotes verified against the document.

```yaml
# ── source ────────────────────────────────────────────────────────────────
- id: sources/pomgat-lv-1.0
  type: source
  title: "S3-Leitlinie Perioperatives Management bei gastrointestinalen Tumoren (POMGAT), Langversion 1.0"
  awmf_register: "088-010OL"
  url: "https://register.awmf.org/assets/guidelines/008-010OLl_S3_Perioperatives-Management-bei-gastrointestinalen-Tumoren-POMGAT_2023-12.pdf"
  content_hash: "sha256:…"
  license: "© Leitlinienprogramm Onkologie; referenced, not rehosted"

# ── claims (phase one: deterministic, verifiable against the source) ──────
- id: claims/pomgat-lv-1.0/7c31a2f0        # hash over (locator, quote); validator-checked
  type: claim
  kind: recommendation
  recommendation_no: "6.5"
  grade: "0"
  verb: kann
  direction: for
  consensus: strong_consensus
  source: {at: sources/pomgat-lv-1.0#page=61, quote: "kann die Einlage einer intraabdominellen"}
  provenance:
    consensus: {at: sources/pomgat-lv-1.0#page=61, quote: "Starker Konsens"}

- id: claims/pomgat-lv-1.0/e945b1d8
  type: claim
  kind: recommendation
  recommendation_no: "6.7"
  grade: "0"
  verb: kann
  direction: for
  source: {at: sources/pomgat-lv-1.0#page=63, quote: "kann die abdominelle Drainage im frühen postoperativen"}

- id: claims/pomgat-lv-1.0/1f80c3aa
  type: claim
  kind: criterion
  source: {at: sources/pomgat-lv-1.0#page=64, quote: "unter 5000 U/L am ersten postop. Tag"}

# ── semantic layer (phase two: linking, all modelling) ────────────────────
- id: concepts/pankreasresektion
  type: concept
  label: "Pankreasresektion"
  source: modelling

- id: statements/drain-early-removal-low-risk
  type: statement
  label: "Nach Pankreasresektion kann die Drainage früh entfernt werden, wenn das Sekret ein geringes Fistelrisiko anzeigt"
  slots:
    population: concepts/pankreasresektion
    action: concepts/drainage-entfernung
    condition: concepts/geringes-fistelrisiko
  source: modelling

# ── structure (the pathway arranging the statements) ──────────────────────
- id: pathways/pomgat-drains/removal_q
  type: decision
  label: "Frühe Drainageentfernung möglich?"
  source: modelling

# ── edges (derived ids; endpoint hashes recorded for staleness) ───────────
- [claims/pomgat-lv-1.0/e945b1d8, supports, statements/drain-early-removal-low-risk, {source: modelling}]
- [claims/pomgat-lv-1.0/1f80c3aa, refines,  claims/pomgat-lv-1.0/e945b1d8, {source: modelling}]
- [concepts/pankreasresektion, codes_as, ops-2026/5-52, {source: modelling}]
- [pathways/pomgat-drains/removal_q, about, statements/drain-early-removal-low-risk, {source: modelling}]

# ── a view: the pathway as a citable unit ─────────────────────────────────
- id: views/pomgat-drains
  type: view
  view_kind: pathway
  filter: {pathway: pathways/pomgat-drains, closure: [about, supports, refines, codes_as]}
  cuts:
    - {cut: 1, as_of: "<commit>", members_hash: "sha256:…", validated: true}
```

Things to notice: the grade sits on the *claim*, extracted verbatim from the
recommendation box, and the statement carries no grade at all — its effective
grade is derived; the criterion is a claim of its own, related by an edge, never
inheriting the grade; the classification code is a URL; a second guideline
discussing early drain removal would add claims and `supports`/`contests` edges
to the *same statement* — the statement's evidence grows without the statement
changing; and the view's cut, not any entity, is the thing a publication would
cite.

---

## 11. Rules of conduct for agents writing to this repository

1. **Read before writing.** This file, the schema, then the existing entities in
   your namespaces. Do not add types, kinds or properties the schema does not
   know.
2. **Extract first, link second.** Phase one mints claims — mechanical,
   verifiable line-by-line against the source. Phase two links them to the
   semantic layer — judgment, all `modelling`. Keep the phases apart; ideally
   they are separate, separately reviewable changes.
3. **Search before minting.** Before creating a concept or statement, look for
   an existing one, and for a codable one. Mint only what no terminology and no
   existing entity covers; flag near-duplicates for review instead of deciding
   sameness silently.
4. **Contest, never overwrite.** A source that disagrees with existing content
   is new claims plus `contests` edges — both sides sourced, conflict surfaced.
   Editing an entity asserts a correction within the same editorial line, and
   nothing else. Recency resolves nothing.
5. **Every statement needs provenance.** If the source says it, cite the passage
   with a verbatim quote you have verified at that location. If the source does
   not say it, write `modelling`. Never guess a page.
6. **Underestimate, never upgrade.** Content without a formal rating in the
   source gets none in the graph. Grades live on claims; derived values are
   computed, not written.
7. **Prefer an explicit gap to an invented answer.** If the source says "no
   recommendation possible", model the gap; if it is silent, leave nothing.
8. **Keep identifiers stable.** Renaming or removing an entity is a reviewed,
   history-preserving change; other entities point at it.
9. **Run the validator** and treat its output as the review's first comment. A
   change that does not validate is not proposed.
10. **Do not set review status.** Agents submit content; attestations decide
    status. An agent never writes a review state or signs on behalf of a person.

---

## 12. Relation to established conventions

The model is a labelled property graph with linked-data identifiers and
W3C-style provenance. The mapping:

| concept here | convention |
|---|---|
| entity with URL, `type` | Linked Data: resources have IRIs, `type` is `rdf:type` |
| `(from, kind, to, props)` | labelled property graph (GQL / openCypher / Gremlin) |
| claim (locator + verbatim quote + content) | nanopublications; W3C Web Annotation (`SpecificResource`, `TextQuoteSelector`); PROV-O `wasDerivedFrom`; PDF locators per RFC 8118 |
| statement with slots, evidence derived | Wikidata statements with references and ranks; SKOS for the concept layer |
| view, cut | RDF named graphs / datasets; a cut is a versioned release of one |
| `modelling` | PROV-O `wasAttributedTo` with no `wasDerivedFrom` |
| codes as nodes, coding as edge | SKOS mappings; FHIR `Coding` |
| agents, attestations, proofs | PROV-O agents; W3C Data Integrity proofs |
| one schema | SHACL/ShEx shapes plus application-level checks |

No inference semantics are assumed: relations are asserted, not entailed.

---

## 13. What this approach deliberately leaves open

- **File format and layout.** YAML as shown, but anything that round-trips to
  the same entities and tuples is acceptable; one entity per file is a
  diff-ergonomics choice, not a rule.
- **The view-filter language.** The schema starts with a minimal set of filter
  forms; how far it grows toward a query language is undecided
  (`docs/open-questions.md`).
- **Statement slot vocabularies and grade derivation.** Which slot shape each
  statement type needs, and how supporting claims' grades compose, are open —
  they are medically sensitive and will be settled against real content.
- **Export projections.** FHIR, RDF, diagram formats — generated from the
  data, never authored.

---

## 14. What the environment bounds

Sources are referenced, never committed and never rehosted — the repository and
its links to public sources are the only assets (`README.md`; the reasoning in
`.claude/memory/design/sources-referenced-never-rehosted.md`). A quote is
therefore checked against a source when an agent has the downloaded bytes at
hand — at extraction, or on a re-fetch — and the check is recorded as a
`validated` attestation (§8), which is the durable evidence once the copy is
gone. If a public source later changes or vanishes, its content hash detects
this loudly, stale attestations downgrade the affected items, and the graph
degrades to "verified, on record" — never to unfalsifiable.

The environment itself is described once, elsewhere: `README.md` for
contributors, `.claude/rules/environment/sandbox-environment.md` for agents.

---

Version 0.2 · 2026-09-05
