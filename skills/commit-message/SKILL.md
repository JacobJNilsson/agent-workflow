---
name: commit-message
description: Writes Conventional Commit messages (story-driven, why-focused). TRIGGER any time a commit is about to be created — including when "commit this", "git commit", "ship it", or "commit and push" is the final step of a larger task. Fires per commit when splitting work. SKIP only if the user says they'll write it themselves.
---

# Commit Message

Each commit should tell a story.

## Rules

- Conventional Commits: begin commit with `<type>[optional scope]:`
- Subject: imperative mood; start capitalized; no trailing period.
- Body: why + what (not how); include domain context if needed.
- Tests: only mention when the "why" is about tests.
- Language: write the subject and the body in ASD-STE100 Simplified Technical
  English. Use the active voice. Use short sentences (maximum 20 words). Use
  one word for one meaning. Do not use idioms or unnecessary jargon.

## Audience

Write for a person who did not see the conversation that produced the change,
who works on a different machine, and who reads the log in six months.

Keep a sentence only if that reader can act on it, or verify it from the
repository or from CI. Remove these:

- Facts about one machine or one checkout: a tool version you measured locally,
  a stale `node_modules`, a crash that occurs only on your operating system.
  Keep such a fact only when it is a property of the repository. Then say where
  it comes from.
- Answers to questions the reader never asked. A sentence that exists because
  of a chat message is not automatically useful.
- The history of your work: attempts, corrections, and dead ends.
- Statements that become false after a routine upgrade.

A commit message stays in the history permanently. You cannot correct it later
without a rewrite of the history. Apply this rule before you commit.
