---
name: push-failure-triage
description: The kinds of push failure, which of them are the design working, and why unpushed commits are usually not at risk.
metadata:
  type: project
---

| Symptom | Meaning |
|---|---|
| git asks for a username | No credential reached git. Host-side; nothing to fix from in here. |
| `401` from git or `gh` | A credential was sent and refused. Also host-side. |
| Push to the default branch, or a merge, refused | Not a credential problem — the review gate ([[main-branch-protection]]). |
| Push refused for lack of `workflows` permission | Not a credential problem — the App deliberately cannot change CI. Hand the workflow file over in the PR (`rules/environment/git-identity.md`). |

The first two are reported, never worked around ([[credential-handling]]). The third is
not a failure at all.

Before treating unpushed work as at risk, check whether the workspace is mounted from the
host or is a clone: if it is mounted, the commits are already in the host's working tree
and a failed push has lost nothing.

**Why:** the first two rows get mistaken for each other, which leads to proposing a
replacement credential — the one move the design forbids. And an agent that believes its
commits are trapped will argue much harder for a workaround than one that knows they are
already safe.

**How to apply:** name which row you are in, report it, and stop.
