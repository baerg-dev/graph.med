---
name: main-branch-ruleset-split
description: The default branch is protected by two separate rulesets on purpose, because ruleset bypass is all-or-nothing.
metadata:
  type: project
---

`main-review` — pull request required, one approval, stale approvals dismissed on push,
approval required of the most recent reviewable push — bypasses for human org members.
`main-safety` — block force pushes, restrict deletions — has an **empty** bypass list and
binds org owners too. Both are Active, not "Evaluate". Separately, the org setting
"Allow GitHub Actions to create and approve pull requests" must stay unticked.

**Why:** a bypass actor skips the *entire* ruleset it appears on, so splitting keeps the
two irreversible operations absolute while leaving humans unblocked for ordinary work.
"Approval of the most recent push" specifically prevents getting a clean diff approved,
then appending commits and merging on the stale approval. If Actions could approve PRs, a
workflow would satisfy the review requirement and the gate would quietly cease to exist.

**How to apply:** a rejected `git push origin main` or `gh pr merge` is this design
working ([[security-enforced-outside-model]]) — do not retry with other flags or look for
another route. Any proposal to add an app, bot or deploy key to a bypass list is a
decision for the user, never a workaround to reach for.
