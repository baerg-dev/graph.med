---
name: parse-next-chunk
description: Continue parsing a registered source into the pool — one chunk per session, ending with a complete handover (PROGRESS.yaml updated, pull request opened). Invoke at the start of a session to pick up where the last one stopped.
---

# Parse the next chunk

One session processes **one chunk** — a chapter or subchapter cluster, roughly
5–15 recommendation boxes — and ends with a complete handover. Do not start a
second chunk; the value of this loop is that every session ends reviewable.

## Before extracting

1. Read `data/PROGRESS.yaml`. Take the first source whose `status` is
   `in_progress`; its `next` field names your chunk, and its `scope_policy`
   and `deferred` list say what is in and out of scope. **If no source is
   `in_progress`, or the source's `next` is `null`, parsing is done: report
   "done" — which source, which pass, and where the deferred work is listed —
   and stop.** Do not look for work elsewhere: a deferred item or an
   enrichment pass starts only when a human registers it in PROGRESS as a new
   pass with its own chunks. Read the spec (`docs/graph-representation.md`)
   and `schema/schema.yaml` if you have not this session.
2. Fetch the source: URL and expected sha256 are on its entity under
   `data/sources/`. **Verify the hash.** On mismatch or an unreachable URL,
   stop parsing: record what you found in PROGRESS (the URL may have drifted —
   AWMF renames expired assets with an `-abgelaufen` suffix), fix the source
   entity if the document merely moved, and hand that over instead. **Never
   parse an expired source.**
3. Extract the chunk's text (`pdftotext -layout`, physical pages from the
   chunk entry) and locate every recommendation box.
4. Branch: `feat/parse-<source-id>-<chunk-id>`.

If the schema does not cover something the chunk needs, the schema change is
its own commit **before** the data commit (spec §7) — and is named in the PR.

## Phase one — claims (mechanical)

For every recommendation box (and any criterion the box text depends on),
create a claim in `data/claims/<source-id>/<chunk-id>.yaml`:

- id `claims/<source-id>/<hash8>` where `hash8` = first 8 hex of
  sha256(`<locator>|<quote>`) — script it, never hand-compute;
- `label`: the full sentence, source language, `lang` tagged;
- `quote`: a short **verbatim substring** of the extracted text, contiguous on
  one line of the pdftotext output (layout columns break sentences across
  lines — verify each quote by substring search before writing it);
- `grade`, `verb`, `direction`, `consensus` exactly as printed; nothing the
  box does not state (underestimate, never upgrade);
- locator `#page=N` with the **physical** page.

## Phase two — linking (judgment, all `modelling`)

- For each claim: search `data/statements/` for an existing statement it bears
  on; `supports`/`contests` accordingly. Mint a statement only when none fits;
  slots reference concepts.
- For each slot: search `data/concepts/` and the terminology namespaces before
  minting a concept.
- Criteria claims attach with `refines` to the claim they qualify.
- Edges go to `data/edges/<source-id>/<chunk-id>.yaml`.

## The handover

1. Update `data/PROGRESS.yaml`: chunk → `done` with a one-line note (box
   count, entity counts, date), set `next` to the next pending chunk, extend
   `deferred` with anything you consciously skipped. **If no pending chunk
   remains, set `next: null` and the source's `status: done`** — the next
   invocation then reports "done" instead of parsing.
2. If a design question surfaced, add it to `docs/open-questions.md` (entry
   format is described there).
3. Commit (schema commit first if any, then infra/data), push, open a PR. The
   PR description is part of the handover: what was extracted, what you were
   unsure about (ambiguous boxes, hard linking decisions), what was deferred.
4. Stop. The merged PR plus PROGRESS.yaml is everything the next session needs.
