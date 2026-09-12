# Work packages

This directory is the register of work that is agreed and not yet done. It is
written for a person joining the repository cold; the agent's step-by-step
procedure is `.claude/skills/next-work-package/SKILL.md`.

## What is here

```
docs/work/
├── README.md                 this file — the convention
├── LATER.md                  work that is named but not registered
├── initiatives/<id>.md       one file per initiative: title and scope
└── NNNN-<id>.md              one file per work package, in number order
```

A **work package** is one session's work for one agent, with a clear end: pages
of a guideline to extract, a linking pass over the semantic layer, a schema
change, a feature of the site, a change to the documentation or the tooling.
An **initiative** is the scope a set of packages serves — what is in, what is
out — so that each package can stay short. **Later** holds what is known but
not agreed as a package yet.

## How a package moves

1. **Registered** — a person adds `NNNN-<id>.md` in a pull request. The number is
   the next unused one and is never reused; the order of numbers is the order
   of work. Anyone may draft a package; it counts once the pull request is
   merged.
2. **Claimed** — an agent creates and pushes the branch `feat/<id>` before it
   writes a line. The branch on the remote *is* the claim; there is no status
   field to keep in sync. Two agents can work at once as long as their packages
   do not depend on each other.
3. **Done** — the pull request that finishes the package **deletes its file**,
   and a person merges it. Done work is not archived here: git holds what was
   done, the pull request holds what was learned. If a session cannot finish,
   the branch stays as the claim and the pull request says what is left.

The registry therefore lists only what is still to do, and a reader of the
directory sees the backlog and nothing else. The validator
(`uv run tools/validate.py`, run by CI on every pull request) checks that the
registry is sound: numbers unique, ids matching file names, dependencies pointing
at lower-numbered packages that still exist, initiatives that still have a
package, extraction packages naming a real source, and the sections below
present.

## A package file

```markdown
---
id: site-search-recall            # = the file name after its number; also the branch name
initiative: ui                    # a file under initiatives/
kind: build                       # extraction | linking | schema | build | docs | tooling
depends_on: []                    # ids of lower-numbered packages that must land first
# source: sources/<id>            # extraction only: the source entity …
# pages: 26-39                    # … and its physical pages
---

## Outcome
What is true when this is done — observable, not "implement X".

## Scope
In: what the package touches.
Out: what it must not widen into, said explicitly.

## Constraints
What the work must not violate: the spec sections, the memories, the rules.

## Open questions            (optional)
Entries of docs/open-questions.md the package waits on or must respect —
named, never restated. A human answers them there; an agent never does.

## Verification
How to prove it works: commands, captures, acceptance criteria.

## Notes                     (optional)
Anything that has no other home. Not progress, not decisions.
```

Two things deliberately have **no** place in a package file:

- **Progress.** Git has it. A package is not edited while it is worked on.
- **Decisions and history.** What was decided and why is a memory under
  `.claude/memory/design/`; what is still undecided is an entry in
  `docs/open-questions.md`; what a diff was unsure of is its pull request. A
  package links to those; it does not copy them.

## Where the rest of the handover lives

| What | Where |
|---|---|
| What is still to do | this directory |
| What is undecided, with the options and the leaning | `docs/open-questions.md` |
| What was decided, and why | `.claude/memory/design/` |
| What a change was unsure of | its pull request |
| What was done | git history |

The pull request is the handover between sessions; no session-snapshot file is
kept, because a stale one would be trusted.
