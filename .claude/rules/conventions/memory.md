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
facts, and a memory only becomes part of the project when a human approves the pull
request that adds it — as with every other change. A claim recorded here has been read by
someone.

Which one to use: if a reviewer should see it, or another machine needs it, it belongs
here. Machine-local quirks belong in per-machine memory.

## The index

Read a file when its line below bears on what you are doing. Do not read them all
pre-emptively.

| Memory | The fact |
|---|---|
| `environment/security-enforced-outside-model.md` | Guarantees are enforced outside the model, never by the agent obeying a rule file. |
| `environment/credential-handling.md` | The agent holds no credential; the host authenticates on its behalf. Never substitute one. |
| `environment/main-branch-protection.md` | The default branch takes changes only through an approved pull request. |
| `conventions/editing-your-own-instructions.md` | Editing the files that instruct you is allowed; saying so in the PR is the obligation. |
| `environment/commit-author-is-not-evidence.md` | A commit's author line is display only, not evidence about the setup. |
| `environment/push-failure-triage.md` | Which failures are host-side, which are the design working, and why commits are usually safe. |
| `design/sources-referenced-never-rehosted.md` | Sources are never committed or rehosted; the graph links to public URLs, and agents download sources per session. |

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

File the memory in the subdirectory of the level it belongs to — `environment/`,
`conventions/`, `design/` (created with its first fact) — as
`conventions/documentation.md` defines them. A `design/` memory most often records
the resolution of an entry in `docs/open-questions.md` — see the `handover` skill.
Link related memories with `[[their-name]]`. Add a row to the index above in the same
commit — a memory absent from the index is a memory nobody will open.

What does **not** belong here: anything the code, the git history, `README.md` or a rule
already states; anything true only of today's session, such as a current outage or a
failure you are in the middle of debugging. Record the durable shape of a problem, not
its current instance. If a fact turns out to be wrong, delete the file rather than
leaving it to be trusted.
