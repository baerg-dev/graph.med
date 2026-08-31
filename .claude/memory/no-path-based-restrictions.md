---
name: no-path-based-restrictions
description: There are no per-path edit restrictions here — an agent may edit any file, including its own instructions; the single gate is human approval of every PR.
metadata:
  type: project
---

The intended model, as stated by the maintainer on 2026-08-31: agents edit anything —
code, `CLAUDE.md`, `.claude/rules/`, `.claude/memory/` — commit under the bot identity,
push a branch and open a pull request. They cannot merge. A human reviews and merges.

There is **no CODEOWNERS file** (verified: absent from all three valid locations, and the
repository's codeowners endpoint returns 404), and `main-require-review` sets
`require_code_owner_review: false`. So no path is owned by anyone in particular and no
file is off-limits to edit.

**Why:** the gate is not "which files may be touched" but "nothing reaches `main` without
a human approving it" — and that holds for every path equally, because the ruleset's
bypass list is empty ([[main-branch-ruleset-split]]). Adding CODEOWNERS would change who
must review a given path; it would not change whether review happens.

**How to apply:** do not tell the user that a path is protected by CODEOWNERS, and do not
refuse an edit on those grounds. Editing your own instructions is permitted — what is
required is that the pull request says so plainly, because a reviewer scanning a feature
diff will not otherwise notice that the agent rewrote its own rules.
