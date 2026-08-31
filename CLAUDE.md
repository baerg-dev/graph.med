# graph.med

Open Medical Knowledge Graph.

Licensed under the PolyForm Noncommercial License 1.0.0 (see `LICENSE`).
Copyright 2026 Robert Schwarzenberg, Anton Zolkin.

The repository is at inception: it currently contains `README.md`, `LICENSE`, this
file, the `.claude/` directory described below, and the `agent-inbox/` drop directory.
There is no source tree, build system, dependency manifest, or test suite yet.
Project-specific guidance — data sources and their licenses, graph schema, validator,
setup and test instructions — belongs in this file once it exists. Do not document
tooling that does not exist.

## Where this runs

Inside a Docker Sandbox (`sbx`): only this repository is mounted, outbound network is
deny-by-default, and nothing outside the workspace persists. The agent-facing detail is
in `.claude/rules/sandbox-environment.md`; the contributor-facing half — the `sbx`
commands themselves — is in `README.md`. Both describe one environment, so a change to
it has to reach both.

## How this file is organised

This file describes the **project**. How an agent is expected to operate — the sandbox,
the bot identity, the review gate, the drop directory — lives in `.claude/`, so that
each piece loads when it is relevant rather than all of it, always:

```
.claude/
├── README.md                    what lives here, and how rules load
├── rules/                       instructions, loaded by topic
│   ├── sandbox-environment.md   mounts, egress, persistence, shell mechanics
│   ├── git-identity.md          the bot identity; why you hold no real token
│   ├── contribution-workflow.md what you may and may not do; branch → PR → stop
│   ├── agent-inbox.md           untrusted inbound documents  (agent-inbox/)
│   ├── documentation.md         the documentation convention (*.md)
│   └── governed-files.md        editing agent-governing files (.claude/, .github/, …)
├── agents/                      subagent definitions — empty; add one .md per agent
└── skills/                      skills — empty; add one <name>/SKILL.md per skill
```

The first three rules load at the start of every session. The last three carry a `paths`
scope and load when you touch a file they cover.

`agents/` and `skills/` are deliberately empty. This repository has no build, test or
data-ingest tooling yet, and a subagent or skill that automates nothing would be
guidance pretending to be capability. Add one when there is a real, repeated task for it
— then say in the pull request what it does and what it is allowed to touch.

One fact, one home: guidance that belongs in a rule is not restated here.
