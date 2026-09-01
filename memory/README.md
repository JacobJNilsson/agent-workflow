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

## Examples

The files in `examples/` are real entries. `delegate-code-to-workers`
and `worker-briefs-carry-repo-guidance` record the two corrections that
shaped the workflow most. The rest show smaller rules: writing style,
PR length, and git conventions.
