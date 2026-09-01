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

- State the core problem or goal.
- If the PR is part of a larger effort, explain where it fits.
- Do not enumerate commits, files changed, or implementation details.
- Only mention code-level details when a non-obvious tradeoff, design decision,
  or dependency quirk needs explanation.

Keep it short. A few sentences is usually enough.

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

Write the title and the description in ASD-STE100 Simplified Technical English.

- Use the active voice.
- Use short sentences: maximum 25 words.
- Use one word for one meaning. Use only approved words where possible.
- Do not use idioms, slang, or unnecessary jargon.
- Keep paragraphs short: maximum 6 sentences.
