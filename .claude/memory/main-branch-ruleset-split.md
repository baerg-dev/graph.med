---
name: main-branch-ruleset-split
description: What actually protects the default branch — one ruleset requiring review, and a second that is active but matches no branches.
metadata:
  type: project
---

Verified against the API on 2026-08-31:

| Ruleset | Enforcement | Targets | Bypass | Rules |
|---|---|---|---|---|
| `main-require-review` | active | `~DEFAULT_BRANCH` | **empty** | `pull_request`: 1 approval, dismiss stale on push, require approval of most recent push, extra approval for unattributed changes |
| `main-block-force-delete` | active | **nothing** — `ref_name.include` is `[]` | empty | `deletion`, `non_fast_forward` |

`gh api repos/<org>/<repo>/rules/branches/main` reports exactly one rule in force:
`pull_request`. The second ruleset contributes nothing, because a ruleset with an empty
include list matches no branch. Note also `require_code_owner_review: false`, and there is
no CODEOWNERS file in the repository ([[no-path-based-restrictions]]).

**Why:** the intended design is two rulesets, so that the irreversible operations stay
absolute even where a bypass exists. Only the first one is doing anything. The practical
exposure is small — the `pull_request` rule already refuses any direct push to the default
branch, force-pushes included, and GitHub will not delete a default branch — but the
documented second layer is not there, and nothing would catch it if the first were ever
relaxed.

**How to apply:** a rejected `git push origin main` or `gh pr merge` is the
`pull_request` rule working ([[security-enforced-outside-model]]) — do not retry with
other flags. Do not claim force-push or deletion protection is in place on the strength of
the ruleset existing; check `rules/branches/main`, which reports what is actually applied.
