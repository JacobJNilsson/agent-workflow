---
name: review-pr
description: Review a GitHub PR and post findings as pending inline review comments, usually phrased as questions. Use when asked to review a PR, or to post review findings on a PR.
---

# Review a PR and stage inline comments

## Workflow

1. Run the `review-code` skill with the PR URL or number as the argument. Wait for the verified findings.
2. Summarize the findings to the user. Lead with data-loss and correctness bugs. Put cleanups last.
3. Draft one comment per finding. Follow the comment style below. Show the drafts as described under presenting drafts, and wait for the user's word before you post.
4. Post the comments as one pending review. Follow the posting steps below.
5. Tell the user the review is pending and that they submit it from the GitHub Files tab.

## Comment style

- Default to one or two short sentences. Include only the evidence the author needs to assess the suggestion. Add detail when the consequence needs explanation.
- Phrase changes as suggestions that leave room for context you may have missed. Prefer "Would it make sense to...?" or "Could we...?" over directives.
- Describe what you observed. Do not claim a reproduction you did not run.
- Name the affected functions or values. Shortening a comment must preserve the context the author needs without reading our conversation.
- Keep a comment at each affected location. Explain a repeated issue once, then reference the first comment by symbol. Name the functions at the later location without repeating the explanation or solution. Keep unrelated findings separate.
- Follow the `technical-writing` and `unslop` skills. Use active voice and at most 25 words per sentence. No em-dashes, semicolons, lists, bold, or "Label: text" constructions in comments.
- Mark cleanups as optional, for example "A follow-up is fine if you agree."
- Start a pure style finding with "nit:" as its own sentence.

## Presenting drafts

For each finding show the code snippet first, then a short explanation when
the snippet does not speak for itself, then the proposed comment, then a
separator. Merge comments that target the same code block into one range
comment.

Before you delete a pending review to re-stage it, read the live comment
bodies first. The user hand-edits drafts on GitHub, and a re-stage from
your last version loses those edits.

## Posting a pending review

GitHub only accepts inline comments on lines inside diff hunks.

1. Download the diff: `gh pr diff <n> --repo <owner>/<repo> > pr.diff`.
2. Map each finding to a new-file line inside a hunk. Compute line numbers from the `@@ -a,b +c,d @@` headers.
3. When a finding sits outside every hunk, anchor it to the nearest related changed line. Name the real line in the comment body.
4. Get the head commit: `gh pr view <n> --json headRefOid`.
5. Write a JSON payload with `commit_id` and a `comments` array. Each comment has `path`, `side: "RIGHT"`, `line`, an optional `start_line` for ranges, and `body`.
6. Post it with no `event` field so the review stays PENDING (staged, invisible to the author):
   `gh api repos/<owner>/<repo>/pulls/<n>/reviews --input review.json`
7. Verify: `gh api repos/<owner>/<repo>/pulls/<n>/reviews/<id>/comments --jq length` must equal the comment count.

Only one pending review can exist per user per PR. Do not pass `event` in the payload. The user submits the review from the GitHub UI.
