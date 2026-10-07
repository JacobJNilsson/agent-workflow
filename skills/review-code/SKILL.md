---
name: review-code
description: Reviews code or a diff against the task, the repo rules, and the tests, then reports findings by severity with a verdict. Use for a local change, a commit range, or a PR, when asked to review, check, or look over code.
---

# Review code

You review code against three things: the task it claims to satisfy, the
repo's own rules, and the tests that cover it. You report what you find. You do
not fix it.

## Read before you judge

1. The repo rules: `AGENTS.md`, `STYLEGUIDE.md`, and anything they point to. A
   finding that contradicts a repo rule is real. A finding that ignores one is
   noise.
2. The task or spec the change claims to satisfy.
3. The diff. For a PR, review the local branch. What GitHub shows is stale once
   anyone pushes.
4. The tests over the changed code. Run them if you can.

## What counts as a finding

Report only problems this change caused, or made reachable. Each finding needs
proof from the code: the file and line, a failing test or a reproduction, or a
contradiction with a stated contract.

Drop anything you cannot support:

- A style preference the repo does not rule on.
- A risk in code this change did not touch.
- A restatement of what a linter or type checker can tell you.

Whether the code should exist at all is a separate question. The simplicity check
owns it. Judge whether the code is right.

## Severity

| Level | Meaning |
| --- | --- |
| `critical` | Wrong behaviour, data loss, a security hole, or a broken contract. |
| `concern` | A real defect, or a missing test on a path this change introduced. |
| `nit` | Small and optional. Say what improves and why. |

## Verdict

End with one line:

- `Request changes` when a critical or concern item stands.
- `Approve with nits` when only nits stand.
- `Approve` when nothing stands.
- `Needs discussion` when the finding is a product or scope decision for the
  engineer, not a defect to fix.

## Reporting

Group findings by severity, most severe first. For each one give the file and
line, what is wrong, the proof, and the smallest fix you would accept.

Leave prose alone. Do not grade comments, commit messages, or docs wording.
Flag a comment or a doc only when it states something false about the code.

Say what you did not check, and why. A review that skipped the database layer is
not a clean review of the database layer.

## Related skills

- `review-pr` runs this skill against a GitHub PR and stages the findings as a
  pending review.
- `review-loop` runs this skill repeatedly with fixes in between. The loop owns
  the mechanics. This skill owns the judgement.
