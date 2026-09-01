# How I work with LLM agents

This repo collects the files that shape how I work with Claude Code. It
is a snapshot for the team, taken 2026-08-26. The live copies stay in my
home directory and in each product repo. Read this file first. It
explains the system. The other directories hold the source files.

## The idea in one paragraph

The agent is a coordinator, not a typist. It writes a spec with me, sends
investigation and code work to worker agents, runs an impartial review
loop, and reviews the lasting prose before a PR opens. Every rule the
agent must follow lives in a file that the agent reads. A rule that is
not in a file does not exist for the agent.

## The layers

Instructions load from the outside in. Each layer adds rules for a
smaller scope.

| Layer | File | What it holds |
| --- | --- | --- |
| Global | `~/.claude/CLAUDE.md`, `~/AGENTS.md` | Rules for every project. Model policy, PR comment ban, writing rules. |
| Workspace | `~/Developer/carboncloud/CLAUDE.md` and `AGENTS.md` | Points the agent at each repo's own guide and at the spec repo. |
| Repo | `<repo>/AGENTS.md`, `STYLEGUIDE.md` | Commands, architecture, review rules. `CLAUDE.md` in each repo is one line, `@AGENTS.md`. Not copied here, read them in each repo. |
| Skills | `~/.agents/skills/<name>/SKILL.md` | Reusable procedures the agent runs on a trigger phrase. |
| Agents | `~/.agents/agents/<name>.agent.md` | Personas for a subagent. |
| Memory | `~/.claude/projects/<project>/memory/` | Facts and feedback that persist between sessions. |

Copies of the global and workspace layers live under `instructions/`. The repo layer stays in each repo. Skills, agents, and memory examples live under `skills/`, `agents/`, and `memory/`.

Two conventions make the layers hold together:

- `CLAUDE.md` files only contain `@AGENTS.md`. The rules live in
  `AGENTS.md`, so other tools read the same file.
- `~/.claude/skills` is a symlink to `~/.agents/skills`. One skill
  directory serves every tool.

## The workflow

The `way-of-working` skill is the spine. For a task that changes code:

1. **Spec together.** Write the spec in chat. Draft product behaviour for
   the spec repo. Spawn investigation agents while the spec forms.
2. **Implement in worktrees.** Worker agents write the code in their own
   git worktrees off `origin/main`. Each brief carries the repo's
   `AGENTS.md`, the style guide, the glossary terms, and the test rules.
   Workers may not edit the spec. Tests come from the spec, before the
   code.
3. **Simplicity check.** One fresh agent asks if the change should exist
   and if less code reaches the goal. Runs once, before any review.
4. **Review loop.** A fresh review agent judges the change. A fix agent
   fixes. Repeat until the review passes, at most three rounds. No push
   between rounds. Fixes land as fixup commits.
5. **Copy review.** A reviewer checks comments, commit messages, and the
   PR description against the glossary and the writing rules.
6. **Open the PR.** Draft PR, short description, why before what.
7. **Review feedback.** Fixup commits while the review runs. Rebase and
   autosquash when the review is green.

Skills that carry each step: `way-of-working`, `simplicity-check`,
`review-loop`, `copy-review`, `commit-message`, `pr-description`,
`git-rebase`. See `skills/README.md` for the full list.

## The rules that matter most

Each rule links to the file that states it.

- **The main loop coordinates. Workers produce.** The agent never writes
  code in the main conversation. It investigates, designs, and briefs a
  worker. See `memory/examples/delegate-code-to-workers.md`.
- **Briefs carry the repo guidance.** A subagent starts with an empty
  context. The harness loads no `AGENTS.md` for it. Every brief pastes
  the relevant rules. See
  `memory/examples/worker-briefs-carry-repo-guidance.md`.
- **Pin the model on every subagent.** Subagents inherit the session
  model. A large fan-out on the top model burns the usage limit. See
  `instructions/global/CLAUDE.md`.
- **Lasting text follows ASD-STE100.** Active voice, at most 25 words
  per sentence, one word for one meaning, no em-dashes, no semicolons.
  This covers comments, commits, PR text, and specs. Chat is exempt.
- **The reviewer never sees earlier rounds.** Each review is a fresh
  agent with no history. This keeps the review impartial.
- **Ask whether the code should exist before asking whether it is
  right.** The simplicity check runs once and before the review loop.
- **The spec is the reference.** Workers cannot amend the document they
  are judged against. A needed spec change goes up to me.

## The spec repo

One repo in the workspace holds what the product should do and the words
we use for it. The workspace `AGENTS.md` names it. It is written for
agents and for the team. Before an agent writes lasting text, it reads
`GLOSSARY.md`. When review feedback settles a term, the term goes into the
glossary in the same session. Other repos never mention the spec repo. A
PR states the reason for a behaviour in its own text. The repo's own
`AGENTS.md` sets the structure and the language rules.

## Memory

Claude Code keeps one file per fact under the project's memory directory,
with an index in `MEMORY.md`. Feedback memories record a correction, why
it was given, and how to apply it. See `memory/README.md` for the format
and `memory/examples/` for real entries.

## Tools and plugins

- Skills installed from elsewhere: `impeccable` (pbakaus/impeccable) for
  frontend design work, `find-skills` (vercel-labs/skills) to discover
  more skills.
- Plugins: `gopls-lsp`, `typescript-lsp`, `figma`, `understand-anything`.
- `git-why`: prints the commit messages behind a line range instead of a
  blame table. https://github.com/JacobJNilsson/git-why

## Adopt it

1. Copy `instructions/global/AGENTS.md` to `~/AGENTS.md` and
   `instructions/global/CLAUDE.md` to `~/.claude/CLAUDE.md`. Edit the
   model policy to match your plan.
2. Copy `instructions/workspace/AGENTS.md` to `<workspace>/AGENTS.md` and
   `instructions/workspace/CLAUDE.md` to `<workspace>.claude/CLAUDE.md`
3. Copy the skills you want into `~/.agents/skills/` and symlink
   `~/.claude/skills` to that directory.
4. Copy `agents/` into `~/.agents/agents/`.
5. Check out your spec repo next to the product repos and name it in
   the workspace `AGENTS.md`.
6. Start a session in the workspace root and run `/way-of-working` on the
   next task.
