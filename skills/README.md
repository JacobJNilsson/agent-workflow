# Skills

A skill is a `SKILL.md` file with a name, a description, and a procedure.
The description holds the trigger phrases. Claude Code loads the skill
when a prompt matches, or when I type `/<name>`.

| Skill | Purpose |
| --- | --- |
| `way-of-working` | The end to end workflow for a code change. Spec, worktrees, review loop, copy review, PR. |
| `simplicity-check` | One fresh agent judges whether the change should exist and whether less code reaches the goal. Reports a verdict only. `review-loop` and `way-of-working` say what to do with it. |
| `review-loop` | Review, fix, re-review until clean. Fresh reviewer each round, no push between rounds, three round cap. |
| `technical-writing` | The writing standard for all lasting text. Diátaxis modes, Google developer style, ASD-STE100, Global English. Adapted from pstack (cursor/plugins, MIT). |
| `unslop` | The catalog of AI tells to cut from any text. Loaded in every session from the global `AGENTS.md`. From pstack (cursor/plugins, MIT). |
| `copy-review` | Review comments, commits, PR text, and specs against the glossary and `technical-writing`. A spec repo can ship a skill that binds it to a glossary. |
| `commit-message` | Conventional Commits, why before what, cold reader test. |
| `pr-description` | Short PR text, why and what, no file lists. |
| `why` | The reason behind code, a change, or a review comment: commit bodies via the bundled `git-why` script, then the PR thread, issues, the spec repo, and logs. Reports found, inferred, and unknown apart. |
| `grilling` | Interview the user in numbered rounds with a recommended answer each until the plan has no silent assumptions. Step 1 of `way-of-working`. Adapted from Matt Pocock (MIT). |
| `decision-log` | One TSV row per decision (what, why, evidence, result) for long or unattended runs. Adapted from pstack (MIT). |
| `legible-code` | Rules for code a second reader follows without the author: tests show the calls, no test-only doors, errors are values, names say the effect, no abbreviations. |
| `website-copy-review` | Review the words on a website: conversion path first, then claims, then copy. |
| `layered-graph-layout` | Rules for a readable drawing of a directed graph with many nodes per rank. |
| `implement-issue` | Pick up the next labelled GitHub issue, implement or investigate, open a reviewed PR. |
| `git-rebase` | Interactive rebase through `GIT_SEQUENCE_EDITOR`, no editor. |
| `commit-gate` | A tracked pre-commit hook that blocks a commit when lint, build, or tests fail. One install target, same targets as CI. |

`~/.agents/skills/<name>` is a symlink into this directory for every skill here, so the repo is the source and the live copy at once.

Third party skills that I use but do not copy here:

- `impeccable`: https://github.com/pbakaus/impeccable
- `find-skills`: https://github.com/vercel-labs/skills

## Writing a skill

- Keep the description short and put the trigger phrases in it. The
  agent decides from the description alone.
- State the rule, then the reason. A rule with a story holds better than
  a rule alone. `simplicity-check` and `review-loop` show the pattern.
- Name what the agent must not do. Skills fail most often on an action
  the author assumed nobody would take.
- Keep company names and paths out of skills that other people will
  adopt. A skill that needs them belongs in the company's spec repo, so
  that people who check out the repo can install it from there.
