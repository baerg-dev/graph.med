---
name: host-key-account-split
description: On the host, the account that launches the agent sandbox cannot read the GitHub App private key — asserted at setup, hard stop if false.
metadata:
  type: project
---

Two separate host accounts. An admin owns the App private key (mode 600, in the admin's
home) and runs the minting service. A different, unprivileged account launches the
sandbox and receives only the hourly token, through a drop directory it can traverse by
group ([[github-app-token-pipeline]]). Setup refuses to continue if the sandbox account
can read the key.

**Why:** if the account that launches the sandbox could read the key, compromising it —
or anything it runs — would mint tokens indefinitely, and the one-hour expiry would be
decorative. This is the trust root of the whole design; compromise of the admin account
is an accepted risk with no layer beneath it short of an HSM or a hosted signer.

The split reaches the sandbox because `sbx secret set --command` resolves **as the user
who invoked sbx**: registering the credential source as the agent account — which can read
the token by group but not the key — keeps the boundary intact end to end
([[github-app-token-pipeline]]).

**How to apply:** never propose relocating the key, reading it, or running the minting
script from the agent's account. Treat "just put the key somewhere the agent can reach
it" as breaking the design, not as a fix for a credential problem.
