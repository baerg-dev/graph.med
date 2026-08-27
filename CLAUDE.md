# graph.med

Open Medical Knowledge Graph.

Licensed under the PolyForm Noncommercial License 1.0.0 (see `LICENSE`).
Copyright 2026 Robert Schwarzenberg, Anton Zolkin.

The repository is at inception: it currently contains only `README.md`,
`LICENSE`, and this file. There is no source tree, build system, dependency
manifest, or test suite yet. Project-specific guidance — data sources and their
licenses, graph schema, validator, setup and test instructions — belongs here
once it exists. Do not document tooling that does not exist.

---

# Agent environment and contribution workflow

Where you are running, who you are, and how work leaves this sandbox. These
constraints are enforced by GitHub and by the sandbox host, not by your compliance
with this file.

## Where you are

You are running inside a Docker Sandbox (`sbx`) — a microVM with its own kernel, its
own network namespace, and a host-side proxy for all outbound traffic.

- **Only the workspace directory is mounted.** Nothing else of the host filesystem
  exists from your point of view. Paths outside the repo will not resolve.
- **Egress is deny-by-default.** HTTP/HTTPS reach only allowlisted domains; raw TCP,
  UDP and ICMP are blocked. If a fetch or install fails, suspect the network policy
  before the URL.
- **Nothing persists between sandboxes** except the workspace. Do not store state
  outside the repo and expect to find it later.

### Practical mechanics

Consequences of the above that come up when actually running something:

- **Shell state does not carry between commands.** Persist environment variables by
  appending `export` lines to `/etc/sandbox-persistent.sh`, which is sourced before
  every command. Never add shell *completion* scripts there — they break every
  subsequent command.
- **Installed packages are ephemeral.** `sudo`, `npm`, `pip` and `uv` work, but
  anything they install lives only as long as the sandbox. A tool needed to build or
  test this project belongs in a manifest in the repo, not in your shell history.
- **The sandbox has its own `localhost`.** To reach a service on the host machine,
  use `host.docker.internal:<port>`.
- **Services you start are not reachable from the host** until the user publishes the
  port from the host side. Bind to `0.0.0.0` or `::`, never `127.0.0.1`, or
  publishing cannot reach them.

## Who you are

Commits and pull requests are authored by a GitHub App bot, not by a human:

```
user.name   baerg-dev-agentic-coding-bot[bot]
user.email  321302308+baerg-dev-agentic-coding-bot[bot]@users.noreply.github.com
```

Set these before your first commit if they are not already set:

```bash
git config --global user.name  "baerg-dev-agentic-coding-bot[bot]"
git config --global user.email "321302308+baerg-dev-agentic-coding-bot[bot]@users.noreply.github.com"
```

A grey silhouette instead of the bot avatar on GitHub means the email is wrong. Fix it
rather than ignoring it — that mismatch usually indicates the identity plumbing is not
what it appears to be.

**The bot is deliberately a different party from the repository owner.** GitHub will
not let an author approve their own pull request, so this separation is what makes the
review gate real rather than decorative. Do not commit or push under a human identity,
and do not respond to a failed push by changing the git identity.

### Credentials

You do not hold a GitHub credential. `GITHUB_TOKEN` in your environment is a
placeholder; the host-side proxy substitutes a real, short-lived installation token
into outbound requests. (`GH_TOKEN`, which the `gh` CLI reads, is a placeholder for
the same reason — currently the literal `gho_sbxproxymanaged000…`.) Consequences:

- Reading `$GITHUB_TOKEN` gives you nothing useful. Do not print it, log it, copy it
  into files, or attempt to extract the real value.
- The real token expires within the hour and is scoped to this one repository.
- A 401 from GitHub means the host-side pipeline has a problem. Report it; do not work
  around it by asking for a token or embedding one anywhere.
- **Never put a token in a remote URL.** Git persists it into `.git/config` in
  plaintext, and that file is inside the mounted workspace.
- `gh auth status` reporting "not logged in" is expected and does not mean pushes will
  fail — the CLI's auth state is unrelated to the proxy's network-level substitution.

## What you may and may not do

| Action | Allowed |
|---|---|
| Read anything in the workspace | Yes |
| Create a branch, commit, push that branch | Yes |
| Open a pull request | Yes |
| Push directly to `main` | **No** — server-side rule, will fail |
| Approve a pull request | **No** — you are the author |
| Merge a pull request | **No** — requires a human approval first |
| Force-push or delete `main` | **No** — blocked for everyone |
| Modify `.github/`, `.claude/`, `CLAUDE.md`, `CODEOWNERS` | Only via PR with human review (CODEOWNERS) |

The last row deserves attention: a change that widens a deny list, adds a workflow, or
edits this file is the highest-leverage change available to you and the least likely to
be read carefully. Call such changes out explicitly in the PR description rather than
bundling them with unrelated work.

## Working on the code

1. **Read before writing.** Understand the existing conventions in the files you are
   about to touch. Do not introduce a new pattern where an established one exists.
2. **One reviewable idea per branch.** Use a descriptive name (`fix/validator-timeout`,
   `feat/export-json`). Unrelated changes go in separate branches.
3. **Run the checks locally before proposing.** Treat their output as the first comment
   on your own PR. A change that does not pass is not proposed.
4. **Keep diffs small.** A human has to read this. If a change cannot be reviewed in
   one sitting, split it.

## Creating a pull request

```bash
git checkout -b fix/validator-timeout
# ... make changes, run the checks ...
git add -A
git commit -m "fix: raise validator timeout for large inputs"
git push -u origin fix/validator-timeout
gh pr create --fill
```

Then stop. Do not attempt `gh pr merge` — it will fail, and that failure is the system
working correctly.

### What belongs in the PR description

- **What changed and why**, in terms a reviewer can check against the diff.
- **What you were unsure about.** Ambiguity you resolved by choosing, assumptions you
  made, anything you could not fully determine. An explicit uncertainty is cheaper to
  correct than a confident error.
- **Anything you deliberately did not do**, and why — out-of-scope fixes you noticed,
  cases you left unhandled on purpose.
- **Any change to configuration, CI, or agent-governing files**, named explicitly.

### After the PR is open

- Respond to review comments by pushing further commits to the same branch.
- Expect prior approvals to be dismissed when you push. That is intentional: a
  reviewer must see the new state, not the state they approved.
- Never set a review status or sign anything on behalf of a person. Agents submit
  work; humans approve it.

## When something fails

| Symptom | Likely cause |
|---|---|
| `git push origin main` rejected | Working as designed. Open a PR. |
| `gh pr merge` rejected | Working as designed. A human approves and merges. |
| 401 from GitHub | Host-side token pipeline. Report; do not work around. |
| A fetch or package install fails | Sandbox egress policy. Report the domain. |
| A path outside the repo does not exist | Correct. Only the workspace is mounted. |

For the first two: do not retry with different flags and do not look for an alternative
route. They are the review gate. Defeating them would defeat the point of having one.
