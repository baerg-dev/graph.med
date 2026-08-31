---
name: credential-handling
description: The agent holds no GitHub credential — the host authenticates outbound requests on its behalf, so there is nothing to find, fix, or substitute.
metadata:
  type: project
---

Authentication happens outside the sandbox. The agent makes ordinary git and `gh` calls
and the host authenticates them; no usable credential exists inside the VM, and the
environment variable that looks like one is a placeholder. This is deliberate: the agent
cannot leak what it does not hold.

**Why:** the credential belongs to a GitHub App bot rather than to a person. A personal
token would act as the human who owns it, making the bot and the reviewer one identity
and deadlocking the review gate rather than enforcing it
([[main-branch-protection]]).

**How to apply:** never propose obtaining, printing, storing or substituting a credential
— not `gh auth token`, not a personal access token, not one embedded in a remote URL, and
not one written into a shell environment file. If authentication fails, it is a host-side
matter: report the symptom ([[push-failure-triage]]) and stop. Do not investigate where
the credential comes from; that is not the agent's business and nothing useful is reachable
from here.
