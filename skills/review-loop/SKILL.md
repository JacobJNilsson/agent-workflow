---
name: review-loop
description: Orchestrates a review-fix loop. Spawns a review agent, then iterates fix and re-review cycles until the review passes. Works with PRs, local changes, or specific commits. Use when asked to review and fix code, or get changes review-ready.
---

# Review Loop

Review existing changes through a cycle of automated review and fixes until the
changes are clean. You (the main agent) stay as the coordinator throughout --
spawning subagents, handling git, and communicating with the user.

## Prerequisites

- Changes already exist (local changes, a PR, or specific commits).
- `gh` CLI is authenticated (if working with PRs).

## Review target

The user specifies what to review. The `/review` agent supports any of the
following targets -- use whichever the user provides:

- **Local changes** (staged/unstaged diffs -- the default when nothing else is
  specified).
- **A PR** (by number or URL).
- **A specific commit or range** (by SHA or ref).

Carry the chosen target through the entire loop so every `/review` invocation
and every fix subagent prompt refers to the same scope.

## Phase 0: the simplicity check

Before the first correctness review, run the **simplicity-check** skill ONCE on
the whole change. That skill only reports. This section says what the loop
does with its verdict.

Correct code that nobody needs is waste, and a finding fixed in code that
should be deleted is work spent twice. A correctness reviewer asks whether the
code is right. It almost never asks whether the code should exist. Ask that
first.

Act on the verdict before any review round starts:

- **SHIP AS IS**: begin the loop below.
- **SIMPLIFY FIRST**: make the named removals, run the project verification
  command, then begin the loop on the smaller change.
- **QUESTION THE REQUIREMENT**: stop and put it to the user. Do not decide it
  alone, and do not start the loop.

Run this ONCE. Do not repeat it between review rounds: scope is a judgement
about the change as a whole, and re-asking every round invites churn.

Report the verdict to the user, including a SHIP AS IS.

## Review loop

### Iteration

1. **Review**: You MUST use the Task tool to spawn the `/review` agent for
   this step. Do NOT review the code yourself -- the review must come from a
   separate, impartial agent. Each `/review` invocation MUST be a **fresh
   Task** (no `task_id` reuse). Never tell the review agent about previous
   review iterations, previous findings, how many rounds have occurred, or
   what was fixed. The reviewer must judge the code on its own merits every
   time.

   **When the target is a PR**, the PR's remote state will be stale after the
   first iteration because this loop never pushes between iterations. The
   review agent must review the **local** branch, not what GitHub shows.
   Before spawning, gather:
   - PR base branch: `gh pr view <number> --json baseRefName`
   - PR title and body: `gh pr view <number> --json title,body`
   - Local commit list for the PR: `git log <base>..HEAD --oneline`
   - The commit range to review: `<base>..HEAD`

   Then invoke `/review` with the commit range as the target (e.g.,
   `/review main..HEAD`) and include the PR title, body, and commit list in
   the Task prompt as context. Explicitly tell the reviewer that the local
   commits are the source of truth and the GitHub PR is stale -- it should
   not fetch the PR from GitHub.

   For non-PR targets, invoke `/review` with the appropriate target (e.g.,
   `/review`, `/review abc1234`).

2. **Evaluate the verdict**:
   - **Approve** (no issues at any severity): The loop is done. Proceed to
     the wrap-up step.
   - **Approve with nits**: Evaluate each nit. If a nit is valid and
     actionable, continue to the fix step and address it. Only skip nits that
     are subjective style preferences with no clear improvement.
   - **Request changes** (critical or concern items): Continue to the fix step.
   - **Needs discussion**: Stop and present the review to the user. Ask how to
     proceed before continuing.

3. **Fix**: Spawn a fresh **generalPurpose subagent** to address the review
   feedback. Include in its prompt:
   - The full review output (all issues, verbatim).
   - The specific files involved.
   - Relevant project conventions.
   - Instruction to run the project's verification command before returning.
   - Instruction to **NOT commit** -- leave changes unstaged so the
     orchestrator can handle commit strategy.
   - What to report back.

4. **Commit**: After the fix subagent returns, you (the orchestrator) decide
   how to commit. **Never create generic "address review feedback" commits.**
   The git history should read as if the fixes were part of the original work.

   - **Only fixup commits that belong to the current branch.** Never fixup
     into commits on main or any base branch. If the relevant commit is on the
     current branch, use `git commit --fixup=<sha>` followed by
     `git rebase -i --autosquash` to fold it in.
   - Otherwise, create a **new commit** with a proper descriptive message
     following the commit-message skill conventions. Never use generic messages
     like "fix: address review feedback".
   - **Do not push between iterations**, even when working with a PR.
     Intermediate pushes clutter the GitHub history with churn. The push
     happens once at wrap-up.

5. **Next iteration**: Go back to step 1.

### Safety cap

Stop after **3 review iterations**. If the reviewer is still requesting changes
after 3 rounds, present the outstanding issues to the user and ask how to
proceed. Do not continue the loop autonomously beyond this cap.

### When rounds repeat a defect CLASS, question the design

If two consecutive rounds find the same KIND of defect in a new place, stop
patching instances. Make the next round's question the design itself: is the
approach able to hold this property at all?

A round that finds a real bug feels like progress, which is what keeps a branch
on a bad approach. One change took nine rounds. Rounds one to six each found a
hand-written parser missing valid syntax, in a new spelling every time. The
answer was to delete the parser, not to fix a seventh spelling.

## Wrap-up

When the review passes:

1. **If working with a PR, push now.** Use `git push --force-with-lease` if
   the branch was rebased during the loop, otherwise a plain `git push`. Then
   re-read the current PR body (`gh pr view <number> --json body`); if the
   accumulated fixes are significant enough to alter the story, update the PR
   description with `gh pr edit <number> --body "..."`. Keep the same style:
   why and what, not how.
2. Report to the user: the changes are review-clean, summarize what was fixed
   and how many review iterations it took. If working with a PR, include the
   PR URL.
3. If there were only nit-level items in the final review, mention them so the
   user can decide whether to address them.

## Guidelines

- **Never review your own code.** The review step MUST always be delegated to
  the `/review` agent via the Task tool. You are the orchestrator, not the
  reviewer. Self-review defeats the purpose of the loop.
- **Communicate at each phase boundary.** Before spawning subagents, briefly
  tell the user what you are doing ("Spawning review agent...",
  "Starting review loop, iteration 2...").
- **Pass full context to subagents.** They start with a clean context window
  and have no access to your conversation history. Be explicit about
  requirements, conventions, and file paths.
- **Keep the reviewer impartial.** Never leak context about previous iterations
  into the `/review` agent. No mention of prior findings, round numbers, or
  what was changed since last review. Each review must be a clean, unbiased
  assessment.
- **Judgment calls are yours.** Amend vs new commit, whether to update the PR
  description -- these are decisions you make as the orchestrator.
- **Fix valid nits.** If the reviewer raises a nit that is actionable and
  improves the code, fix it. Only ignore nits that are purely subjective style
  preferences with no clear benefit.
- **Check the reviewed language against ASD-STE100.** Tell each spawned
  `/review` agent to check that the prose in the reviewed changes obeys
  ASD-STE100 Simplified Technical English. This applies to documentation,
  comments, user-facing text, commit messages, and the PR description. The
  reviewer must report a violation as a finding, so the fix step corrects it.
  Examples of violations: passive voice, sentences with more than 25 words,
  one word with more than one meaning, idioms, and unnecessary jargon.
- **Check the prose against the cold reader test.** Tell each spawned `/review`
  agent to read the PR description and the commit messages as a person who did
  not see the conversation that produced them. The reviewer must report as a
  finding each statement that this person cannot act on, or cannot verify from
  the repository or from CI. Examples of violations: a tool version measured on
  one machine, an environment problem that belongs to one checkout, an answer
  to a question that nobody asked in the PR, and a report of attempts or
  corrections.
