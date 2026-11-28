---
name: pr-description
description: Writes PR titles and descriptions focused on why a change exists. TRIGGER any time a PR is about to be created or updated — including when "open a PR", "gh pr create", "send for review", or similar is the final step of a larger task. SKIP only if the user says they'll write it themselves.
---

# PR Description

## Title

- Imperative mood, start capitalized, no trailing period.
- Describe the outcome, not the code. No conventional-commit prefixes.

## Description

Focus on **why** this change exists and **what** it accomplishes at a product or
system level.

- Open with a merge-order or deploy warning when one applies. Skip a warning
  that restates the obvious.
- Lead with the problem, stated so a reader who does not know the code can
  weigh the change against it. Then the mechanism. "X now does Y" with the
  reason in a subordinate clause is not a why.
- If the PR is part of a larger effort, say where it fits.
- Do not enumerate commits, files changed, or implementation details.
- Mention code-level details only for a non-obvious tradeoff or dependency
  quirk.
- No decisions section, no justification of decisions, no attribution of a
  decision to a person. The body speaks with the contributor's own voice.

Keep it to about 1000 characters. Write it, then delete every sentence the
diff already proves.

The user edits descriptions by hand. Before you rewrite a body, fetch the
current one and keep every difference from your last version. Those
differences are deliberate edits.

## Picture of the change

Add a small picture when the shape of the change is hard to see in prose. Pick the smallest view that makes the point:

- Pseudocode for logic or an algorithm.
- A call tree for runtime control flow.
- A shallow file tree for a change in which file owns what.
- A diff sketch of one of these when the point is what changes in a shape that already exists.

Keep only the calls, files, and states the reader needs to see the point. Put the picture next to the sentence it supports. A picture shows the shape of the change. It is not a list of changed files.

Leave the picture out when a sentence already makes the point. A one-line change, a renamed symbol, or a bumped version needs none.

A call-tree sketch for a change that sends a rollout's progress to the UI:

```diff
 startRollout
   runBatch
+    reportProgress
   finishRollout
```

## Risk

End the body with a short risk assessment. It answers two questions.

Is the change a one-way door or a two-way door? A revert walks back a two-way door. A revert cannot walk back a one-way door. Examples are a dropped column, a deleted file in a bucket, a message sent to users, or a public API that clients already call. Name what a revert cannot undo.

What is the blast radius? Name what else the change can break when it goes wrong. Examples are callers of a changed function, consumers of a changed API, other services that read the same table, or the layout of other pages.

Keep it to one or two sentences each. "Two-way door: a revert restores the old retry loop. Blast radius: every job that calls the shared HTTP client."

## Audience

Write for a reviewer who did not see the conversation that produced the change,
who works on a different machine, and who reads this in six months.

Keep a sentence only if that reader can act on it, or verify it from the
repository or from CI. Remove these:

- Facts about one machine or one checkout: a tool version you measured locally,
  a stale `node_modules`, a crash that occurs only on your operating system.
  Keep such a fact only when it is a property of the repository. Then say where
  it comes from.
- Answers to questions the reader never asked. A paragraph that exists because
  of a chat message is not automatically useful to a reviewer.
- The history of your work: attempts, corrections, and dead ends.
- Statements that become false after a routine upgrade.

Keep a finding when it changes the decision to merge. Write it as a property of
the repository, and give the reader a way to reproduce it.

## Language

Follow the `technical-writing` and `unslop` skills. Active voice, one
thought per sentence, plain words, one word for one meaning. Keep paragraphs
short: maximum 6 sentences.

Write the body as you would brief the reviewer in person. "An operator needs
to see when the batches of a rollout are done" becomes "While a rollout runs,
someone needs to see how far it has come and which batches failed."

Source: the picture of the change and the risk assessment adapt the `pr` skill by Matt Pocock (https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md, MIT).
