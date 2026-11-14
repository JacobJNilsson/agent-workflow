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
- The `way-of-working` skill and the skills it uses are available.

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

### 2. Work the issue through way-of-working

Follow the `way-of-working` skill from step 1 to the draft PR. The issue is
the input to the spec. Read the issue body, its comments, and every linked
issue or PR before the spec step.

The `ready for implementation` label counts as an approved spec. Ask the user
only when the issue is ambiguous or leaves a product decision open. Do not
guess what the issue means. A large code sketch still waits for the user's
approval, as the `code-shape` skill says.

The PR body references the issue with `Closes #<number>`, so the merge closes
the issue.

### 3. Done

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
- **Ask when uncertain.** A question is cheaper than a wrong implementation.
