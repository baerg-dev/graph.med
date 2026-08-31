---
description: The bot identity commits are made under, and why the GitHub credential is not yours to hold.
---

# Who you are, and what you hold

Commits and pull requests are authored by a GitHub App bot, not by a human:

```
user.name   baerg-dev-agentic-coding-bot[bot]
user.email  321302308+baerg-dev-agentic-coding-bot[bot]@users.noreply.github.com
```

Set these before your first commit if they are not already set:

```bash
git config --global user.name  "baerg-dev-agentic-coding-bot[bot]"
git config --global user.email "321302308+baerg-dev-agentic-coding-bot[bot]@users.noreply.github.com"
```

A grey silhouette instead of the bot avatar on GitHub means the email is wrong. Fix it
rather than ignoring it. The inference runs only in that direction: a *correct* avatar
proves nothing, because `user.email` renders the bot regardless of which credential
actually pushed. The server-side facts are the push actor and the PR author — see
`.claude/memory/commit-author-is-not-evidence.md`.

**The bot is deliberately a different party from the repository owner.** GitHub will
not let an author approve their own pull request, so this separation is what makes the
review gate real rather than decorative. Do not commit or push under a human identity,
and do not respond to a failed push by changing the git identity.

## Credentials

You do not hold a GitHub credential. Authentication happens outside the sandbox: you make
ordinary git and `gh` calls, and the host authenticates them on your behalf. Any
token-shaped value in your environment is a placeholder.

- Do not print, log, copy or attempt to resolve it. Nothing useful is reachable from here.
- **Never put a token in a remote URL.** Git persists it into `.git/config` in plaintext,
  and that file is inside the mounted workspace.
- A `401` means a host-side problem. Report it; do not work around it by asking for a
  token, substituting one, or writing one into a shell environment file.
- `gh auth status` reporting "not logged in" is expected and does not mean pushes will
  fail — the CLI's auth state is unrelated to how requests are authenticated.
