---
name: push-failure-triage
description: How to tell the kinds of push failure apart under sbx, and why unpushed commits are usually not at risk.
metadata:
  type: project
---

| Symptom | Meaning |
|---|---|
| `could not read Username for 'https://github.com'` | No credential reached git — the proxy injected nothing. |
| `401 Bad credentials` | Something was sent and GitHub rejected it — an expired credential, or a placeholder the proxy did not substitute. |
| Push to `main`, or `gh pr merge`, rejected | Not a credential problem at all — the review gate ([[main-branch-protection]]). |

What is normal inside the sandbox, and what is not:

- `/run/agent-token` **absent** — correct. It is a host path; it was never mounted here
  ([[github-app-token-pipeline]]).
- No git credential helper configured — correct under sbx.
- `GH_TOKEN` holding a placeholder such as `gho_sbxproxymanaged000…` — expected. A real
  `ghs_`/`ghp_` value in the environment is an alarm, not a fix.
- A token in `/etc/sandbox-persistent.sh` — always wrong.

The cause is usually host-side and invisible from in here, so check what the credential
itself says ([[commit-author-is-not-evidence]]) before theorising about the chain.

Before treating unpushed work as at risk, check the workspace mode: if `/run/sandbox/source`
does not exist the workspace is bind-mounted **direct** from the host, so commits are
already in the host's working tree and nothing is lost. In clone mode they live only in
the sandbox until fetched.

**Why:** the first two rows get misdiagnosed as each other, which leads to proposing a
replacement credential — the one move the design forbids. And an agent that believes its
commits are trapped will push harder for a workaround than one that knows they are safe.

**How to apply:** name the row you are in, say which link of the chain is missing, and
stop. Do not substitute a credential or retry with different flags.
