# graph.med

Open Medical Knowledge Graph.

> **Status: at inception.** There is no source tree, build system, dependency
> manifest or test suite yet. This README describes how the project is worked on;
> it will describe what the project *is* once there is something to describe.

## Development environment (sbx)

Work on this repository happens inside a **Docker Sandbox (`sbx`)** — a microVM
with its own kernel and its own network namespace, started and managed from the
host by the `sbx` CLI. Both human and agent contributions are made from one.

What that means in practice for a contributor:

- **Only this repository is mounted.** Nothing else of the host filesystem is
  visible from inside the sandbox, and paths outside the workspace do not
  resolve. Anything the project needs must live in the repository.
- **Outbound network is deny-by-default.** HTTPS reaches allowlisted domains
  only; raw TCP, UDP and ICMP are blocked. A blocked request returns HTTP 403
  with the reason in the body. Allow a domain from the host:

  ```bash
  sbx policy allow network <domain>
  sbx policy log                      # what was blocked, and by which rule
  ```

- **Installed packages are ephemeral.** They live as long as the sandbox does.
  A tool needed to build or test this project belongs in a manifest in the
  repository, not in someone's shell history.
- **Services are not reachable from the host** until the port is published, and
  they must bind to `0.0.0.0` or `::` rather than `127.0.0.1`:

  ```bash
  sbx ports <sandbox-name> --publish 8080:8080/tcp
  ```

Agent-specific rules — bot identity, credentials, what an agent may and may not
do — are in [`.claude/`](.claude/README.md); [`CLAUDE.md`](CLAUDE.md) describes the
project itself.

## Sharing files with the project

Source documents — papers, guidelines, reports — are **not committed to this
repository**. They travel through a cloud drop folder instead, which keeps
third-party material and its licensing out of the Git history.

**To send a document in:** open the upload link and drag the file onto the page.
You need no account, no Git and no terminal.

> **Upload link:** _not yet created — see "Current status" below._

**What happens to it:** the folder behind that link is synced one way onto a
maintainer's machine, into `agent-inbox/` inside this repository. That directory
is gitignored, so nothing in it is ever committed and it is empty in a fresh
clone. The sandbox reads those files as ordinary local files — no network access
and no credentials are involved on the sandbox side.

**Maintainer side**, once per machine:

```bash
rclone config                                              # authorize the remote
rclone copy <remote>:graph.med-inbox ./agent-inbox         # then run on a timer
```

The sync is deliberately one-way. A bidirectional sync would propagate a local
deletion back to the cloud, where it could destroy someone else's submission.

**Please do not send** anything patient-identifiable, and nothing under terms
that forbid redistribution. An open upload link is the wrong channel for either.

### Current status

The provider is not fixed yet. It needs two things: a file-request feature so
contributors can upload without an account, and an `rclone` backend so the
maintainer side can sync. Dropbox, OneDrive, Box and pCloud all qualify. Google
Drive does not — it has no anonymous upload path.

Once a remote and an upload link exist, they replace the placeholder above.

## License

PolyForm Noncommercial License 1.0.0 — see [`LICENSE`](LICENSE).
Copyright 2026 Robert Schwarzenberg, Anton Zolkin.
