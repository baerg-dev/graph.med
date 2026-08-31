---
name: frozen-secret-failure
description: A credential stored as a literal value in the sbx keychain keeps being served after it dies — the signature is `(stored)` in `sbx secret ls`.
metadata:
  type: project
---

An installation token pasted into `sbx secret set` is valid for under an hour. It works,
expires, and the keychain keeps serving the corpse with no error anywhere. `sbx secret ls`
shows such an entry as `(stored)`; a correctly registered source does not
([[github-app-token-pipeline]]). This has happened here once: sessions that could push
were followed by sessions that could not, and nothing in between changed.

The type of credential that was frozen was never established, which matters more than the
outage: if it was a human PAT rather than an installation token, the agent was acting as
an org member who sits on the `main-review` bypass list, and the review gate was
ineffective while it was live. Assert the credential's *type*, not the commit's
appearance ([[commit-author-is-not-evidence]]):

```bash
gh api /installation/repositories --jq '.repositories[].full_name'  # exactly this repo
gh api /user --jq .login                                            # MUST fail
```

`/user` succeeding means a user token is in play.

**Why:** the failure is silent in both directions — a dead credential produces no
keychain error, and a wrong-type credential produces correct-looking commits. Only an
assertion about the live credential distinguishes them.

**How to apply:** on any credential oddity, check `sbx secret ls` for `(stored)` before
theorising, and run the two `gh api` calls above rather than trusting a bot avatar. A
changed secret only takes effect on a **new** sandbox — global secrets are injected at
creation time.
