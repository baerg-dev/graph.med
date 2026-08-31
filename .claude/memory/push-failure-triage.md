---
name: push-failure-triage
description: How to tell the three kinds of push failure apart, and why unpushed commits are usually not at risk.
metadata:
  type: project
---

Three failures look similar and mean different things:

| Symptom | Meaning |
|---|---|
| `could not read Username for 'https://github.com'` | No credential reached git at all — no helper configured, or the token file is absent. |
| `401 Bad credentials` from `gh` or git | A credential was sent and GitHub rejected it — expired, or a placeholder that was never substituted. |
| Push to `main` or `gh pr merge` rejected | Not a credential problem. The review gate ([[main-branch-ruleset-split]]). |

Check `git config --get credential.helper` and whether the token drop directory is
mounted before concluding anything ([[github-app-token-pipeline]]). A non-empty
`GH_TOKEN` in the environment is itself a signal: the sanctioned container has none, so
its presence means some other credential path is in play.

Before treating unpushed work as at risk, check the workspace mode: if `/run/sandbox/source`
does not exist the workspace is bind-mounted **direct** from the host, so commits are
already in the host's working tree and nothing is lost by a failed push. In clone mode
they live only in the sandbox until fetched.

**Why:** the first two failures get misdiagnosed as each other, which leads to proposing
a replacement credential — exactly the move the design forbids. And an agent that thinks
its commits are trapped will push harder for a workaround than one that knows they are
already safe on the host.

**How to apply:** identify which row you are in, say so, and stop. Report the missing
link; do not substitute a credential or retry with different flags.
