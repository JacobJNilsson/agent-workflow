---
name: lighter-code
description: After a change passes review, find the existing code that the change made unnecessary, prove it, and remove it in its own commit. TRIGGER as the last step of review-loop when the loop passes, and when asked what a change made removable, dead, or lighter.
---

# Lighter code

A change often leaves code behind that has no job any more. Examples are a function whose last caller the change replaced, a flag that is now always true, a fallback for a case that can no longer occur, and a test that pins removed behaviour. Nothing fails, so neither the tests nor a reviewer notice. The code stays, and every later reader pays for it.

The `simplicity-check` skill asks whether the change itself is bigger than it needs to be. This pass asks a different question: what did the change make unnecessary in the code around it?

In one change, a new plan diff replaced a module that matched plan rules by a structural identity. The tests passed, and two reviewers passed the change. This pass found that the module had lost its last caller. It removed six functions and their tests in a separate commit, and a reviewer confirmed the proof.

## When to run it

Run it once, after the review loop passes and before the author's final `unslop` pass. The code is final at that point, so the pass judges what will merge.

## Who runs it

The agent that wrote the change runs it while its context is still loaded, because it knows what it replaced. When that agent is gone, give a fresh worker the diff, the requirement, and this skill. The pass edits code, so a coordinator that does not write code hands it to a worker.

## What to examine

Examine the code the change touched and the code next to it: callers, callees, tests, flags, configuration, state fields, documentation, and agent instruction text. Ask these questions:

1. Does a function, type, or file lose its last caller?
2. Does a flag, option, or parameter now always carry the same value?
3. Does a branch, fallback, or guard handle a case that the change made impossible?
4. Do two paths now do the same thing?
5. Does a test pin behaviour that the change removed?
6. Does a document or comment describe behaviour the code no longer has?

## Rules

- Prove each claim before you act on it. Find every caller across the repository, including other build tags, generated code, and scripts. Show that the case can no longer occur.
- Remove only what this change made unnecessary. Code that was already removable before the change is not part of this change. List it in the report instead, so the pull request stays about one thing.
- Put each removal in its own commit, after the feature commits. The commit body names the change that made the code unnecessary.
- Change no behaviour. If a removal changes what a user or a test sees, the code was not unnecessary.
- Report a pass that finds nothing as a valid result. Name each candidate you checked and the reason it stays. Do not invent a removal to look useful.

## After the pass

- If the pass removed nothing, continue to the author's `unslop` pass.
- If the pass removed code, one fresh reviewer reviews the removal commits alone, as a review-loop round does. A finding goes through triage like any other. Do not run the pass again.

## Report

Return four lists, and the coordinator relays them to the user:

- **Removed**: the commit, what it removed, and the proof.
- **Simplified**: the commit, what it simplified, and the proof that behaviour is unchanged.
- **Listed for later**: code that was removable before this change, and where it is.
- **Checked and kept**: each candidate that stays, and why.
