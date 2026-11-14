---
name: make-rule
description: Use when the user corrects how an agent worked or what it produced, when the same review comment comes back a second time, and when asked to turn a lesson into a lint rule, a type, a test, or a check.
---

# Make a rule

A correction in the chat helps once. An agent in the next session makes
the same mistake, because it copies the nearest pattern in the code. A
check in the code stops the mistake for every agent that comes after.

Turn each correction into the hardest check that can catch it. A line in a
skill or in `AGENTS.md` is the last resort, because agents forget prose.

## Fix first

Fix the mistake the user pointed at before you write the rule. The user
asked for the fix. The rule comes after it.

## Name the pattern

Write one sentence that names the pattern in code, not the single case.
"The handler logs and then returns the error" is a case. "A function logs
an error that it also returns" is a pattern that a check can find.

If the mistake was in how you worked, not in the code, name the step that
went wrong. "Pushed to `main`" is a pattern. A hook can block it.

## Pick the hardest layer

Go down the list and stop at the first layer that can catch the pattern.

1. **Structure.** Change the API, the types, or the folder layout so the
   wrong code cannot be written. A function that takes a parsed value
   cannot get an unparsed one.
2. **Lint rule.** A linter fails on the pattern. Use this layer for most
   rules.
3. **Test.** A test fails when the behaviour breaks. Use it for a rule
   about behaviour that no linter can see.
4. **Gate script or hook.** A script in the commit gate or CI checks the
   repo, or a Claude Code hook checks what the agent does. Use it for
   rules about files, commits, and agent actions.
5. **Prose.** A line in a skill or in the repo's `AGENTS.md`. Use it only
   when the rule needs judgment that no machine has. Say in the report
   that the rule is prose and why.

## Pick the home

Put a general rule where every repo in that language gets it. Put a rule
that only one repo needs in that repo.

| The rule is about | Home |
| --- | --- |
| Go code in any repo | `JacobJNilsson/anti-slop-go`, a new analyzer |
| TypeScript in any repo | The anti-slop Oxlint plugin, `tools/oxlint/anti-slop` |
| One repo's code | That repo's lint config or a script in its gate |
| What agents do | A Claude Code hook in `~/.claude/hooks` |

A repo gets a new anti-slop-go rule only after it moves to the new
version. Say in the report which repos still need the upgrade.

## Write the check

1. Write the error message first. Name the right fix, not only the wrong
   code. "Return the error and let the caller log it" tells the agent what
   to do. "Do not log errors" does not.
2. Add a test with one case that fails the check and one that passes.
3. Run the check on the whole repo. Fix the old cases in the same PR when
   there are few. When there are many, keep a list of the files that still
   fail and let the list only shrink. Never add a silent exception.
4. Make sure the check runs in the commit gate and in CI, not only by
   hand. A check that nobody runs is prose.
5. Open the rule as its own PR, apart from the feature work. An exception
   to a rule also gets its own PR, because it changes the rules.

## When the check must wait

Some rules take more time than the task allows. Then add a row to
`~/.agents/rule-candidates.tsv` and tell the user. Create the file with
this header if it does not exist:

```
date	repo	pattern	layer	home	state
```

Fill in the date, the repo, the pattern sentence, the layer, the home, and
`todo` as the state. Set the state to `done` with the PR number when the
check lands, or `dropped` with a reason.

## Report

Tell the user in a few lines:

- the pattern, in one sentence,
- the layer and the home you picked,
- where the check runs: commit gate, CI, or a hook,
- the PR, or the row you added to the candidates file.
