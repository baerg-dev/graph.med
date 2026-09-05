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
**Leaning:** slot sets per statement type; the current schema ships one PICO-ish set with every slot optional as a starting point. The granularity rule (smallest independently contestable unit) is the fixed part; the slots serve it. First evidence (chunk ch06, POMGAT chapter 6, 15 statements): population+action fit every statement, condition and outcome each earned their keep once, nothing resisted the shape — Chunks ch04 and ch05 (35 more statements, chapters 4–5) confirm it: population+action still fit every statement, condition was used 7 times and outcome 5 times, and one action concept (`perioperative-fortfuehrung-dauertherapie`) was shared by four statements with the drug therapy in the population slot — a first sign that slot filling, not slot shape, is where sameness will be decided. Chunk ch07a (13 statements, chapter 7.1–7.3) adds the first strain: two statements are *comparative* — 7.11 (epidural analgesia superior to peripheral regional analgesia) and 7.12 (TAP block as an alternative to epidural analgesia) — and the shape has no comparator slot, so the comparator survives only in the label. A second source contesting "EA beats PRA" would still find the statement, but one asserting "EA beats systemic opioids" (7.9's actual comparison) fills identical slots and is a different proposition. Either a `comparator` slot or a per-type slot set for comparative statements is the likely fix; not added yet, because one chunk is thin evidence. Chunk ch07b (11 statements, chapter 7.4.1) is the first where `outcome` dominates: nine statements fill it with the same concept (`postoperativer-paralytischer-ileus`), because every box is "Drug X zur Prophylaxe des POI" — the outcome is the *purpose* of the action, not a measured effect. The slot works, but it is doing a different job than in 7.11's "EA is superior" (where the outcome would be pain intensity). Whether purpose and measured effect should share a slot is a second facet of the same question. All statements still come from one source, so the shape has not yet met cross-source sameness. Keep open until a second source lands on the same statements. (2026-09-05, updated after ch04–ch05 and ch07a)
**Settled by:** a second source's claims linking into existing statements without the slots getting in the way.

## concept-minting  (graph-representation.md §2, §11.3)
**Question:** Who may mint uncoded concepts, and what keeps the concept namespace from silting up with near-duplicates?
**Options:** any agent, with search-before-mint discipline and review · a curated namespace only humans extend · agents propose, a periodic curation pass merges/blesses
**Leaning:** any agent with search-before-mint plus review (the rule is already §11.3); the mitigation for silting is that concepts are thin and sameness lives in edges, so late cleanup is cheap. First observation (chunk ch07a): the near-duplicates that appear are driven by population *scope*, not by wording — `gastrektomie` (ch06) beside `gastrektomie-oder-magenteilresektion` (7.3), `pankreaskopfresektion` (ch06) beside `klassische-whipple-operation` (7.4, whose body text explicitly excludes pylorus-preserving variants). Both were minted deliberately because the boxes draw different boundaries; a concept hierarchy (broader/narrower edge) would let them coexist without looking like duplicates. Revisit if the first extractions produce a duplicate rate that review cannot absorb. (2026-09-05, updated after ch07a)
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

## gap-notices  (graph-representation.md §3.2, §11.7; schema `claim.kind: gap_notice`, `edge_kinds`)
**Question:** How does a `gap_notice` claim — a box that says "no recommendation can be given" (POMGAT 4.3 on calcium antagonists, 4.6 on perioperative glucocorticoids) — enter the semantic layer? `supports`/`contests` target statements, but a gap asserts no proposition; the structural `gap` node exists only inside a pathway, and none is authored yet.
**Options:** leave gap notices as unlinked claims until a pathway arranges them (a `gap` node `about` … nothing) · allow a `gap` structural node outside any pathway that the claim `supports` · mint a statement of the form "no recommendation possible for X" and let the claim support it · a dedicated edge kind (`notes_gap`: claim → concept) pointing at the topic the source declines to rule on
**Leaning:** the fourth option is the most honest — the gap is *about a concept* (Calciumantagonisten, perioperative Glukokortikoidgabe), not a proposition, and an edge to the concept keeps it findable from the topic without inventing a statement nobody can contest. Deferred in chunk ch04: both gap claims are extracted and unlinked, so nothing is lost. Note that 4.7 ("in der Pankreas- und Leberchirurgie kann … erwogen werden") is the exception carved out of 4.6's gap — whatever shape gap notices take should let a recommendation stand *inside* a gap's scope. (2026-09-05)
**Settled by:** the first pathway or view that has to render "the guideline declines to recommend here".

## box-granularity  (graph-representation.md §3.1; schema `claim.grade`, `claim.verb`; data/claims/pomgat-lv-1.0/ch04–ch05)
**Question:** Is a recommendation *box* or a recommendation *sentence* the unit of a claim? POMGAT boxes routinely hold two to four sentences with different verbs and directions (4.1: kann / soll / sollte nicht / soll), and three boxes print compound grades — "A/B" (5.1, 5.6), "B/0" (5.4) — one grade per sentence.
**Options:** one claim per box, with `grade`/`verb`/`direction` becoming lists or the schema admitting compound grades · one claim per sentence sharing the box's `recommendation_no`, each carrying the single grade its verb maps to (A↔soll, B↔sollte, 0↔kann) · one claim per box plus one sub-claim per sentence with `refines` edges
**Leaning:** per sentence, as done in ch04 and ch05: a claim carries one verb and one direction by schema, and per-sentence claims are what let statements stay at "smallest independently contestable unit". The cost is that the grade of a compound-grade box is *assigned* to sentences by the verb mapping rather than read off — deterministic under the AWMF grading scheme, but an inference the extractor makes, so review should confirm it is not an upgrade in disguise. The box remains recoverable via the shared `recommendation_no`. (2026-09-05)
**Settled by:** the first reviewer who wants the box back as an addressable unit, or the validator once it has to check `recommendation_no` uniqueness.
