# Description examples

These examples come from the skills in this repo. Each one shows a rule from `SKILL.md`. The rewrites are suggestions, and this task did not change the other skills.

## A description that works: `why`

> Finds the reason behind code, a change, a review comment, or a number, from commit bodies, PR threads, issues, and logs. TRIGGER when asked why something is the way it is or why a colleague chose or wrote something, before you change or delete a line whose purpose is unclear, when a comment and the code disagree, before you run git blame or git log, and when a guard, flag, threshold, or test looks arbitrary. SKIP when the question is only who or when.

- One phrase says what the skill does.
- The triggers name requests ("asked why"), moments ("before you change or delete a line"), and signals ("a comment and the code disagree").
- The skip line separates "why" from the near miss "who or when".

## A description that works: `grilling`

> Interviews the user in rounds until a plan, design, or spec has no silent assumptions. TRIGGER at the spec step of a task, when the user says grill me, stress-test this, poke holes, or asks whether a plan is complete, and before a spec is called good. SKIP when the user gives a fully specified task.

- It quotes the phrases a user types: "grill me", "stress-test this", "poke holes".
- It names a place in the workflow, "the spec step of a task".

## A description that works: `code-shape`

> Use when a spec is settled and before the first implementation brief, when a fix or a feature needs new functions or packages, and when the user asks which functions, packages, or tests a change needs.

- It has no summary, only triggers. That is enough when the name already says the purpose.

## A description that fails: `unslop`

> Cut AI tells from any writing. Must always apply.

- It is an order and not a condition. The agent cannot tell when "any writing" starts.
- "Must always apply" does not tell the model what to look for. A skill that loads on every turn is a rule, and a rule belongs in `AGENTS.md`.
- The checker reports it: `description does not say when to use the skill`.
- A rewrite: `Removes AI tells from prose. Use when writing or editing text that a person will read, and before you hand back docs, comments, commit messages, or PR text.`

## A description that fails: `way-of-working`

> Coordinate code changes through a spec, a code sketch, implementation worktrees, a review loop, the author's final unslop pass, and a PR. Use at the start of a feature, fix, or refactor, and when asked how we work.

- The trigger is good. The first sentence lists the steps of the workflow.
- An agent that reads the step list may follow it from memory and skip the body. Superpowers reports this failure for a description that summarized a review step.
- A rewrite: `Coordinates a code change from request to merged PR. Use at the start of a feature, fix, or refactor, and when asked how we work.`

## A description that is half done: `git-rebase`

> Perform interactive git rebases without opening an editor. Use when asked to squash, fixup, reorder, drop, or edit commits.

- It has triggers, and the checker passes it.
- It has no skip line. A request to rebase onto main without any history edit also matches "rebase". Add `SKIP for a plain rebase or merge.` if you see a wrong load.

## Patterns to copy

| Pattern | Example |
| --- | --- |
| Name the words a user types | `when the user says grill me, stress-test this, poke holes` |
| Name a moment in the work | `before you run git blame or git log` |
| Name a signal in the code | `when a guard, flag, threshold, or test looks arbitrary` |
| Name the near miss to skip | `SKIP when the question is only who or when` |
| Keep the purpose to one phrase | `Finds the reason behind code, a change, or a number` |

## Patterns to avoid

| Pattern | Why |
| --- | --- |
| A list of the skill's steps | The agent follows the list and skips the body. |
| "Helps with", "handles", "processes data" | It matches everything and tells nothing. |
| "I can" and "you can" | The text goes into the system prompt, so first and second person confuses the speaker. |
| `<` and `>` characters | The platform rejects them as XML tags. |
| A name of a company, product, or path | Another team cannot adopt the skill. |
