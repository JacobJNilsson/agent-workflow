---
name: way-of-working
description: The workflow for tasks that change code, spec first with parallel investigation, implementation agents in worktrees, a simplicity check, a review loop, a copy review of lasting text, then a PR. TRIGGER at the start of any feature, fix, or refactor task, and when asked how we work.
---

# Way of working

Follow these steps for a task that changes code. Skip steps only when the
user says so.

## 1. Spec together

Write the spec with the user, iterating in chat. Draft product behaviour
for the cc-wiki repo. While the spec forms, spawn
investigation agents to map the current state. Always pass an explicit
model override, never run agents on Fable. Feed the findings back into the
spec before it settles.

## 2. Implement in worktrees

When the user calls the spec good, spawn implementation agents in separate
git worktrees branched off origin/main. The agents write the code and
create the commits. Every brief carries the repo's AGENTS.md and style
guide rules, the relevant GLOSSARY.md terms from cc-wiki,
and the repo's test conventions. The harness loads none of that for
subagents.

The spec is not the implementation agent's to change. Every brief states
it: the agent must not edit, create, or remove the spec, a decision
record, or any document the work is judged against. The agent reports a
spec issue with its suggestion, and the managing agent decides and makes
the change, with the user where it moves decided behaviour.

Every brief also carries these commit rules. A mechanical rename goes in
its own commit before the change that needs it: same signatures, callers
follow, no behaviour change, so a reviewer can skip it. A commit that
renames and changes at once cannot be reviewed that way. Every commit
builds and passes lint on its own, because a rebase merge lands each one
on main as it is. Lint cleanup of files the change touches goes in a
separate companion PR that merges first, never inside the change. Code
comments are one sentence, two at most.

Work test-driven as far as the work allows. Write the test from the spec,
watch it fail, then write the code that makes it pass. A test written
after the code tends to pin what the code does, not what the spec
demands. Where test-first does not fit, the test still derives from the
spec's words, never from the implementation's behaviour. For every bug
fix, the regression test comes first and must fail against the unfixed
code. Prove a doubtful test is load-bearing by reverting the change and
watching it fail.

## 3. Simplicity check, then review loop

Run the simplicity check once on the whole change. It reports whether the
change should exist and whether less code reaches the goal. Act on its
verdict: simplify first, or take a questioned requirement back to the user.

Then spawn a review loop on the commits and iterate fix and re-review until
the review passes.

A review sometimes shows that the spec itself needs an adjustment. The
implementation agent raises that concern, with its suggestion, to the
managing agent. The managing agent makes the spec change — with the user
when it moves decided behaviour — and the implementation continues against
the updated spec. A reviewer judges the implementation against the spec as
it stands, and flags an implementation that quietly amended it.

## 4. Copy review

Spawn a copy review on longer code comments and on the PR description
before anything is published. The reviewer checks glossary terms, one word
for one meaning, clear referents, short active sentences, and that a
reader without the conversation understands the text.

## 5. Open the PR

Create the PR as a draft unless the user says otherwise. The description
states the problem and what the change does, in about 1000 characters. Do
not add a decisions-for-review section. A decision lives in a code comment
or a commit message. A genuinely open question goes to the reviewer as a
comment, or to the user in chat, not into the description.

The user edits PR descriptions by hand. Before you rewrite one, fetch the
current body and keep every difference from your last version. Those
differences are the user's deliberate edits.

## 6. Review feedback

Land review fixes as fixup commits so the reviewer sees the increments. Do
not rewrite history while a review is in progress. The moment the review
is approved, rebase onto main, autosquash, verify the tree, and force
push. Do not wait for a go. A merged fixup commit lands on main as it is,
and main is never rewritten.
