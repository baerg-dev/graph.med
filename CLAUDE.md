# graph.med

Open Medical Knowledge Graph.

Licensed under the PolyForm Noncommercial License 1.0.0 (see `LICENSE`).
Copyright 2026 Robert Schwarzenberg, Anton Zolkin.

The repository is at inception: it currently contains `README.md`, `LICENSE`, this
file, the design documentation under `docs/`, the one schema for the data pool
(`schema/schema.yaml`), and the `.claude/` directory described below. There is no
source tree, build system, dependency manifest, or test suite yet.
Project-specific guidance — data sources and their licenses, setup and test
instructions — belongs in this file once it exists. Do not document tooling that does
not exist.

## Where this runs

Inside a Docker Sandbox (`sbx`): only this repository is mounted, outbound network is
deny-by-default, and nothing outside the workspace persists. The agent-facing detail
is in `.claude/rules/environment/sandbox-environment.md`; the contributor-facing half
— the `sbx` commands themselves — is in `README.md`. Both describe one environment, so
a change to it has to reach both.

## How the documentation is organised

Documentation exists at three levels — **environment** (what is true of the world the
work runs in), **conventions** (how work is done here), and **design** (what is being
built, and how we intend to get there). The levels and what each owes the reader are
defined in `.claude/rules/conventions/documentation.md`.

This file describes the **project** and maps the rest. Design lives in `docs/`:
`docs/graph-representation.md` is the authority on how knowledge is represented —
one pool of source-anchored claims and a semantic layer, graphs as versioned views,
provenance, attestations, review — with `schema/schema.yaml` as the authority on
syntax, and `docs/open-questions.md`
carries what is not yet decided: the handover between sessions. How an agent is expected to operate
lives in `.claude/`, filed by level, so that each piece loads when it is relevant
rather than all of it, always:

```
.claude/
├── README.md                    what lives here, and how rules load
├── rules/
│   ├── environment/             the world you run in
│   │   ├── sandbox-environment.md   mounts, egress, persistence, shell mechanics
│   │   └── git-identity.md          the bot identity; why you hold no real token
│   └── conventions/             how work is done here
│       ├── contribution-workflow.md what you may and may not do; branch → PR → stop
│       ├── documentation.md         the documentation levels (*.md)
│       ├── governed-files.md        editing agent-governing files (.claude/, .github/, …)
│       └── memory.md                what project memory is, and the index of it
├── memory/                      durable facts, one per file, filed by level
│   ├── environment/
│   └── conventions/
├── agents/                      subagent definitions — empty; add one .md per agent
└── skills/
    └── handover/                end a session: update docs/open-questions.md
```

Rules without a `paths:` scope load at the start of every session; the two that have
one load when you touch a file they cover.

`memory/` is what an agent has learned about this project that the code does not
record — why a constraint exists, what was decided and rejected. It is checked in, so
it is reviewed and shared rather than private to one machine.
`rules/conventions/memory.md` carries its index.

`agents/` is deliberately empty, and `skills/` holds exactly one skill. This
repository has no build, test or data-ingest tooling yet, and a subagent or skill
that automates nothing would be guidance pretending to be capability. The exception
earned its place: ending a session with open questions is a real, repeated task, and
the `handover` skill maintains `docs/open-questions.md` for it. Add another only for
another such task — then say in the pull request what it does and what it is allowed
to touch.

One fact, one home: guidance that belongs in a rule is not restated here.
