---
name: main-branch-protection
description: What is actually in force on the default branch — one pull-request rule, with an empty bypass list.
metadata:
  type: project
---

Two rulesets, both `active`, both targeting `~DEFAULT_BRANCH`, both with an **empty
bypass list** — so they bind org owners as well as the bot:

| Ruleset | Rules |
|---|---|
| `main-require-review` | `pull_request`: 1 approval, stale approvals dismissed on push, approval of the most recent push, extra approval for unattributed changes |
| `main-block-force-delete` | `deletion`, `non_fast_forward` |

The split is deliberate: a bypass actor skips the entire ruleset it appears on, so keeping
the two irreversible operations in their own ruleset lets review be relaxed for humans
some day without force-push and deletion following it.

`require_code_owner_review` is `false` and there is no CODEOWNERS file
([[no-path-based-restrictions]]).

**Why:** a ruleset's existence says nothing about its reach. One of these two was `active`
with an empty target list for a while, matching no branch and protecting nothing, and the
ruleset list gave no hint of it. `gh api repos/<org>/<repo>/rules/branches/main` reports
what is actually applied, which is the check that distinguishes intent from effect.

**How to apply:** a rejected `git push origin main` or `gh pr merge` is this rule working
([[security-enforced-outside-model]]) — do not retry with other flags. Before stating that
any particular protection is in place, read `rules/branches/main` rather than the ruleset
list.
