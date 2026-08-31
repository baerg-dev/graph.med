---
name: github-app-token-pipeline
description: The git credential is a GitHub App installation token that never enters the sandbox — sbx stores a resolving source and the host proxy injects it.
metadata:
  type: project
---

The App private key stays in the host admin account ([[host-key-account-split]]) and a
timer mints a `ghs_…` installation token — one hour, this repository only — into a tmpfs
file on the host. That file is **not** mounted into the sandbox. Instead the path is
registered as a resolving *source*:

```bash
sbx secret set github --command 'cat /run/agent-token/token' --refresh on-demand
```

sbx resolves it on the host, keeps it in the OS keychain, and the proxy injects it into
outbound requests. Inside the VM the agent sees only a placeholder — there is no token
file, no credential helper, and nothing to read, log, or exfiltrate.

**Why:** `--command` stores a source rather than a value, which is what preserves the
40-minute rotation; a stored value cannot rotate, so the keychain goes on serving a
credential that has expired, with no error anywhere. `--refresh on-demand` is mandatory because the
`55m` default would cache a resolve made at minute 39 of a 60-minute token until minute
94. A user PAT is doubly wrong: it acts as the human, collapsing the two-party review
gate ([[main-branch-protection]]).

**How to apply:** never suggest `gh auth token`, a PAT, `sbx secret set -t/--token`, a
token in a remote URL, or writing this token into `/etc/sandbox-persistent.sh` — that
last one puts it inside the VM and discards the whole benefit. Expect `/run/agent-token`
to be **absent** in the sandbox; its presence would be the anomaly. Triage failures with
[[push-failure-triage]].
