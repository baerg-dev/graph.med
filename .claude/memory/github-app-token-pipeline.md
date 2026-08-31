---
name: github-app-token-pipeline
description: The agent's git credential is a short-lived GitHub App installation token delivered by file mount — never a PAT, never `gh auth token`.
metadata:
  type: project
---

The App private key never leaves the host admin account ([[host-key-account-split]]). A
timer mints a `ghs_…` installation token — one hour, scoped to this one repository — and
writes it to a tmpfs drop directory. That **directory** is bind-mounted read-only into the
agent container, where a git credential helper reads the file per operation. The agent
never handles the token as a value.

**Why:** a user PAT acts as the human who owns it, which would make the bot and the
reviewer one GitHub identity and deadlock the review gate instead of enforcing it
([[main-branch-ruleset-split]]). The mount is a directory because each refresh replaces
the inode — a file mount pins the container to a token that expired an hour ago.

**How to apply:** never suggest `gh auth token`, `sbx secret set github`, a personal
access token, or a token in a remote URL (git writes it to `.git/config` in plaintext).
If pushing fails, triage it with [[push-failure-triage]] and report which link of the
chain is missing rather than proposing a substitute credential.
