---
name: commit-author-is-not-evidence
description: The bot avatar on a commit is cosmetic and forgeable; the push actor and PR author are the only server-side identity facts.
metadata:
  type: project
---

`user.email` set to the bot address renders the bot's avatar regardless of which
credential actually pushed. It is display, not identity. The facts GitHub records
server-side are the push actor and the PR author:

```bash
gh pr list --state all --json number,author,createdAt
gh api repos/<org>/<repo>/activity \
  --jq '.[] | [.timestamp,.actor.login,.activity_type] | @tsv'
```

**Why:** a correct avatar is equally consistent with a human PAT having done the push, so
it distinguishes nothing. Only an assertion about the live credential does — which is what
the two calls above are for.

**How to apply:** never offer a correct-looking commit or avatar as evidence that the
identity plumbing is sound. A *wrong* avatar still signals a misconfigured `user.email`
and is worth fixing — but the inference only runs in that direction.
