---
name: implement-issue
description: Pick up the oldest GitHub issue labeled "ready for implementation" or "needs investigation", research and implement or investigate, then open a reviewed PR or update the issue. Use when asked to work on issues, pick up work, or implement the next task.
---

# Implement Issue

Work through GitHub issues end-to-end. Handles two types of issues:

- **ready for implementation** — research, implement, open a reviewed PR.
- **needs investigation** — research the problem, update the issue with findings,
  and create sub-issues labeled `ready for implementation` if appropriate.

After completing an issue, check for the next one and continue.

## Prerequisites

- `gh` CLI is authenticated.
- The working directory is a git repository with a remote.
- The `commit-message`, `pr-description`, and `review-loop` skills are available.

## Workflow

### 1. Pick the issue

Fetch all open issues labeled `ready for implementation` or `needs investigation`:

```sh
gh issue list --label "ready for implementation" --state open --json number,title,body,labels,createdAt
gh issue list --label "needs investigation" --state open --json number,title,body,labels,createdAt
```

Pick the oldest issue across both lists (by `createdAt`). If no issues match,
tell the user and stop.

Before starting work on an issue, check whether an open PR already addresses it:

```sh
gh pr list --state open --json number,title,body,headRefName
```

Look for PRs that reference the issue number (e.g., `Closes #N`, `Fixes #N`) or
whose title/branch clearly targets the same problem. If a PR already exists,
skip the issue and move to the next oldest one. If all issues are covered by
open PRs, tell the user and stop.

For `needs investigation` issues, follow the **Investigation** workflow below.
For `ready for implementation` issues, continue with step 2.

Read the issue carefully. Present the issue title and number to the user before
continuing.

### 2. Understand the problem

Before writing any code:

- Read the full issue body, comments, and any linked issues or PRs.
- Identify which parts of the codebase are affected. Use search tools to find
  relevant files, types, and tests.
- Understand existing conventions: frameworks, naming, patterns, test structure.
- If the issue is ambiguous or underspecified, ask the user for clarification
  before proceeding. Do not guess intent.

### 3. Plan the approach

Think through the solution:

- What changes are needed and where?
- Are there edge cases the issue doesn't mention?
- What tests need to be added or updated?
- Will this require migration, configuration, or documentation changes?

Do not share the plan unprompted — start implementing. If the approach involves
a significant architectural decision or tradeoff, briefly mention it to the user
before proceeding.

### 4. Implement

Create a new branch from the default branch:

```sh
git checkout -b <type>/<short-description> main
```

Work in focused, logical commits. Use the `commit-message` skill for all commit
messages. Each commit must:

- Be independently correct (tests pass, code compiles).
- Leave the codebase in a good state on its own — if the PR ended at this
  commit, there would be no dead code, unused methods, or dangling scaffolding.
- Contribute something meaningful to the end goal. A commit must not merely
  prepare for a later change by adding methods or types that nothing uses yet.
- Refactoring commits are fine when they make subsequent changes easier to
  understand, but the refactoring itself must stand alone as a coherent
  improvement.

After all changes are complete:

- Run the project's test suite and verify it passes.
- Run lint/typecheck commands if available.
- Ensure full test coverage for new code.

### 5. Open a pull request

Push the branch and create a PR using the `pr-description` skill. Reference the
issue in the PR body with `Closes #<number>` so it auto-closes on merge.

### 6. Review loop

Start the `review-loop` skill against the PR. Fix issues until the review
passes.

### 7. Done

Report the PR URL to the user. Then check for the next issue and continue.

---

## Investigation workflow (needs investigation)

For issues labeled `needs investigation`:

### 1. Research

- Read the issue thoroughly.
- Explore the codebase to understand the problem space.
- Identify root causes, relevant files, and possible solutions.
- Consider edge cases and implications.

### 2. Report findings

Update the issue with a comment containing:

- What you found (root cause, affected code, constraints).
- Proposed solution(s) with tradeoffs if multiple exist.

### 3. Create sub-issues

If the investigation reveals concrete work items, create sub-issues labeled
`ready for implementation`. Each sub-issue should be self-contained and
actionable.

### 4. Close or relabel

- If the investigation is complete and sub-issues created, remove the
  `needs investigation` label from the original issue.
- If the issue needs user input before proceeding, comment with your questions
  and leave it open.

Then check for the next issue and continue.

---

## Guidelines

- **One issue per PR.** Do not bundle unrelated changes.
- **Stay on track.** Only fix what the issue asks for. If you notice unrelated
  problems, note them but do not fix them in this PR.
- **Commit early, commit often.** Logical units of work, not one giant commit.
- **Never skip tests.** If the project has tests, new behavior gets tests.
- **Ask when uncertain.** A question is cheaper than a wrong implementation.
