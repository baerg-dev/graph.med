---
name: main-branch-protection
description: The default branch takes changes only through an approved pull request; force-pushes and deletion are refused outright.
metadata:
  type: project
---

Every change to the default branch arrives through a pull request that a human has
approved. Approvals are dismissed when new commits are pushed, so the reviewer always sees
the state being merged. Force-pushing and deleting that branch are refused outright. None
of this is waivable by the agent.

**Why:** the bot is the author of its own pull requests, and GitHub does not let an author
approve their own — which is what makes the review a real gate rather than a formality,
and why the agent's identity is deliberately not a human's ([[credential-handling]]).

**How to apply:** a rejected `git push origin main` or `gh pr merge` is this working, not
an obstacle — report it and stop, do not retry with other flags or look for another route.
Push a branch and open a pull request instead ([[editing-your-own-instructions]]). Before
stating that a particular protection is in place, check rather than assume: a branch rule
can be configured and still not apply.
