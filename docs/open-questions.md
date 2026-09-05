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

Questions carried by v0.1 — quote-verification, graph-versioning,
attestation-scope, edge-identity, stale-severity, the v0.2 consistency fixes,
inbound-documents — were settled by the pool-and-views redesign and applied in
spec v0.2; their whys are the `design/` memories. The entries below are the
open edges of the v0.2 model.

---

## grade-derivation  (graph-representation.md §3.3, §6.5; schema `statement.derived.effective_grade`)
**Question:** How does a statement's effective grade compose from its supporting claims' grades — and what does a contesting claim do to it?
**Options:** highest supporting grade wins · most recent guideline's grade wins · no scalar at all — display the grade *distribution* and let the reader judge · a per-view-kind policy declared in the schema
**Leaning:** toward the distribution — collapsing "one S3 guideline says soll (A), another says kann (0)" into a single scalar loses exactly the disagreement the model exists to surface; a contesting claim should mark the statement contested rather than adjust any number. Medically sensitive; settle against real content, not in the abstract. (2026-09-05)
**Settled by:** the first statement with supporting claims from two graded sources; lands in the schema.

## statement-shape  (graph-representation.md §3.2; schema `statement.slots`)
**Question:** Which slot vocabulary does each statement type need — is population/action/condition/outcome (PICO-shaped) right, and for which content is it overkill?
**Options:** one fixed slot set for all statements · slot sets per statement type in the schema · free-form statements with slots optional everywhere
**Leaning:** slot sets per statement type; the current schema ships one PICO-ish set with every slot optional as a starting point. The granularity rule (smallest independently contestable unit) is the fixed part; the slots serve it. First evidence (chunk ch06, POMGAT chapter 6, 15 statements): population+action fit every statement, condition and outcome each earned their keep once, nothing resisted the shape — but all statements came from one chapter of one source, so the shape has not yet met cross-source sameness. Keep open until a second source lands on the same statements. (2026-09-05)
**Settled by:** a second source's claims linking into existing statements without the slots getting in the way.

## concept-minting  (graph-representation.md §2, §11.3)
**Question:** Who may mint uncoded concepts, and what keeps the concept namespace from silting up with near-duplicates?
**Options:** any agent, with search-before-mint discipline and review · a curated namespace only humans extend · agents propose, a periodic curation pass merges/blesses
**Leaning:** any agent with search-before-mint plus review (the rule is already §11.3); the mitigation for silting is that concepts are thin and sameness lives in edges, so late cleanup is cheap. Revisit if the first extractions produce a duplicate rate that review cannot absorb. (2026-09-05)
**Settled by:** the duplicate rate observed after the first two independent document extractions.

## view-filter-language  (graph-representation.md §4, §13; schema `view_filters`)
**Question:** How expressive do view filters get — the two starting forms (pathway closure, explicit selection) or a real query language?
**Options:** keep the fixed filter forms, adding one per proven need · adopt an existing query language (a GQL/Cypher subset, Datalog) early · filters as code in the build layer, not data
**Leaning:** fixed forms, extended one proven need at a time — a query language is a dependency and an injection surface the data model should not commit to before a build layer exists. Filters must stay declarative data so cuts are reproducible. (2026-09-05)
**Settled by:** the first view a fixed form cannot express.

## evidence-profiles  (data/PROGRESS.yaml deferred; schema `claim`)
**Question:** How are the per-outcome GRADE evidence tables of evidence-based recommendation boxes modelled — the ⊕-symbol ratings per outcome with effect sizes that justify a claim's grade?
**Options:** not at all (the grade plus the locator suffice; the reader follows the link) · a structured `evidence_profile` property on the claim (outcome, rating, effect, CI) · each outcome row as its own claim (kind: fact) with a `refines` edge to the recommendation claim
**Leaning:** none yet — deliberately unmodelled in chunk ch06. The third option fits the model best (rows are source-anchored, quotable, individually verifiable) but multiplies claims roughly fivefold per box; decide when a consumer (a view, the website, grade-derivation) actually needs the profiles rather than on principle. (2026-09-05)
**Settled by:** the first consumer that needs evidence detail beyond the grade.
