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
session; editing it by hand is just as valid. What the current pass of work is,
and which chunk is next, is not a question and lives in `data/PROGRESS.yaml`.

---

## grade-derivation  (graph-representation.md §3.3, §6.5; schema `statement.derived.effective_grade`)
**Question:** How does a statement's effective grade compose from its supporting claims' grades — and what does a contesting claim do to it?
**Options:** highest supporting grade wins · most recent guideline's grade wins · no scalar at all — display the grade *distribution* and let the reader judge · a per-view-kind policy declared in the schema
**Leaning:** toward the distribution — collapsing "one S3 guideline says soll (A), another says kann (0)" into a single scalar loses exactly the disagreement the model exists to surface; a contesting claim should mark the statement contested rather than adjust any number. Medically sensitive; settle against real content, not in the abstract. (2026-09-05)
**Settled by:** the first statement with supporting claims from two graded sources; lands in the schema.

## statement-shape  (graph-representation.md §3.2; schema `statement.slots`)
**Question:** Which slot vocabulary does each statement type need — is population/action/condition/outcome (PICO-shaped) right, and for which content is it overkill?
**Options:** one fixed slot set for all statements · slot sets per statement type in the schema · free-form statements with slots optional everywhere
**Leaning:** slot sets per statement type; the schema ships one PICO-ish set with every slot optional as the starting point, and the granularity rule (smallest independently contestable unit) is the fixed part. One source's ninety statements fit it, with three strains worth keeping in view: *comparative* statements (7.11 "epidural analgesia is superior to peripheral regional analgesia", 7.12 "TAP block as an alternative") have no comparator slot, so a different comparison fills identical slots — a `comparator` slot or a per-type slot set is the likely fix; `outcome` is used both as the *purpose* of an action (chapter 7.4.1, nine statements "X zur Prophylaxe des POI") and as a *measured effect* (7.11, pain intensity), and whether the two should share a slot is unsettled; and slots are roles, not types — `mpom` is the action of 8.1–8.5 and the condition of 8.6–8.7 without duplication, which is reassuring. The shape has not yet met cross-source sameness. (2026-09-05)
**Settled by:** a second source's claims linking into existing statements without the slots getting in the way.

## concept-minting  (graph-representation.md §2, §11.3)
**Question:** Who may mint uncoded concepts, and what keeps the concept namespace from silting up with near-duplicates?
**Options:** any agent, with search-before-mint discipline and review · a curated namespace only humans extend · agents propose, a periodic curation pass merges/blesses
**Leaning:** any agent with search-before-mint plus review (the rule is already §11.3); concepts are thin and sameness lives in edges, so late cleanup is cheap. The near-duplicates observed so far are driven by population *scope*, not wording (`gastrektomie` beside `gastrektomie-oder-magenteilresektion`, `pankreaskopfresektion` beside `klassische-whipple-operation`, five liver-resection concepts): the boxes draw different boundaries, so both are right. The `broader` edge (spec §5, decided 2026-09-10) is the answer to that part — such concepts coexist under one family without looking like duplicates — and narrows this question to who mints and how many true duplicates review has to absorb. (2026-09-10)
**Settled by:** the duplicate rate observed after the first two independent document extractions.

## view-filter-language  (graph-representation.md §4, §13; schema `x-view-filters`)
**Question:** How expressive do view filters get — fixed filter forms or a real query language?
**Options:** keep the fixed filter forms, adding one per proven need · adopt an existing query language (a GQL/Cypher subset, Datalog) early · filters as code in the build layer, not data
**Leaning:** fixed forms, extended one proven need at a time — a query language is a dependency and an injection surface the data model should not commit to before it is needed, and filters must stay declarative data so cuts are reproducible. The first proven need arrived: a `section` form for selection views (spec §4, §6.7), so a chapter of a source can be a view. (2026-09-10)
**Settled by:** the first view a fixed form cannot express.

## evidence-profiles  (data/PROGRESS.yaml deferred; schema `claim`)
**Question:** How are the per-outcome GRADE evidence tables of evidence-based recommendation boxes modelled — the ⊕-symbol ratings per outcome with effect sizes that justify a claim's grade?
**Options:** not at all (the grade plus the locator suffice; the reader follows the link) · a structured `evidence_profile` property on the claim (outcome, rating, effect, CI) · each outcome row as its own claim (kind: fact) with a `refines` edge to the recommendation claim
**Leaning:** none yet. The third option fits the model best (rows are source-anchored, quotable, individually verifiable) but multiplies claims roughly fivefold per box; decide when a consumer (a view, the site, grade-derivation) actually needs the profiles rather than on principle. (2026-09-05)
**Settled by:** the first consumer that needs evidence detail beyond the grade.

## gap-notices  (graph-representation.md §3.2, §11.7; schema `claim.kind: gap_notice`, edge kinds)
**Question:** How does a `gap_notice` claim — a box that says "no recommendation can be given" (POMGAT 4.3 on calcium antagonists, 4.6 on perioperative glucocorticoids) — enter the semantic layer? `supports`/`contests` target statements, but a gap asserts no proposition; the structural `gap` node exists only inside a pathway, and none is authored yet.
**Options:** leave gap notices as unlinked claims until a pathway arranges them · allow a `gap` structural node outside any pathway that the claim `supports` · mint a statement of the form "no recommendation possible for X" and let the claim support it · a dedicated edge kind (`notes_gap`: claim → concept) pointing at the topic the source declines to rule on
**Leaning:** the fourth — the gap is *about a concept*, not a proposition, and an edge to the concept keeps it findable from the topic without inventing a statement nobody can contest. The gap claims are extracted and unlinked, so nothing is lost. Whatever shape gap notices take must let a recommendation stand *inside* a gap's scope: 4.7 ("in der Pankreas- und Leberchirurgie kann … erwogen werden") is the exception carved out of 4.6's gap. The site's *Lücke* direction (publication.md §3) will need this. (2026-09-05)
**Settled by:** the first pathway or view that has to render "the guideline declines to recommend here".

## box-granularity  (graph-representation.md §3.1; schema `claim.grade`, `claim.verb`)
**Question:** Is a recommendation *box* or a recommendation *sentence* the unit of a claim? POMGAT boxes routinely hold two to four sentences with different verbs and directions (4.1: kann / soll / sollte nicht / soll), and three boxes print compound grades — "A/B" (5.1, 5.6), "B/0" (5.4) — one grade per sentence.
**Options:** one claim per box, with `grade`/`verb`/`direction` becoming lists or the schema admitting compound grades · one claim per sentence sharing the box's `recommendation_no`, each carrying the single grade its verb maps to (A↔soll, B↔sollte, 0↔kann) · one claim per box plus one sub-claim per sentence with `refines` edges
**Leaning:** per sentence, as the pool does: a claim carries one verb and one direction by schema, and per-sentence claims are what let statements stay at "smallest independently contestable unit". The cost is that the grade of a compound-grade box is *assigned* to sentences by the verb mapping rather than read off — deterministic under the AWMF grading scheme, but an inference, so review should confirm it is not an upgrade in disguise. The box remains recoverable via the shared `recommendation_no`. (2026-09-05)
**Settled by:** the first reviewer who wants the box back as an addressable unit, or the validator once it has to check `recommendation_no` uniqueness.

## quality-indicators  (graph-representation.md §3.1, §5; schema `claim.kind`, edge kinds; data/PROGRESS.yaml deferred)
**Question:** How do a guideline's quality indicators — POMGAT chapter 9 defines four (Tabelle 7): each a numerator/denominator measure with a Qualitätsziel, derived from one "soll" recommendation it restates as Referenz-Empfehlung — enter the pool? They are source-anchored and quotable like claims, but no claim kind names what they are, and `supports`/`contests` misdescribe the relation: a QI is not evidence for its statement, it is a measure *of adherence to* it.
**Options:** a claim kind `quality_indicator` plus a new edge kind (`measures`: claim → statement) · model the QI as a statement of its own that the QI text `supports`, linked to the underlying statement by `complements` · leave QIs out of the pool entirely
**Leaning:** the first, once a consumer asks — a hospital-facing view wants "this one is audited, target 0%" next to the recommendation, and a dedicated kind plus edge keeps a QI a claim (verbatim, hashed, verifiable) without pretending it is evidence. Two scope mismatches await a modelling pass: QI 3's denominator spans three organ groups whose recommendations are three statements, and QI 4's is narrower (Kolonresektion) than the box it references. (2026-09-05)
**Settled by:** the first view that has to show which recommendations are audited, or a second source whose QIs land on the same statements.

## cut-publication  (publication.md §7; graph-representation.md §4; schema `view.cuts`)
**Question:** How is a cut served next to the floating view — and does a cut get a single-file export (a PDF) as the citable artefact?
**Options:** the build checks out each cut's `as_of` commit and renders it under `<view-id>@<n>` on every deploy · a cut is rendered once, when made, and its output committed to a publication branch · cuts are not served at all; the URL redirects to the repository at the commit
**Leaning:** the first — one build, no second branch to keep consistent, and a cut stays exactly as reproducible as the pool it is cut from; build time grows with the number of cuts, which is fine for years. A PDF export belongs to a cut if anywhere. (2026-09-06)
**Settled by:** the first citation of a view.

## decision-graph-derivation  (publication.md §3; graph-representation.md §3.2 structure, §5 `branch`/`guard`)
**Question:** The site draws one decision tree *derived* from statement slots. Is that the durable form, or a stand-in until pathways are authored — and what do authored pathways add that the derivation cannot?
**Options:** keep deriving from slots and never author pathways for plain recommendation chapters · author a pathway per chapter as structural nodes with `branch` guards and `about` edges, and render those instead · both — derived by default, authored where a chapter is a real algorithm (a flowchart in the source)
**Leaning:** the third. The derivation is honest (every element is a slot value or a claim's grade, nothing invented) and covers recommendation lists well, but it has no branch labels, no ordering between decisions, and no gaps; a chapter that *is* a decision algorithm in the source deserves authored structure with guards. (2026-09-06)
**Settled by:** the first source chapter that is a flowchart, authored as a pathway and read next to its derived graph.

## phase-vocabulary  (graph-representation.md §3.2, §6.7; schema `statement.slots`)
**Question:** Where does the perioperative phase — präoperativ, intraoperativ, postoperativ — live, now that chapters are filters and not knowledge? POMGAT's headings encode it; a second guideline organised anatomically will state it in the sentence instead.
**Options:** a `phase` vocabulary on the statement · a phase concept in the population or condition slot · a facet value on the action concept · nothing — the phase stays in the label
**Leaning:** on the statement: "postoperativ" qualifies the recommendation, not the patient, and a small controlled vocabulary makes "colorectal, postoperative" a cross-guideline query the way "7.4" never can be. Not part of the current pass; decide when the second source arrives or when the site wants a phase filter. (2026-09-10)
**Settled by:** the first cross-source query or view that needs the phase.

## concept-hierarchy-depth  (graph-representation.md §5 `broader`; publication.md §3)
**Question:** How many levels does the concept hierarchy need — one family layer above the existing concepts (Leber, Kolorektum, …), or two (Organ, then Eingriffsart)?
**Options:** one layer of eight to ten families · two layers where a family has both open and minimally invasive members · as many as the source's headings warrant, per family
**Leaning:** one layer until the candidate list says otherwise; the site folds by family, and a second layer only pays off where a family has more members than fit one fan. Decide while writing the edges (chunk `broader-edges`). (2026-09-10)
**Settled by:** chunk `broader-edges` of the current pass.

