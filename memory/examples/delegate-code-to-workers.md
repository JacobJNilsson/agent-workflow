---
name: delegate-code-to-workers
description: "Never write code in the main loop, spawn a worker agent for all code changes"
metadata:
  type: feedback
---

Never write or edit code in the main conversation loop. Spawn a worker
agent for all code changes.

**Why:** the main loop runs on the most capable model, whose usage limit
is scarce. Code work burns it fastest. Investigation, review,
orchestration, and conclusions stay in the main loop. Mechanical
production goes to workers.

**How to apply:** investigate and design in the main loop, then hand a
precise brief to an Agent worker with an explicit model override (opus
or sonnet, never the inherited session model, see the subagent model
policy in CLAUDE.md). Small one-line fixes are also worker work.
