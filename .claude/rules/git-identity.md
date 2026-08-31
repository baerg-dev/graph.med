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

You do not hold a GitHub credential. `GITHUB_TOKEN` in your environment is a
placeholder; the host-side proxy substitutes a real, short-lived installation token
into outbound requests. (`GH_TOKEN`, which the `gh` CLI reads, is a placeholder for
the same reason — currently the literal `gho_sbxproxymanaged000…`.) Consequences:

- Reading `$GITHUB_TOKEN` gives you nothing useful. Do not print it, log it, copy it
  into files, or attempt to extract the real value.
- The real token expires within the hour and is scoped to this one repository.
- A 401 from GitHub means the host-side pipeline has a problem. Report it; do not work
  around it by asking for a token or embedding one anywhere.
- **Never put a token in a remote URL.** Git persists it into `.git/config` in
  plaintext, and that file is inside the mounted workspace.
- `gh auth status` reporting "not logged in" is expected and does not mean pushes will
  fail — the CLI's auth state is unrelated to the proxy's network-level substitution.
