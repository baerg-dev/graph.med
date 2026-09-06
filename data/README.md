# data/ — the pool

The entities and edges of the knowledge pool, laid out by namespace
(`docs/graph-representation.md` §2; syntax authority: `schema/schema.yaml`):

```
data/
├── PROGRESS.yaml            parsing progress per source — the handover between sessions
├── sources/<source-id>.yaml one entity per source document
├── claims/<source-id>/<chunk>.yaml    the claims extracted from one chunk
├── concepts/<id>.yaml       one entity per file
├── statements/<id>.yaml     one entity per file
├── pathways/                structural nodes, when pathways are authored
├── edges/<source-id>/<chunk>.yaml     edges minted while processing that chunk
└── views/<id>.yaml          view definitions and their cuts
```

Claims and the edges minted alongside them are grouped per chunk for diff
ergonomics; semantic entities are one per file because they accumulate history
independently. Identity is the URL, never the file (spec §2).

Rules that bind everything here:

- **Source language, tagged.** All content stays in the source language with a
  `lang` tag; nothing is translated at extraction (spec §2, "Language").
- **Verbatim quotes, physical pages.** Every quote is a verbatim substring of
  the source's extracted text; `#page=N` counts physical PDF pages (spec §6.2).
- **Only current sources.** An expired guideline (AWMF: renamed with an
  `-abgelaufen` suffix, banner "wird aktuell überarbeitet") is not parsed — its
  successor will be, when published.
- **One chunk per session**, then a handover: `PROGRESS.yaml` updated, a pull
  request opened. The `parse-next-chunk` skill runs this loop.
