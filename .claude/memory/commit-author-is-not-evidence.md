---
name: commit-author-is-not-evidence
description: A commit's author line is display only — it is not evidence about which credential produced the commit.
metadata:
  type: project
---

`user.name` and `user.email` decide what a commit *looks* like on GitHub. They are set
locally and say nothing about how it was authenticated. The identity that matters is
recorded server-side, in the push and pull-request records.

**Why:** an author line that looks correct is consistent with several different things
having produced it, so it distinguishes nothing. A *wrong* one is still worth fixing — it
means the local config is off — but the inference only runs in that direction.

**How to apply:** never offer a correct-looking commit as evidence that the setup is
sound. If identity genuinely needs establishing, that is a question for the maintainer to
answer from the repository's server-side records, not something to infer from a diff.
