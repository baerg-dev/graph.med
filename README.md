# graph.med

Open Medical Knowledge Graph.

> **Status: at inception.** There is no source tree or build system yet. What exists
> is the design (`docs/`), the one schema (`schema/schema.yaml`), the validator that
> enforces it and the CI that runs it (see "Checks"), and the pool under `data/` as
> it lands through pull requests. This README describes how the project is worked
> on; it will describe what the project *is* once there is more to describe.

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

## Checks

One check exists: the validator, `tools/validate.py`, which checks everything under
`data/` against `schema/schema.yaml` — ids, enums, provenance, claim hashes, edges,
and optionally every quote against the cited page of its source. The commands, and
what each form checks, are in [`CLAUDE.md`](CLAUDE.md) under "Checks" — one home for
them, read by humans and agents alike. Python tooling is managed with
[`uv`](https://docs.astral.sh/uv/) (`pyproject.toml`, `uv.lock`); never pip.

CI runs the same validator (`.github/workflows/validate.yml`) on every pull request —
including every push to an open pull request — and on every push to `main`, as two
jobs: the offline structural check, then the quote verification, which downloads each
source, verifies its content hash and checks every quote.

Two facts about the workflow that contributors should know:

- **Workflow files are edited by humans only.** The bot's GitHub App has no
  `workflows` permission, so GitHub refuses any push from it that touches
  `.github/workflows/`. This is deliberate: an agent cannot change what CI runs.
  When an agent needs a workflow change, it puts the file's content in the pull
  request and a person commits it.
- **The workflow's token is read-only** — a repository setting, restated as
  `permissions: contents: read` in the file — so a run can check the repository but
  never write to it, approve anything, or trigger further runs.

Running the quote check inside the sandbox needs each source's domain on the egress
allowlist (`sbx policy allow network register.awmf.org` for the first source). The
download is cached under `~/.cache/graph.med/sources/` by content hash and is
ephemeral, like everything outside the repository.

## Source documents

Source documents — papers, guidelines, classification releases — are **not
committed to this repository**, and not rehosted anywhere else. Third-party
material carries its own licensing and does not belong in the history of a
PolyForm-licensed repository; the repository and its links to public sources
are the only assets. An agent that needs a source downloads it from its public
URL into the session's working copy (the source's domain needs an egress
allowlist entry — see "Development environment" above), extracts what it needs into
the graph, and references the public location; the downloaded copy is
ephemeral and never committed. The reasoning is recorded in
`.claude/memory/design/sources-referenced-never-rehosted.md`.

## License

PolyForm Noncommercial License 1.0.0 — see [`LICENSE`](LICENSE).
Copyright 2026 Robert Schwarzenberg, Anton Zolkin.
