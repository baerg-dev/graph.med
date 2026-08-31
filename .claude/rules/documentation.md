---
description: How documentation in this repository is written and kept honest.
paths:
  - "**/*.md"
---

# Writing documentation in this repository

Every documentation file here carries a section on the sandbox, pitched at that file's
audience. `README.md` covers what a contributor needs — mounts, egress, published
ports, the `sbx` commands themselves. The rules under `.claude/rules/` cover what an
agent needs: identity, credentials, and what it may and may not do. When you add a
documentation file, give it one.

When the sandbox's behaviour changes, update **every** such section rather than only
the nearest one. A stale description of the environment is worse than no description,
because it gets trusted.

Two further conventions, both consequences of the repository being at inception:

- **Do not document tooling that does not exist.** No build system, dependency
  manifest or test suite exists yet. Describe what is here, not what is planned.
- **Say where a thing is described, once.** Each fact about the environment has one
  home — the contributor-facing half in `README.md`, the agent-facing half in
  `.claude/rules/`. Cross-reference rather than restate; two copies drift.
