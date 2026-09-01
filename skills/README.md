# Skills

A skill is a `SKILL.md` file with a name, a description, and a procedure.
The description holds the trigger phrases. Claude Code loads the skill
when a prompt matches, or when I type `/<name>`.

| Skill | Purpose |
| --- | --- |
| `way-of-working` | The end to end workflow for a code change. Spec, worktrees, review loop, copy review, PR. |
| `simplicity-check` | One fresh agent judges whether the change should exist and whether less code reaches the goal. Reports a verdict only. `review-loop` and `way-of-working` say what to do with it. |
| `review-loop` | Review, fix, re-review until clean. Fresh reviewer each round, no push between rounds, three round cap. |
| `cc-copy-review` | Review comments, commits, PR text, and specs against the glossary and the writing rules. |
| `commit-message` | Conventional Commits, why before what, cold reader test. |
| `pr-description` | Short PR text, why and what, no file lists. |
| `git-why` | Read the commit reasoning behind a line instead of a blame table. |
| `git-rebase` | Interactive rebase through `GIT_SEQUENCE_EDITOR`, no editor. |

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
- Keep company paths out of skills that other people will adopt.
  `cc-copy-review` is CarbonCloud specific by design.
