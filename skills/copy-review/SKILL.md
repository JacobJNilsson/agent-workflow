---
name: copy-review
description: Reviews the lasting prose in a change - code comments, commit messages, PR descriptions, and spec text - against the writing rules and the product glossary. TRIGGER when the user asks to copy-review, prose-review, or check the wording of comments, commits, PR bodies, or specs. SKIP for website or marketing copy.
---

# Copy review

Review the words that outlive the conversation: code comments, commit
messages, PR descriptions, and spec text. Report findings with concrete
rewrites. Do not change files until the user approves the findings, unless
the user asked for a review-and-fix pass.

## The glossary is the vocabulary

If the workspace has a spec repo, its glossary holds the product's terms.
The workspace instructions name the repo. A project skill may bind this
review to a specific glossary and to extra term lists. Read the glossary
before reviewing.

Every term in the reviewed text must match the glossary. One word has one
meaning. A second name for a glossary term is a finding. A new term that
the glossary lacks is a finding too: the fix is to add the term to the
glossary, not to define it inline.

Test each sentence that uses a glossary term: replace the term with its
definition and read the sentence again. If it stops making sense, the
sentence misuses the concept, and that is a finding.

Without a glossary, hold the text to its own vocabulary. Two names for one
thing is still a finding.

## Language rules

All lasting text follows ASD-STE100 Simplified Technical English:

- Active voice.
- Max 25 words per sentence. Count, do not guess.
- One word for one meaning.
- No idioms. No unnecessary jargon. Plain words.
- No em-dashes. Use a comma, a full stop, or brackets.
- No semicolons in prose. Code semicolons are fine.

## Per text kind

**Code comments.** A comment states a constraint the code cannot show. Flag
a comment that narrates what the next line does, and a comment whose claim
the code contradicts. Comments are short: one sentence is the norm, two is
the limit, and a longer comment is a finding unless it carries a fact the
reader cannot get elsewhere. Flag a comment that restates a fact another
comment or the type already states, or that says the same thing twice in
different words. Propose the shortest text that keeps the load-bearing fact.
An LLM writes comments that are too long and too complete. Cut, do not
polish.

**Commit messages.** Story-driven, why before what. Apply the cold reader
test: every claim must be actionable or verifiable from the repo or CI.
No history of attempts. No facts about one machine. The subject states the
outcome and must not over-promise the commit's content.

**PR descriptions.** Short, roughly 1000 characters. A deploy or merge-order
warning when one applies, then a short why. No decisions section, no
justification of decisions, no attribution of decisions to a person. The
body speaks with the contributor's own voice.

**Spec text.** Follows the spec repo's own writing rules. Present tense,
behaviour stated as fact, open questions marked open. Terms come from the
glossary.

## Report shape

Group findings as: worth fixing, borderline with a stated lean, checked and
clean. Each finding names the file and line (or the PR or commit), states
the problem in one sentence, and proposes the rewrite. End with a verdict
per scope area: clean, or needs a fix pass.
