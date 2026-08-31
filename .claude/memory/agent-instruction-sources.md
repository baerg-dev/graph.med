---
name: agent-instruction-sources
description: A parent-directory CLAUDE.md is loaded every session as project instructions, is agent-writable, and is in no repository — so edits to it never reach a pull request.
metadata:
  type: project
---

The review gate is that every change reaches `main` through a pull request a human
approves ([[no-path-based-restrictions]]). That covers every file *in the repository*.
Not every instruction the agent loads is in the repository. Verified inside the sandbox on
2026-08-31:

- The mount is the **parent** directory, not the repository. `/home/claubert/myfiles/repos/CLAUDE.md`
  (~19 KB) sits one level above the working tree, is loaded as project instructions every
  session, is writable by the agent, and is in no git repository at all. An edit to it
  produces no diff, no pull request and no history — it simply takes effect next session.
- `~/.claude/` exists *inside* the VM and is agent-writable, including `settings.json` and
  `skills/`. It is the VM's own, freshly created — the host's per-user config genuinely
  does not leak in — but it is still an instruction surface outside the repo.

Check with `ls ../CLAUDE.md` and `git -C .. rev-parse --show-toplevel`.

**Why:** the model assumes an agent's instructions can only change through a reviewed
pull request. A writable instruction file one directory up is a way to change them with no
review at all, and it is loaded with the same authority as the repo's own rules. It is
also already wrong on substance: it recommends
`sbx secret set github -t "$(gh auth token)"`, which is both the wrong credential type and
the storage mode that caused [[frozen-secret-failure]].

**How to apply:** treat the repo's own rules as authoritative wherever the parent file
disagrees, and say so rather than following it. Do not edit it to fix a disagreement —
it is shared with any other repository under that directory, where its generic advice may
be correct. Narrowing the mount to the repository itself is the fix that restores
"instructions change only through review".
