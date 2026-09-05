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

## Source documents

Source documents — papers, guidelines, classification releases — are **not
committed to this repository**. Third-party material carries its own licensing
and does not belong in the history of a PolyForm-licensed repository. The route
by which such documents reach a working copy is deliberately not decided yet;
until it is, there is none.

## License

PolyForm Noncommercial License 1.0.0 — see [`LICENSE`](LICENSE).
Copyright 2026 Robert Schwarzenberg, Anton Zolkin.
