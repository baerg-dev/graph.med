---
name: parse-next-chunk
description: Do the next registered chunk of work on the pool — one chunk per session, ending with a complete handover (PROGRESS.yaml updated, pull request opened). Invoke at the start of a session to pick up where the last one stopped.
---

# Do the next chunk

One session does **one chunk** — a registered unit of work on one source: a
chapter cluster to extract, a schema change, a linking pass over existing
entities, a build feature — and ends with a complete handover. Do not start a
second chunk; the value of this loop is that every session ends reviewable.

## Before working

1. Read `data/PROGRESS.yaml`. Take the first source whose `status` is
   `in_progress`; its `next` field names your chunk. The chunk's `does` is
   your instruction, its `kind` says what it touches, its `depends` names the
   chunks that must be done first (they are, if the registry is maintained;
   check), and the source's `scope_policy` and `deferred` list say what is in
   and out of scope. **If no source is `in_progress`, or the source's `next`
   is `null`, the pass is done: report "done" — which source, which pass, and
   where the deferred work is listed — and stop.** Do not look for work
   elsewhere: a deferred item or a further pass starts only when a human
   registers it in PROGRESS with its own chunks. Read the spec
   (`docs/graph-representation.md`), `schema/schema.yaml` and, for a `build`
   chunk, `docs/publication.md`, if you have not this session. Read the
   entries of `docs/open-questions.md` the chunk names.
2. If the chunk reads the source (it names `pages`): fetch it — URL and
   expected sha256 are on its entity under `data/sources/`. **Verify the
   hash.** On mismatch or an unreachable URL, stop: record what you found in
   PROGRESS (the URL may have drifted — AWMF renames expired assets with an
   `-abgelaufen` suffix), fix the source entity if the document merely moved,
   and hand that over instead. **Never parse an expired source.** Extract the
   chunk's pages with `pdftotext -layout`.
3. Branch: `feat/<source-id>-<chunk-id>`.

If the schema does not cover something the chunk needs, the schema change is
its own commit **before** the data commit (spec §7) — and is named in the PR.

## Extraction chunks

Phase one — claims, mechanical. For every recommendation box (and any
criterion the box text depends on), create a claim in
`data/claims/<source-id>/<chunk-id>.yaml`:

- id `claims/<source-id>/<hash8>` where `hash8` = first 8 hex of
  sha256(`<locator>|<quote>`) — script it, never hand-compute;
- `label`: the full sentence, source language, `lang` tagged;
- `quote`: a short **verbatim substring** of the extracted text, contiguous on
  one line of the pdftotext output (layout columns break sentences across
  lines — verify each quote by substring search before writing it);
- `grade`, `verb`, `direction`, `consensus`, `recommendation_no`, `section`
  exactly as printed; nothing the box does not state (underestimate, never
  upgrade);
- locator `#page=N` with the **physical** page.

Phase two — linking, judgment, all `modelling`:

- For each claim: search `data/statements/` for an existing statement it bears
  on; `supports`/`contests` accordingly. Mint a statement only when none fits;
  slots reference concepts.
- For each slot: search `data/concepts/` and the terminology namespaces before
  minting a concept; a new concept gets its `facet`.
- Criteria claims attach with `refines` to the claim they qualify.
- Edges go to `data/edges/<source-id>/<chunk-id>.yaml`.

## Linking, schema and build chunks

The chunk's `does` says what to produce; the spec and `docs/publication.md`
say what it must look like. A linking chunk edits existing entities or adds
edges under the rules of spec §11 (every change `modelling` or sourced, search
before minting, nothing inherited, no review status written). A schema chunk
changes `schema/schema.yaml` and `tools/validate.py` together and leaves the
data valid. A build chunk changes `tools/build.py` and `tools/site/` and is
checked by building (`CLAUDE.md`, "Build") and reading the result.

## The handover

1. Update `data/PROGRESS.yaml`: chunk → `status: done`, set `next` to the next
   pending chunk whose dependencies are done, extend `deferred` with anything
   you consciously skipped. Chunk notes are for what the next session must
   know, not for counts and dates — git has those. **If no pending chunk
   remains, set `next: null` and the source's `status: done`** — the next
   invocation then reports "done" instead of working.
2. If a design question surfaced, add it to `docs/open-questions.md`; if the
   chunk settled one it names, apply the decision, delete the entry, and
   record the why as a memory (the `handover` skill describes both).
3. Run the validator; for a build chunk also the build. Commit (schema commit
   first if any, then data or tooling), push, open a PR. The PR description
   is part of the handover: what was done, what you were unsure of, what was
   deferred, and any change to the schema, the validator or agent-governing
   files, named explicitly.
4. Stop. The merged PR plus PROGRESS.yaml is everything the next session needs.
