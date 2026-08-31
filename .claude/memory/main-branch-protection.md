---
name: main-branch-protection
description: What is actually in force on the default branch — one pull-request rule, with an empty bypass list.
metadata:
  type: project
---

`gh api repos/<org>/<repo>/rules/branches/main` reports what applies, and is the only
answer worth trusting: a ruleset can exist, be `active`, and still match no branch. What
it reports today is a single `pull_request` rule from `main-require-review` — one
approving review, stale approvals dismissed on push, approval required of the most recent
push, extra approval for unattributed changes. Its **bypass list is empty**, so it binds
org owners as well as the bot.

That rule is also what refuses a direct push to the default branch, force-pushes included.
`require_code_owner_review` is `false` and there is no CODEOWNERS file
([[no-path-based-restrictions]]).

**Why:** a bypass actor skips the entire ruleset it appears on, so an empty bypass list is
what makes the gate apply equally to everyone. And a ruleset's existence says nothing
about its reach — the branch-level endpoint is the check that distinguishes intent from
effect.

**How to apply:** a rejected `git push origin main` or `gh pr merge` is this rule working
([[security-enforced-outside-model]]) — do not retry with other flags. Before stating that
any particular protection is in place, read `rules/branches/main` rather than the ruleset
list.
