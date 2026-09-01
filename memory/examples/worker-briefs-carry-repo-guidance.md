---
name: worker-briefs-carry-repo-guidance
description: "Every code worker and review brief must carry the target repo's AGENTS.md and STYLEGUIDE.md rules"
metadata:
  type: feedback
---

Repo conventions never reach spawned workers by themselves. The harness
loads CLAUDE.md for the main session, not AGENTS.md, and loads nothing
for a subagent. A repo's AGENTS.md and STYLEGUIDE.md stay invisible to
workers unless the brief carries them.

**Why:** guidance that is not in the agent's context does not exist.
Reviewers then find the violations at ten times the cost.

**How to apply:** before spawning a code or review worker for a repo,
read that repo's AGENTS.md and the files it references. Put "read
<repo>/AGENTS.md and every file it references before writing" in every
brief, and paste the directly relevant sections (for tests, the
STYLEGUIDE.md Tests rules) verbatim. Review briefs use the style guide as
the rubric and cite rule names in findings. Every worker gets its own
fresh worktree from origin/main, removed after its branch is pushed.
Luigi test placement: tests for package foo go in foo/footest as package
footest, never next to the source file. Tests of unexported symbols are
the flagged exception. Repo CLAUDE.md files include AGENTS.md, and the
workspace root CLAUDE.md points agents at each repo's AGENTS.md. See
[[delegate-code-to-workers]].
