---
name: agent-instruction-sources
description: Not every instruction the agent loads comes from a CODEOWNERS-gated file — a parent-directory CLAUDE.md and the VM's own ~/.claude are outside the repo.
metadata:
  type: project
---

The security concept holds that because the sandbox cannot see the host's `~/.claude`,
agent instructions can only come from in-repo files and are therefore all CODEOWNERS-gated.
The first half is true; the conclusion does not follow. Verified inside the sandbox on
2026-08-31:

- The mount is the **parent** directory, not the repository. `/home/claubert/myfiles/repos/CLAUDE.md`
  (~19 KB) sits one level above the working tree, is loaded as project instructions every
  session, and is in no git repository at all — so no CODEOWNERS rule can reach it.
- `~/.claude/` exists *inside* the VM and is agent-writable, including `settings.json` and
  `skills/`. It is the VM's own, freshly created — the host's per-user config genuinely
  does not leak in — but it is still an instruction surface outside the repo.

Check with `ls ../CLAUDE.md` and `git -C .. rev-parse --show-toplevel`.

**Why:** the governance argument is that `.claude/`, `CLAUDE.md` and `.github/` are the
only channels by which an agent can be told what to do, and all of them require human
review. An unreviewed instruction file one directory up defeats that for anything it says,
and it is loaded with the same authority as the repo's own.

**How to apply:** when reasoning about what governs this agent, count the parent
`CLAUDE.md` as an ungoverned input. Do not cite "all agent config is CODEOWNERS-gated" as
a property that currently holds. Narrowing the mount to the repository itself, or moving
that file into the repo, would make it true.
