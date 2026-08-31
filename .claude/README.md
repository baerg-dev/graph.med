# `.claude/`

Operating instructions for coding agents working on this repository. `CLAUDE.md` at the
repository root describes the *project*; everything here describes *how work is done*
and by whom.

These files are read by the agent, not enforced by it. The constraints they describe —
branch protection, CODEOWNERS review, the sandbox's egress policy — are enforced by
GitHub and by the sandbox host. A rule file that drifts from what those systems actually
do is worse than none, because it gets trusted.

## Layout

| Path | What it holds |
|---|---|
| `rules/` | Topic-scoped instructions. One `.md` per topic. |
| `agents/` | Subagent definitions, one `.md` each. Currently empty. |
| `skills/` | Skills, one `<skill-name>/SKILL.md` each. Currently empty. |

## Rules

Every `.md` file under `rules/` is a rule. Whether it loads always or conditionally is
decided by one frontmatter key:

- **No `paths:` key** — the rule loads at the start of every session, like `CLAUDE.md`.
- **A `paths:` list** — the rule loads when a file matching one of the patterns comes
  into context. Patterns are matched gitignore-style against the path relative to the
  repository root, so `agent-inbox/**` covers everything in that directory.

| Rule | `paths:` |
|---|---|
| `sandbox-environment.md` | — always |
| `git-identity.md` | — always |
| `contribution-workflow.md` | — always |
| `agent-inbox.md` | `agent-inbox/**` |
| `documentation.md` | `**/*.md` |
| `governed-files.md` | `.claude/**`, `.github/**`, `CLAUDE.md`, `CODEOWNERS` |

Three things worth knowing before adding one:

- **Frontmatter is stripped before the rule reaches the model.** `description:` is for
  the human reading the directory, not for the agent; put anything the agent needs in
  the body.
- **Path scoping fires on reading a file, and is silent when it does not fire.** A rule
  with an unmatched or mistyped pattern produces no error — it simply never appears. After
  adding one, open a file it covers and confirm it is in context.
- **A rule is read in full when it loads.** One topic per file; keep it short. `**/*.md`
  is about as broad as a scope should get.

## The sandbox

Everything here is written for an agent running inside a Docker Sandbox (`sbx`): only
this repository is mounted, egress is deny-by-default, and nothing outside the workspace
survives the sandbox. `rules/sandbox-environment.md` is the full account; `README.md` at
the root covers the same environment from the contributor's side.

## Changing anything in here

This directory is covered by CODEOWNERS: changes land only through a pull request a
human approves. Say explicitly in the description what a change permits that was not
permitted before, and do not bundle it with unrelated work. See `rules/governed-files.md`.
