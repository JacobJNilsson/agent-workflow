# Memory

Claude Code keeps a memory directory per project under
`~/.claude/projects/<project>/memory/`. Each memory is one file with one
fact. `MEMORY.md` is an index with one line per memory. The index loads
into every session. A memory file loads when the agent recalls it.

## Format

```markdown
---
name: <short-kebab-case-slug>
description: <one line, used to decide relevance>
metadata:
  type: user | feedback | project | reference
---

<the fact>

**Why:** <the reason>

**How to apply:** <what the agent does differently next time>
```

Types:

- `user`: who the user is and what they prefer.
- `feedback`: a correction or a confirmed approach, with the reason.
- `project`: ongoing work and constraints the code does not show.
- `reference`: a pointer to an external resource.

## What goes in

- A correction I gave, and the reason behind it.
- A convention that a review found more than once.
- Task state that spans sessions, with absolute dates.

## What stays out

- Anything the repo already records. Code structure, git history,
  `AGENTS.md` content.
- Anything that only matters to one conversation.
- Secrets.

## When a memory moves into a skill

A memory is a holding place. When a correction turns out to be a general
rule, it moves into the skill that governs that step and the memory is
deleted. The writing rules, the PR length, the review loop rules, and the
rule that the main loop never writes code all started as memories and now
live in `technical-writing`, `pr-description`, and `way-of-working`. A
rule that is specific to one repo belongs in that repo's `AGENTS.md` or
style guide, not here. This repo keeps no example entries for that
reason: an example that restates a skill goes stale the day the skill
changes.
