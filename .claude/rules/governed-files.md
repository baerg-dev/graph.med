---
description: Extra care required when editing the files that govern agents and CI.
paths:
  - .claude/**
  - .github/**
  - CLAUDE.md
  - CODEOWNERS
---

# You are editing a file that governs agents

`.github/`, `.claude/`, `CLAUDE.md` and `CODEOWNERS` decide what an agent is told, what
CI runs, and who must review. A change here is the highest-leverage change available to
you and the least likely to be read carefully.

- **It requires human review.** CODEOWNERS covers these paths; the change reaches `main`
  only through a pull request someone else approves.
- **Call it out explicitly in the PR description.** Name the file and say what the
  change permits that was not permitted before. Do not bundle it with unrelated work —
  a rule change riding along in a feature branch is how a guardrail gets widened
  unnoticed.
- **Never weaken a constraint to unblock yourself.** If a rule, a deny list or a
  workflow is stopping you, that is a question for the user, not an edit to make.
  Report what blocked you and why you think the rule is wrong.
- **Keep the split honest.** `CLAUDE.md` is the project's own description; the files in
  `.claude/rules/` are the operating instructions. Guidance that belongs in a rule
  should not be duplicated back into `CLAUDE.md` — one home per fact.
