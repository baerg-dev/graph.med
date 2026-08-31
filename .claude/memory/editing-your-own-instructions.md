---
name: editing-your-own-instructions
description: An agent may edit the files that instruct it — the obligation is to say so plainly in the pull request.
metadata:
  type: project
---

Agents edit anything here: code, `CLAUDE.md`, the rules under `.claude/rules/`, these
memories. They commit under the bot identity, push a branch and open a pull request. They
do not merge. A human reviews and merges every change
([[main-branch-protection]]).

**Why:** the gate is not which files may be touched — it is that nothing lands without a
person approving it, and that applies to every path equally. So a change to your own
instructions is permitted, and the review is what makes it safe.

**How to apply:** when a change touches the files that govern agents, name it in the pull
request description and say what it permits that was not permitted before. Keep it out of
an unrelated feature diff, where a reviewer scanning for code changes will not notice that
the rules moved. And never edit a rule to unblock yourself: if one is stopping you, that is
a question for the user, not an edit to make.
