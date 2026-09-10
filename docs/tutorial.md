# A walk through graph.med

> **Who this is for.** Anyone joining the project — a physician, a contributor, an
> agent — who wants to understand what is in the pool and why it is shaped the way
> it is, before reading the specification. Everything here is real: the example is
> one recommendation of the POMGAT guideline as it sits in `data/` today. The
> authority on the model is `graph-representation.md`; on the site,
> `publication.md`; on syntax, `schema/schema.yaml`. This page only explains.

The site is at **[graph.med](https://graph.med/)**, and the first view is
[graph.med/pomgat-lv-1.0](https://graph.med/pomgat-lv-1.0/). Open it next to this
page.

---

## 1. The question the project answers

A clinical guideline is a long PDF. A physician wants one thing from it: *for this
patient, in this situation, what does the guideline say, and where does it say
that?* graph.med takes guidelines apart into pieces small enough to answer that
question, keeps every piece tied to the exact passage it came from, and draws the
pieces as a decision tree you can read on a phone.

Two rules shape everything else:

- **Nothing is invented.** Every piece of knowledge points at a passage in a
  public document, with a quote a machine can check. Where the project adds
  something of its own — a grouping, a wording — it says so.
- **The document is not the knowledge.** A guideline's chapters are how one
  publisher arranged one document. The knowledge is what the recommendations say,
  for whom, under which condition. The pool models the second and remembers the
  first only as provenance.

## 2. One recommendation, from the page to the graph

Take recommendation 6.7 of POMGAT, on page 63, in section 6.1.3 "Pankreas":

> Nach Pankreasresektion kann die abdominelle Drainage im frühen postoperativen
> Verlauf (bis 4. postoperativer Tag) gezogen werden, wenn das Drainagesekret
> initial auf ein geringes Risiko einer Pankreasfistel hinweist.

Here is how it lives in the pool, layer by layer.

### The source

The guideline itself is an entity, `sources/pomgat-lv-1.0`: a title, the public
URL at the AWMF register, a content hash of the PDF, the licence line, and the
document's complete table of contents. **The PDF is never copied into the
repository.** Everything links to the register's own copy; the hash detects if
that copy ever changes.

### The claim — what the source says, where

```yaml
- id: claims/pomgat-lv-1.0/6b9239a9        # derived from the anchor below, never chosen
  type: claim
  lang: de
  kind: recommendation
  recommendation_no: '6.7'
  section: "6.1.3"                         # where in the document; must exist in the outline
  label: Nach Pankreasresektion kann die abdominelle Drainage im frühen postoperativen
    Verlauf (bis 4. postoperativer Tag) gezogen werden, wenn das Drainagesekret initial
    auf ein geringes Risiko einer Pankreasfistel hinweist.
  grade: '0'
  verb: kann
  direction: for
  consensus: starker_konsens
  source:
    at: sources/pomgat-lv-1.0#page=63
    quote: kann die abdominelle Drainage im frühen postoperativen
```

A **claim** is one place in one document and what is printed there: the sentence,
its grade, its verb, its direction, the consensus. The `source` is the anchor — a
physical page and a short verbatim quote. The validator can download the PDF and
check that the quote is on that page. The claim's id is a hash of the anchor, so two
people extracting the same sentence produce the same claim, and nobody can quietly
edit what the guideline said.

Claims are **mechanical**. Extracting them is reading, not judgment. That is why a
claim carries the grade and the statement below does not: grades come from
documents, never from us.

### The statement — the proposition the claim is evidence for

```yaml
id: statements/fruehe-drainageentfernung-pankreasresektion
type: statement
lang: de
label: Nach Pankreasresektion kann die abdominelle Drainage früh (bis 4. postoperativer
  Tag) entfernt werden, wenn das Drainagesekret ein geringes Pankreasfistelrisiko anzeigt.
short_label: "Frühe Drainageentfernung bei geringem Fistelrisiko"
slots:
  population: concepts/pankreasresektion
  action: concepts/fruehe-drainageentfernung
  condition: concepts/geringes-pankreasfistelrisiko
source: modelling
```

A **statement** is the proposition itself, written once, in the pool's own words.
Its `source: modelling` says exactly that: no document states this sentence; a
person or agent wrote it. What ties it to the guideline is an edge:

```yaml
- [claims/pomgat-lv-1.0/6b9239a9, supports, statements/fruehe-drainageentfernung-pankreasresektion, {source: modelling}]
```

Why two layers? Because a second guideline will speak about the same thing. Its
claim will `supports` — or `contests` — **the same statement**. The statement's
evidence grows; the statement itself is untouched; and where two guidelines
disagree, the disagreement is visible on one node instead of being resolved by
whoever edited last. A statement is deliberately the *smallest unit that can be
supported or contested on its own*, which is why one guideline box with three
sentences becomes three claims and, usually, three statements.

The **slots** are what make a statement navigable: *whom* it is for (population),
*what* it recommends (action), *when* (condition), *to what end* (outcome). The
site's decision tree is nothing but these slots drawn as questions and answers.

The `short_label` is the same proposition compressed for a box on the drawing — at
most 60 characters, and it must still tell the statement apart from its siblings.
Shortening a clinical sentence can change its meaning, so short labels are reviewed
like everything else.

### The concepts — the vocabulary

```yaml
id: concepts/geringes-pankreasfistelrisiko
type: concept
lang: de
label: Geringes Risiko einer postoperativen Pankreasfistel (nach initialem Drainagesekret)
short_label: "Geringes Pankreasfistelrisiko"
facet: finding
source: modelling
```

A **concept** is a thing the statements talk about: a procedure, a drug, a
finding, an outcome. It is thin — a label, maybe a definition, a `facet` saying
what kind of thing it is — and it *means*; it never claims. A concept cannot be
contested. Concepts are minted only after searching for an existing one, and
where a classification has a code for it, the code becomes a node of its own,
linked by a `codes_as` edge, so that two guidelines meet on the same code.

Concepts also carry the one hierarchy in the pool:

```yaml
- [concepts/kolorektale-resektion, broader, concepts/kolorektale-chirurgie, {source: modelling, as_of: "2026-09-10", lang: de,
   rationale: "Die kolorektale Resektion ist der Eingriff der kolorektalen Chirurgie."}]
```

`broader` means "is a special case of". It lets the site fold thirty-six patient
groups into ten families. It carries **no evidence and no inheritance**: a
recommendation for colorectal resection says nothing about its minimally invasive
variant unless the guideline says so. Where the guideline is silent, the gap stays
visible. That rule is what keeps the graph from improvising.

### The body text — what qualifies a recommendation

Recommendation boxes are terse; the paragraphs around them say when a
recommendation applies. Those paragraphs become claims too, related to the box by
an edge that says *how*:

```yaml
- [claims/pomgat-lv-1.0/8349aa77, refines, claims/pomgat-lv-1.0/6b9239a9, {source: modelling}]
```

The refining claim here is the criterion "Amylase-Konzentration im Drainagesekret
unter 5000 U/L am ersten postop. Tag" from page 64. It refines the recommendation;
it never inherits its grade. The other two relations are `supplements` and
`limits`. On the site they appear under "From the body text".

### The direction — derived, never stored

The site shows every recommendation as one of four words: **für**, **gegen**,
**abwägen**, **Lücke**. Nobody writes that word into the data. It is computed from
the claims: `soll`/`sollte` for or against give für or gegen; `kann` — the
guideline's own open recommendation — gives abwägen, with the lean shown beside it;
a box that says "no recommendation possible" gives Lücke. Our example is abwägen,
eher für. The rule is the same for every statement, so it can be changed in one
place and never drifts.

## 3. Where the chapters went

Section 6.1.3 appears exactly once in the example: on the claim, as `section`.
Statements and concepts never carry a chapter, because a statement can be
supported from two chapters and a concept used in five. The source entity carries
the whole table of contents, so the validator can check that every claim names a
real section, and so the site can count which sections nobody has extracted yet.

On the site, a chapter is a **filter**: the `§` panel narrows the tree to what one
section supports. It is never a node in the graph. What a chapter *means*
clinically — an organ, a phase — goes onto concepts, as facets and families, where
the next guideline with a different outline can meet it.

## 4. Views: the pool is one, the graphs are many

There is one pool and no separate graphs. A **view** is a named filter over the
pool — "everything drawn from POMGAT" — and every view is a page:
[graph.med/pomgat-lv-1.0](https://graph.med/pomgat-lv-1.0/). The unadorned page is
*floating*: it shows the pool as of the last build. A **cut** freezes a view at a
commit so that it can be cited, and will be added when someone needs to cite one.

Every entity has a page and a JSON document at its own identifier, so
`graph.med/statements/fruehe-drainageentfernung-pankreasresektion` is a working
link from anywhere, and `…/claims/pomgat-lv-1.0/6b9239a9` leads to the page and
the quote.

## 5. How to read the page

Left to right: the guideline, **Welche Population?**, the families of patient
groups by weight, each unfolding into its members, then **Welche Bedingung?** where
a statement has a condition, then the recommendation as a box — a direction glyph
and the short label, coloured by the guideline's grade — and its aim as a tag.
Tap a box: the details show the direction, the full sentence, the population,
action, condition and **source** on one footing, then the evidence, claim by claim,
with the quote and a link into the PDF at the cited page. The **copy** button
beside a quote is for viewers that cannot highlight the search from the link.

## 6. How the pool grows

Work is registered as **passes** of **chunks** in `data/PROGRESS.yaml`, one chunk
per session, each ending in a pull request a person reviews. A chunk extracts a
chapter (claims first, mechanical; then linking, judgment), or changes the schema,
or adds a site feature. The rules an agent follows are short and worth reading
once: read before writing; extract first, link second; search before minting;
contest, never overwrite; every statement needs provenance; underestimate, never
upgrade; prefer an explicit gap to an invented answer.

What is not decided yet lives in `open-questions.md`, with the options and the
current leaning, so that nobody re-derives it. What was decided, and why, lives in
`.claude/memory/design/`.

## 7. Words

| word | means |
|---|---|
| **source** | a public document: title, URL, content hash, licence, outline; never copied |
| **claim** | one passage of one source and what it states: verbatim quote, page, grade, verb |
| **statement** | a proposition in the pool's words, with slots; what claims support or contest |
| **concept** | a thing statements talk about; has a facet; can be a special case of another (`broader`) |
| **slot** | a statement's population, action, condition or outcome, filled with a concept |
| **edge** | a typed link: `supports`/`contests` (claim → statement), `refines`/`supplements`/`limits` (claim → claim), `broader`, `codes_as` (concept), `specializes`/`complements`/`conflicts` (statement → statement) |
| **section** | where in its document a claim was found; on the claim only |
| **view** | a named filter over the pool; a page on the site. A **cut** is a frozen view |
| **modelling** | provenance meaning "no document says this; we asserted it" |
| **direction** | für / gegen / abwägen / Lücke, derived from the claims |
| **chunk**, **pass** | one session's registered unit of work; an ordered list of them |
