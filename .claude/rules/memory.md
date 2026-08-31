---
description: The project's memory — durable facts about this project that are not derivable from the code, and the index of what is recorded.
---

# Project memory

`.claude/memory/` holds what an agent has learned about this project that the repository
does not otherwise record: design decisions, the reasoning behind constraints, and the
things that were only ever said out loud. One fact per file.

This is not Claude Code's per-machine memory. That lives outside the repository, is
private to one machine, and nobody reviews it. **Project memory is checked in**, so it is
versioned, it survives the sandbox, every contributor and every agent sees the same
facts, and — because `.claude/` is covered by CODEOWNERS — a memory only becomes part of
the project when a human approves the pull request that adds it. A claim recorded here
has been read by someone.

Which one to use: if a reviewer should see it, or another machine needs it, it belongs
here. Machine-local quirks belong in per-machine memory.

## The index

Read a file when its line below bears on what you are doing. Do not read them all
pre-emptively.

| Memory | The fact |
|---|---|
| `security-enforced-outside-model.md` | The agent is assumed prompt-injectable; guarantees come from GitHub, the microVM and the proxy, never from rule files. |
| `github-app-token-pipeline.md` | The credential never enters the sandbox: sbx stores a resolving source and the host proxy injects it. |
| `frozen-secret-failure.md` | A secret stored as a value keeps being served after it expires; `(stored)` in `sbx secret ls` is the signature. |
| `commit-author-is-not-evidence.md` | The bot avatar is cosmetic; push actor and PR author are the only identity facts. |
| `host-key-account-split.md` | The account that launches the sandbox cannot read the App private key, by assertion. |
| `main-branch-ruleset-split.md` | Two branch rulesets, deliberately, because bypass is all-or-nothing. |
| `agent-instruction-sources.md` | A parent-directory `CLAUDE.md` is loaded every session and no CODEOWNERS rule reaches it. |
| `push-failure-triage.md` | Telling the kinds of push failure apart; what is normal inside the sandbox and what is an alarm. |

## Writing one

```markdown
---
name: <kebab-case-slug, matching the filename>
description: <one line — this is what decides whether the file gets read>
metadata:
  type: project | reference
---

<the fact, stated plainly>

**Why:** <what makes it true, or what breaks without it>

**How to apply:** <what to do differently because of it>
```

Link related memories with `[[their-name]]`. Add a row to the index above in the same
commit — a memory absent from the index is a memory nobody will open.

What does **not** belong here: anything the code, the git history, `README.md` or a rule
already states; anything true only of today's session, such as a current outage or a
failure you are in the middle of debugging. Record the durable shape of a problem, not
its current instance. If a fact turns out to be wrong, delete the file rather than
leaving it to be trusted.
