---
name: decision-log
description: Keeps a TSV log with one row per decision (what, why, evidence, result) during long or unattended work. TRIGGER when the user asks to record decisions or assumptions as you go, for a worker run that spans more than one PR, for autonomous or multi-phase work, and when a reviewer judges the work after stepping away. SKIP for a single small change.
---

# Decision log

Keep one log per piece of work. A reviewer reads it top to bottom, follows
the evidence, and spot-checks. It replaces the questions the reviewer would
otherwise ask in chat.

## Format

One TSV file, one row per decision. Cells stay on one line. Evidence is a
pointer, not prose. Columns:

- **ts.** ISO 8601 timestamp.
- **phase.** The phase or workstream.
- **decision.** What was chosen or done, in one line.
- **why.** The reason in plain words.
- **evidence.** A path or link that proves it: a commit hash, a PR number,
  a `file:line`, or an artifact path. Never a paragraph.
- **result.** The outcome: `tests green`, `reverted`, `open`,
  `INCONCLUSIVE`.

Example rows, for illustration only:

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first, about 100 components	wanted the size before a long run	commit 3a9f1c2	found 5 things to settle first
2026-05-24T11:15:00Z	widget	moved the widget styles without a change to the look	keep the change small and the result identical	commit 7c21e0a, pixel-diff 0	tests pass
2026-05-24T12:30:00Z	widget	discarded a helper's work because its screenshots were blank	checked the real files instead of its summary	worktree reset	reverted
```

## Log a row

Write each row the way you would tell a colleague what you did. Plain
words, concrete actions. The `unslop` rules apply to log text.

Use the helper:

```sh
scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

It stamps `ts`, writes the header on first use, and keeps cells on one line.
A plain `printf` that appends a row works too.

Log decision points and checkpoints, not every action. A row is a fork
chosen, a unit completed with its verification result, a pivot or revert
with its trigger, a blocker surfaced, or an assumption made because the
user was not there to ask. One row per iteration for loop runs. Skip the
trivial.

## Where it lives

The log is a working artifact. Keep it at `decisions.tsv` in the work
directory, or at `.audit/<task>.tsv` when several efforts run at once, and
leave it out of git. Commit it only when the work is large enough that a
reviewer needs the trail to trust the result.

## Rules

- One row is one decision or checkpoint.
- Append only. A wrong call gets a new row that supersedes it. Never edit
  or delete a row.
- Prefer evidence from a committed script over a one-off check, so the
  reviewer can rerun it.

## Before you hand back

Read the log against what you did. Every row maps to a real action. Every
evidence pointer resolves and shows what the row claims. A fork, pivot, or
abandoned approach that shaped the work but has no row is a gap. Add it.
Fix the log, not the story.

End the report with an attention list: the rows where the evidence is weak,
a verification was skipped, or a choice looks risky in hindsight. "No
flags" is a valid list.

## Composing

Other skills name this skill for their audit trail instead of inventing a
format. A worker brief that asks for a decision log names the file path.

Source: adapted from the pstack `show-me-your-work` skill
(github.com/cursor/plugins, MIT).
