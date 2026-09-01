---
name: keep-pr-descriptions-short
description: "PR descriptions stay short, roughly 1000 characters, not the 2000-character essays that agents produce by default"
metadata:
  type: feedback
---

Keep PR descriptions to about 1000 characters.

Keep only these parts:

- The merge-order or deploy warning, when one applies.
- A short why, two or three sentences.

No decisions section of any kind. The contributor makes the decisions and
presents a decision to the reviewer in person when it is non-obvious.

Cut the narrative restatement of the problem, the file-by-file list, and
the retelling of what earlier PRs did.

**Why:** the reviewer reads the diff. The description exists for what the
diff cannot show, which is intent. The PR body speaks with the
contributor's voice, so never attribute a decision to a person by name or
date, and never justify decisions there.

**How to apply:** write the description, then delete every sentence that
the diff already proves. Skip warnings that restate the obvious. The user edits
descriptions by hand, so before rewriting a body, fetch the current one
and treat differences from the last agent version as deliberate edits,
never as loss to restore. See [[no-emdash-no-semicolon]] for the style
rules that apply to the same text.
