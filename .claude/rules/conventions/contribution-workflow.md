---
description: What an agent may and may not do in this repository, and how a change becomes a pull request.
---

# Contribution workflow

The constraints below are enforced by GitHub, not by your compliance with this file.
Hitting one is the system working, not an obstacle to route around.

## What you may and may not do

| Action | Allowed |
|---|---|
| Read anything in the workspace | Yes |
| Create a branch, commit, push that branch | Yes |
| Open a pull request | Yes |
| Push directly to `main` | **No** — server-side rule, will fail |
| Approve a pull request | **No** — you are the author |
| Merge a pull request | **No** — requires a human approval first |
| Force-push or delete `main` | **No** — refused outright |
| Modify `.claude/`, `CLAUDE.md` — your own instructions | Yes, like any other file — but say so in the PR |

No file is off-limits to edit. The single gate is that every pull request to `main` needs
a human approval, and that applies to every path equally. The last row still has its own
rule — see `governed-files.md` — because changing your own instructions is easy for a
reviewer to miss in a larger diff.

## Working on the code

1. **Read before writing.** Understand the existing conventions in the files you are
   about to touch. Do not introduce a new pattern where an established one exists.
2. **One reviewable idea per branch.** Use a descriptive name (`fix/validator-timeout`,
   `feat/export-json`). Unrelated changes go in separate branches.
3. **Run the checks locally before proposing.** Treat their output as the first comment
   on your own PR. A change that does not pass is not proposed. The checks and their
   commands are listed in `CLAUDE.md` under "Checks"; CI runs the same ones on every
   pull request and every push to `main`.
4. **Keep diffs small.** A human has to read this. If a change cannot be reviewed in
   one sitting, split it.

## Creating a pull request

```bash
git checkout -b fix/validator-timeout
# ... make changes, run the checks ...
git add -A
git commit -m "fix: raise validator timeout for large inputs"
git push -u origin fix/validator-timeout
gh pr create --fill
```

Then stop. Do not attempt `gh pr merge` — it will fail, and that failure is the system
working correctly.

### What belongs in the PR description

- **What changed and why**, in terms a reviewer can check against the diff.
- **What you were unsure about.** Ambiguity you resolved by choosing, assumptions you
  made, anything you could not fully determine. An explicit uncertainty is cheaper to
  correct than a confident error.
- **Anything you deliberately did not do**, and why — out-of-scope fixes you noticed,
  cases you left unhandled on purpose.
- **Any change to configuration, CI, or agent-governing files**, named explicitly.

### After the PR is open

- Respond to review comments by pushing further commits to the same branch.
- Expect prior approvals to be dismissed when you push. That is intentional: a
  reviewer must see the new state, not the state they approved.
- Never set a review status or sign anything on behalf of a person. Agents submit
  work; humans approve it.

## When something fails

| Symptom | Likely cause |
|---|---|
| `git push origin main` rejected | Working as designed. Open a PR. |
| A force-push to `main` rejected | Same rule — a force-push is still a direct push. |
| A push touching `.github/workflows/` refused for lack of `workflows` permission | Workflow files are human-only. Hand the file over in the PR — see `environment/git-identity.md`. |
| `gh pr merge` rejected | Working as designed. A human approves and merges. |
| 401 from GitHub | Host-side token pipeline. Report; do not work around. |
| A fetch or package install fails | Sandbox egress policy. Report the domain. |
| A path outside the repo does not exist | Correct. Only the workspace is mounted. |

For the first two: do not retry with different flags and do not look for an alternative
route. They are the review gate. Defeating them would defeat the point of having one.
