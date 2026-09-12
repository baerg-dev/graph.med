---
id: ui
title: The site as the physician reads it
---

The site changes the physician asked for after reading the live view
(`docs/publication.md` §3: "Folded by default", "Every branching is a question",
"Everything readable", "The interaction", "Chapters and search", "What the section
shows").

**Scope.** Build packages only: `tools/build.py` and `tools/site/`. No data change,
no schema change. Every package is checked in a browser on desktop and phone (the
`screenshot` skill), and its pull request links the preview at
`graph.med/preview/pr<N>/`.

**Out of scope,** listed in `LATER.md`: how structural and organisational
recommendations are told apart (needs data), grouping axes and specialised views,
extraction quality, review and feedback.
