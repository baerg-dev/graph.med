# Graph Representation — how knowledge is stored in this repository

> **Status: design intent (v0.1).** No validator, no schema, and no CI exist in
> this repository yet. Statements below that a check runs, or that a change "does
> not pass", describe the model this repository is being built to — not behaviour
> anyone can rely on today.

 
This file explains the approach behind every graph in this repository. It is written for humans who review changes and for AI agents that read or write graph data. It fixes *concepts and rules*; it does not prescribe a file format or a schema. The concrete schemas live next to the data and are the authority on syntax.
 
If you are an agent about to add or change content: read this file, then the schema referenced by the graph you are working on, then the existing entities in that graph. Never invent structure that neither this file nor the schema describes.
 
---
 
## 1. One sentence
 
Everything is an **entity with a URL**; relations are **typed tuples** between URLs; every statement carries **provenance** that points back to where it came from; graphs are **independent namespaces** that may reference each other; review is a **signed attestation** by an agent over an entity's content hash; a **schema per graph kind** says which types, properties and relations are allowed.
 
---
 
## 2. Entities and URLs
 
An entity is anything we want to talk about or point at: a recommendation, a decision point, a variable, a code in a classification, a source document, a graph itself. Every entity has exactly one identifier of the form
 
```
<graph-id>/<entity-id>
```
 
The graph id is the namespace; the entity id is unique within it. Identifiers are short, ASCII, stable, and never encode meaning that might change (no titles, no page numbers).
 
Finer things are addressed by extending the path:
 
```
<graph-id>/                          the graph's own metadata entity
<graph-id>/<entity-id>               an entity
<graph-id>/<entity-id>/<property>    one property of that entity
<graph-id>@<version>/<entity-id>     the entity as it was in a specific version of the graph
```
 
The property-level address is what feedback, provenance and reviews point at ("the grade of this recommendation is wrong", not "this recommendation is wrong"). Nothing is stored under a property address; it is an address that the resolution rules in §5 answer for.
 
Identity is the URL, never the file. How entities are distributed over files is a storage and diff-ergonomics decision that the model does not depend on.
 
**Canonical form.** Every entity has exactly one canonical serialisation (deterministic key order and encoding, fixed by the repository's validator and never changed without a migration). The hash of that form identifies the entity's content at a version and is what signatures cover (§6). Authors never compute it; the validator does.
 
---
 
## 3. Graphs are independent namespaces
 
A graph is a self-contained, independently versioned unit: its own metadata entity, its own nodes, its own edges, its own schema reference. A graph is complete and valid on its own. There is no monolith; there are many graphs side by side, and most of them never touch each other.
 
Examples of graphs that coexist in the same URL space:
 
- a clinical guideline turned into a decision pathway (`088-010OL/…`),
- a second guideline, unrelated to the first (`003-001/…`),
- a classification such as ICD-10-GM or OPS, one node per code (`icd10gm-2026/…`),
- a topic taxonomy used for coverage maps,
- a hospital SOP,
- a set of cross-graph links (see §7).
Graphs of different *kinds* declare different schemas (§8). Graphs of the same kind share one.
 
**Versioning.** An unadorned URL means "the current version". A graph version is a tag on the repository, not a parallel copy. Edges that cross graph boundaries pin the version they were written against (`003-001@2.0/…`) so that an update on either side surfaces as a stale link rather than silently changing meaning.
 
---
 
## 4. Edges are typed tuples
 
An edge is
 
```
(from-URL, kind, to-URL, properties?)
```
 
`kind` is a short verb from the vocabulary of the graph's schema. Properties on the tuple are for information that belongs to the relation itself — a guard condition on a branch, a rationale on a link between two guidelines, and always the edge's provenance (§5). An edge is identified by its triple unless it is given an explicit id (only needed when two parallel edges of the same kind exist).
 
An edge whose endpoints have different graph ids is a **cross-graph edge**. There is no separate mechanism for these; they are the same tuples, with two extra rules: endpoints are version-pinned, and the schema says which kinds are allowed to cross.
 
Edges express two very different things and the vocabulary keeps them apart:
 
- **structure within the knowledge** — a decision branches to an outcome, a text fragment refines a recommendation, a sub-category is broader than a category;
- **semantic links to other graphs** — a mention of a diagnosis *codes as* a node in the ICD graph; a recommendation in one guideline *specializes* one in another.
Codes from classifications are never bare strings inside a property. A code is a node in the classification's graph and coding is an edge to it, so the link can carry its own provenance and can dangle visibly when the classification changes.
 
---
 
## 5. Provenance
 
Provenance answers "where does this statement come from". It is the central guarantee of this repository: a human must be able to jump from any statement to the exact passage that justifies it, and a machine must be able to verify that the passage exists.
 
### 5.1 Sources are entities
 
Every source document — a PDF, a web page, a classification release — is itself an entity with a URL, a version, a location on the web, a content hash and licence information. Provenance points *into* sources with a locator whose syntax depends on the media type: a page for PDFs, a text anchor for HTML, a code for a classification.
 
```
pomgat-lv-1.0#page=61
bfarm-icd10gm-2026#code=K57.3
some-website#:~:text=exact%20phrase
```
 
The build layer turns these into clickable deep links using the standard fragment conventions of the target format. Authors never write the final link; they write the locator.
 
### 5.2 A provenance reference
 
A reference is a locator, optionally with a short verbatim **quote** from that place:
 
```yaml
{at: pomgat-lv-1.0#page=61, quote: "Nach Pankreasresektionen sollte eine intraabdominelle Drainage"}
```
 
The quote is short (a clause, not a paragraph). It serves three purposes at once: it lets the viewer highlight the passage, it lets a reviewer confirm at a glance that the right sentence is meant, and it lets the validator check automatically that the text really appears at the stated location. A statement whose quote cannot be found where it claims to be does not pass.
 
A property may have **several** references — a statement made in a summary box and refined in the body text, or present in both the long and short version of a document. Provenance values are therefore lists; a single reference is shorthand for a list of one.
 
### 5.3 Two kinds of provenance value
 
- a reference (or list of references) into a source — "the source says this";
- the marker **`modelling`** — "the source contains no such statement; this was asserted by the person or agent who built the graph".
`modelling` is the honest value for synthesised things: a decision question that reformulates several sentences into one branch, an enumeration the source never names, the negative branch a source only implies, every cross-graph link. It is never a way to skip provenance; it is provenance of a different kind, and the export records it as attribution to an agent instead of derivation from a passage.
 
### 5.4 Default on the entity, override per property
 
Every node and every edge carries a default `source`. Any property whose origin differs from the default gets its own entry under `provenance`, keyed by the property name:
 
```yaml
- id: 088-010OL/drain_panc_removal_q
  type: decision
  label: "Frühe Drainageentfernung möglich?"
  criteria: {any: [ … ]}
  source: {at: pomgat-lv-1.0#page=63, quote: "frühe Drainageentfernung"}
  provenance:
    label: modelling
    criteria:
      - {at: pomgat-lv-1.0#page=63, quote: "unter 5000 U/L an POD 1"}
      - {at: pomgat-lv-1.0#page=63, quote: "unter dem Dreifachen der Serumkonzentration"}
```
 
Resolution for the address `088-010OL/drain_panc_removal_q/criteria`: the override if present, otherwise the entity default.
 
### 5.5 The schema decides which properties need provenance
 
Not every property has a source. Identifiers, types and reviewer notes are ours. The schema of each graph kind states, per property, whether provenance is **required** (must resolve to a passage, never `modelling`), **optional** (passage or `modelling`), or **not applicable**. This is where domain rules such as "a recommendation grade must always come from the document, never from the extractor" are enforced mechanically rather than by discipline.
 
### 5.6 Who did it
 
Which extraction run produced a graph is recorded on the graph's metadata entity as a reference to an agent (§6). Who reviewed what is recorded as attestations (§6), never as a hand-written field on the entity. Review state is derived from attestations and can be gated per type by the schema — for example, content types that cannot be safely extracted without human judgment may not be merged until a qualified human has attested to them.
 
---
 
## 6. Agents, attestations and review
 
People, organisations and software runs are entities like everything else, in their own namespace (e.g. `agents/…`). An agent entity has an opaque, stable id; how the agent authenticates — a repository login, an ORCID, a hospital single sign-on, a signing key — is a set of *identity claims* and *verification methods* attached to the agent, which can be added, rotated or replaced without touching anything that refers to the agent.
 
An **attestation** is an entity that records that an agent makes a claim about a subject at a specific content version, and signs it:
 
```yaml
- id: attestations/0001
  type: attestation
  subject: 088-010OL@0.3.0/drain_panc_abdominal      # an entity, or an entity/property
  subject_hash: "sha256:9f2c…"                        # hash of the subject's canonical form (§2)
  claim: expert_reviewed                              # expert_reviewed | validated | disputed | …
  by: agents/mkoch
  date: 2026-08-25
  proof: {type: …, verification_method: agents/mkoch#key-1, value: "…"}
```
 
Rules that follow:
 
- **Review state is derived, not asserted.** An entity's status is whatever its valid attestations support. Nobody writes `validated` into an entity.
- **A changed entity invalidates its attestations.** If the canonical hash no longer matches, the attestation is *stale* and the derived status drops until someone re-attests. This is the same mechanism as version-pinned cross-graph edges (§7), applied to review.
- **The signature covers the subject hash**, so the proof never sits inside the entity it certifies, and the same attestation format works whether the key came from a local key pair, a browser passkey, or a short-lived certificate bound to an external identity provider. Only the proof type and the verification method differ.
- **Authority is governance, not data.** Which agents may issue which claims is a role on the agent, granted through the repository's governance process and checked by the validator. The graph records who attested; it does not decide who may.
- **A service acting for a human** (a review website, a bot opening pull requests) is itself an agent and acts *on behalf of* the human; the human's key signs the attestation, the service's key signs the commit.
Signed commits in the repository history are complementary: they protect the changesets. Attestations protect the statements.
 
---
 
## 7. Linking graphs without merging them
 
Graphs stay separate; relations between them are ordinary cross-graph edges (§4). Three properties make this safe:
 
1. **The edge says what it is.** Its kind (e.g. *specializes*, *complements*, *conflicts*, *codes as*) carries the semantics; no free-text interpretation is needed to act on it.
2. **The edge is modelling.** No source document states a relation between two documents, so cross-graph edges carry `modelling` provenance plus a rationale and a date. They are our assertions, isolated and individually reviewable, and they never alter the graphs they connect.
3. **Endpoints are pinned.** When either graph moves to a new version, the edge becomes stale and is surfaced for re-evaluation rather than silently applied.
Whether the cross-graph edges of a domain are stored inside one of the graphs, in a dedicated link graph, or elsewhere is a storage choice. Semantically they are one thing: tuples whose endpoints live in different namespaces.
 
---
 
## 8. Schemas: one per graph kind
 
The core of this approach knows nothing about any domain. It defines entities, URLs, tuples, provenance, versions and review. Everything else — which node types exist, which properties each type requires or forbids, which edge kinds exist and between which types they may run, which vocabularies are allowed, which properties need provenance — is a **schema for a graph kind**. Every graph declares which schema it conforms to.
 
Schemas are ordinary, versioned artefacts in the repository. A schema may extend another (an SOP schema may relax the grading requirements of a guideline-pathway schema). A new domain means a new schema, not a change to the core.
 
A schema is validated in two layers, and readers should expect both:
 
- **shape checks** that a standard schema validator can perform: required and forbidden properties per type, enumerations, expression grammars, URL syntax;
- **graph and semantic checks** that need the whole graph or other graphs: all URLs resolve, quotes are found at their locators, edge endpoints have permitted types, cross-graph edges are pinned, structural properties such as acyclicity or branch coverage hold. These are declared alongside the schema and executed by the repository's validator.
Every change to the repository runs both layers. A change that fails either is not merged.
 
---
 
## 9. Illustration: a clinical guideline pathway
 
The first graph kind in this repository turns a clinical guideline into a decision pathway. It is one instantiation of the approach, shown here so that the abstract rules above have a concrete face.
 
Node types distinguish, by construction, what carries a formal grade from what does not: a *recommendation* (graded, from a recommendation box) versus an ungraded *step*; a machine-evaluable *decision* versus a *clinical judgment* a clinician must make; body-text content that *refines*, *supplements* or *limits* a recommendation without ever inheriting its grade; an explicit *gap* where the guideline states that no recommendation can be given; and *variables* the decisions are evaluated on. Edges include guarded *branches*, deliberate *loops*, references between chapters, the three body-text relations, *codes as* links into classification graphs, and the cross-guideline kinds *complements*, *specializes* and *conflicts*.
 
A slice of one guideline, in the shape the rules above imply:
 
```yaml
# nodes
- id: 088-010OL/drain_panc_abdominal
  type: recommendation
  label: "Nach Pankreasresektion intraabdominelle Drainage anlegen"
  grade: B
  verb: sollte
  direction: for
  evidence: low
  consensus: strong_consensus
  recommendation_no: "6.5"
  source: {at: pomgat-lv-1.0#page=61, quote: "Nach Pankreasresektionen sollte eine intraabdominelle Drainage"}
  provenance:
    consensus: {at: pomgat-lv-1.0#page=61, quote: "Starker Konsens"}
 
- id: 088-010OL/drain_panc_remove_early
  type: step
  label: "Drainage bis zum 4. postoperativen Tag entfernen"
  source: {at: pomgat-lv-1.0#page=63, quote: "bis zum 4. postoperativen Tag"}
 
- id: 088-010OL/fr_k1_amylase
  type: text_fragment
  klasse: 1
  text: "Die frühe Entfernung setzt ein geringes Fistelrisiko voraus, operationalisiert über die Drainage-Amylase."
  source: {at: pomgat-lv-1.0#page=63, quote: "Definition ist zwischen den Studien uneinheitlich"}
 
# edges  (from, kind, to, properties)
- [088-010OL/drain_panc_abdominal, sequence, 088-010OL/drain_panc_removal_q, {source: modelling}]
- [088-010OL/drain_panc_removal_q, branch, 088-010OL/drain_panc_remove_early,
   {guard: true, source: {at: pomgat-lv-1.0#page=63, quote: "bei geringem Fistelrisiko"}}]
- [088-010OL/fr_k1_amylase, refines, 088-010OL/drain_panc_abdominal, {source: modelling}]
- [088-010OL/drain_panc_abdominal, codes_as, ops-2026/5-52, {source: modelling}]
- [003-001@2.0/vte_prophylaxe_dauer, conflicts, 088-010OL@0.3.0/vte_prophylaxe_dauer_gi,
   {rationale: "unterschiedliche Prophylaxe-Dauer bei unterschiedlichem Stand", as_of: 2026-08-24, source: modelling}]
```
 
And the classification it links to, which is simply another graph:
 
```yaml
- id: ops-2026/5-52
  type: category
  code: "5-52"
  label: "Operationen am Pankreas"
  source: bfarm-ops-2026#code=5-52
```
 
Things to notice: the grade and its companions appear only on the *recommendation*; the body-text fragment is tied to the recommendation by an edge, not by anything inside either node; every edge has provenance, `modelling` where the document is silent; the classification code is a URL, not a string; only the cross-guideline edge carries version pins; no entity carries a review status — that is derived from attestations (§6).
 
---
 
## 10. Rules of conduct for agents writing to this repository
 
1. **Read before writing.** The schema declared by the target graph and the entities already present define the vocabulary. Do not add types, kinds or properties that the schema does not know.
2. **Every statement needs provenance.** If the source says it, cite the passage with a quote you have actually verified at that location. If the source does not say it, write `modelling`. Never guess a page.
3. **Underestimate, never upgrade.** Content without a formal rating in the source must never receive one in the graph. When unsure whether something is graded, it is not.
4. **Do not resolve conflicts silently.** Two sources that disagree are represented as a *conflicts* relation with both sides sourced, not as one chosen answer.
5. **Prefer an explicit gap to an invented answer.** If the source covers a situation with "no recommendation possible", say so with a gap node; if it does not cover the situation at all, leave nothing.
6. **Stay inside your namespace.** Changes to one graph do not edit another. Relations to other graphs are cross-graph edges with pinned versions.
7. **Keep identifiers stable.** Renaming or removing an entity is a versioned change with a changelog entry, because other graphs may point at it.
8. **Run the validator** and treat its output as the review's first comment. A change that does not validate is not proposed.
9. **Do not set review status.** Agents submit content; humans attest to it. An agent never writes a review state, an attestation, or a signature on behalf of a person.
---
 
## 11. Relation to established conventions
 
The model is a labelled property graph with linked-data identifiers and W3C-style provenance. Readers from either tradition should find it familiar; the mapping is:
 
| concept here | convention |
|---|---|
| entity with URL, `type` | Linked Data: resources have IRIs (compact ids expand under a base), `type` is `rdf:type` |
| `(from, kind, to, props)` | labelled property graph (GQL / openCypher / Gremlin): typed relationships that carry properties |
| graph as namespace | RDF named graphs / datasets |
| provenance reference with locator and quote | W3C Web Annotation (`SpecificResource`, `FragmentSelector`, `TextQuoteSelector`); PROV-O `wasDerivedFrom`; PDF locators per RFC 8118, HTML locators per URL Text Fragments |
| `modelling` | PROV-O `wasAttributedTo` an agent with no `wasDerivedFrom` |
| codes as nodes, coding as edge | SKOS concepts and mappings; FHIR `Coding` |
| agents, attestations, proofs | PROV-O `Agent`/`actedOnBehalfOf`; W3C Data Integrity proofs (Verifiable Credentials) |
| schema per graph kind | SHACL/ShEx shapes, JSON Schema, plus application-level graph checks |
 
Four things are compact conventions of this repository rather than idioms of any one standard, and are mapped explicitly on export: properties on edges and per-property provenance (RDF-star or reification in RDF; native in property graphs), the `modelling` marker, `@version` pinning in URLs (versioned named graphs, `canonical|version` in FHIR), and property-level addresses. No inference semantics are assumed: relations are asserted, not entailed.
 
---
 
## 12. What this approach deliberately leaves open
 
- **File format and layout.** YAML, JSON, JSON Lines or anything else that round-trips to the same entities and tuples is acceptable; the schema of a graph kind states what its graphs use.
- **View layer.** How graphs are rendered, laid out or queried is a separate concern built on top of the data; nothing in the data depends on it.
- **Export projections.** Because every entity has a URL, every relation is a typed tuple and every statement has provenance, the data maps cleanly onto standard forms — linked-data provenance and annotation vocabularies, domain interchange standards such as HL7 FHIR for the clinical case, diagram formats for review. These are generated from the data, never authored.
---
 
## 13. What the environment bounds

Provenance is only as verifiable as the sources within reach. Work on this repository
happens inside a sandbox that mounts nothing but the workspace and blocks outbound
network by default, and source documents are never committed (`README.md`), so a quote
can be checked only against a source present in the workspace — it cannot be fetched to
settle the question, and a fresh clone contains no sources at all.

How verification is discharged under that bound is not yet decided: it may be
best-effort wherever the source is at hand, or performed once by an agent that had the
source and recorded as an attestation (§6). Until it is decided, §5.2's "the validator
checks the quote" is intent, not a guarantee.

The environment itself is described once, elsewhere: `README.md` for contributors,
`.claude/rules/environment/sandbox-environment.md` for agents.

---
 
Version 0.1 · 2026-08-25

