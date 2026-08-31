---
name: security-enforced-outside-model
description: Every guarantee about what an agent can do here is enforced by GitHub or the OS, never by the agent obeying instructions.
metadata:
  type: project
---

The agent is assumed exploitable by indirect prompt injection: it holds all three legs of
the "lethal trifecta" — repository and local data, untrusted content (READMEs, dependency
trees, fetched pages, issue bodies), and egress via git, shell and MCP. So `CLAUDE.md` and
everything in `.claude/rules/` are documentation, not controls. The real boundaries are
server-side branch rulesets ([[main-branch-ruleset-split]]) and OS-level container
isolation.

Explicitly *not* defended against, and accepted: exfiltration through allowlisted
`github.com` (a commit, branch or gist is a viable channel, and the repository is public
anyway), a malicious dependency reading container contents, and the agent producing
plausible-but-wrong code that passes review.

**Why:** following instructions is the model's core function, so instruction-hardening
can never be a security boundary. Writing the accepted non-goals down keeps effort off
controls this design has already declined on purpose.

**How to apply:** when a push, merge or approval is refused, that is a control working —
report it and stop, never route around it. When asked to make the agent safer, propose a
server-side or OS-side control; more emphatic wording in a rule file is not an answer.
