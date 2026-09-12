---
name: next-work-package
description: Do the next registered work package — one per session, ending with a complete handover (the package removed from docs/work/, a pull request opened). Invoke at the start of a session to pick up where the last one stopped; it reports "nothing registered" when docs/work/ holds no package, and "all claimed" when every open package is taken.
---

# Do the next work package

One session does **one work package** — a registered unit of work: pages of a
source to extract, a linking pass over existing entities, a schema change, a
build feature, a docs change, a piece of tooling — and ends with a complete
handover. Do not start a second package; the value of this loop is that every
session ends reviewable. The convention itself, written for humans, is
`docs/work/README.md`; this file is the agent's procedure.

## Before working

1. **Find your package.** `git fetch origin`. The packages are the files
   `docs/work/NNNN-<id>.md`, in number order. Yours is the lowest-numbered one
   that is *open*: every id in its `depends_on` no longer has a file (done
   packages are removed), and no branch `feat/<id>` exists on `origin`
   (`git ls-remote --heads origin feat/<id>` prints nothing) — a branch is the
   claim. Skip claimed ones — but a claim with no pull request behind it
   (`gh pr list --head feat/<id>` is empty) and no commit beyond `main` is a
   session that never got to work: report it as a stale claim and let a
   human delete the branch; do not take it over on your own. **If
   `docs/work/` holds no package, report
   "nothing registered" and stop. If every open package is claimed, report
   "all claimed" and stop.** Do not look for work elsewhere: an entry in
   `docs/work/LATER.md` becomes a package only when a human registers it.
2. **Claim it before writing code:** `git checkout -b feat/<id>` from `main`,
   then `git push -u origin feat/<id>` at once, so that the branch exists on
   `origin` before anything else happens. (`docs/…` or `chore/…` where that
   fits better; the claim check looks for `feat/<id>` first, so prefer it.)
3. **Read the package** in full — Outcome, Scope, Constraints, Verification — and
   its initiative (`docs/work/initiatives/<initiative>.md`), then what it points
   at: the spec (`docs/graph-representation.md`), `schema/schema.yaml`,
   `docs/publication.md` for a build package, and the entries of
   `docs/open-questions.md` it names. A package whose Open questions gate it
   (box-colour gates `site-colour-by-direction`) is not open until the entry is
   settled; skip it and say so.
4. If the package reads a source (kind `extraction`, with `source` and
   `pages`): fetch it — URL and expected sha256 are on the source entity under
   `data/sources/`. **Verify the hash.** On mismatch or an unreachable URL, stop:
   fix the source entity if the document merely moved (AWMF renames expired
   assets with an `-abgelaufen` suffix), and hand that over instead. **Never
   parse an expired source.** Extract the pages with `pdftotext -layout`.

If the schema does not cover something the package needs, the schema change is
its own commit **before** the data commit (spec §7) — and is named in the PR.

## By kind

**extraction** — phase one, claims, mechanical: for every recommendation box
(and any criterion the box text depends on), a claim in
`data/claims/<source-id>/<package-id>.yaml`:

- id `claims/<source-id>/<hash8>` where `hash8` = first 8 hex of
  sha256(`<locator>|<quote>`) — script it, never hand-compute;
- `label`: the full sentence, source language, `lang` tagged; one claim per
  recommendation sentence, never one per box (memory
  `box-granularity-per-sentence`);
- `quote`: a short **verbatim substring** of the extracted text, contiguous on
  one line of the pdftotext output (layout columns break sentences across
  lines — verify each quote by substring search before writing it);
- `grade`, `verb`, `direction`, `consensus`, `recommendation_no`, `section`
  exactly as printed; nothing the box does not state (underestimate, never
  upgrade);
- locator `#page=N` with the **physical** page.

Phase two, linking, judgment, all `modelling`: for each claim, search
`data/statements/` for an existing statement it bears on and
`supports`/`contests` it; mint a statement only when none fits, its slots
referencing concepts. For each slot, search `data/concepts/` and the
terminology namespaces before minting a concept; a new concept gets its
`facet`. Criteria claims attach with `refines` to the claim they qualify. Edges
go to `data/edges/<source-id>/<package-id>.yaml`.

**linking** — edits existing entities or adds edges under spec §11: every change
`modelling` or sourced, search before minting, nothing inherited, no review
status written.

**schema** — changes `schema/schema.yaml` and `tools/validate.py` together and
leaves the data valid.

**build** — changes `tools/build.py` and `tools/site/`, checked by building
(`CLAUDE.md`, "Build"), reading the result, and looking at the page in a browser
on desktop and phone (the `screenshot` skill); the PR says what you saw and links
its preview at `graph.med/preview/pr<N>/`.

**docs** and **tooling** — the package's Outcome says what is true when it is
done; the documentation levels (`.claude/rules/conventions/documentation.md`)
say where a change goes; a change to a workflow file is handed over in the PR
description (`.claude/rules/environment/git-identity.md`).

Do not widen the package: what its Scope lists as out stays out, and a question
under its Open questions is answered by a human in `docs/open-questions.md`,
never silently by you.

## The handover

1. **Remove your package:** `git rm docs/work/NNNN-<id>.md`, and delete its id
   from every other package's `depends_on`. If it was its initiative's last
   package, `git rm` the initiative file too. What you consciously skipped, or
   found and could not do, goes into `docs/work/LATER.md`, stated as the durable
   shape of the work, not as a log; never register a package on your own. What
   the next session must know goes into the PR, into a memory if it is durable,
   or into `docs/open-questions.md` if it is undecided — not into the registry.
2. If a design question surfaced, add it to `docs/open-questions.md`; if the
   package settled one it names, apply the decision, delete the entry, and
   record the why as a memory (the `handover` skill describes both).
3. Run the validator (it checks `docs/work/` too); for a build package also the
   build. Commit (schema commit first if any, then data or tooling), push, open
   a PR. The PR description is part of the handover: what was done, what you
   were unsure of, what went into `LATER.md`, and any change to the schema, the
   validator or agent-governing files, named explicitly.
4. Stop. The merged PR removes the package and frees the branch name; that plus
   `docs/work/` is everything the next session needs.
