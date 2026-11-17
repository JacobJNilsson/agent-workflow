# Skill scripts audit

This audit lists, for every skill under `skills/`, the steps an agent does by hand that a script could do. A script is faster, it gives the same answer every time, and a test proves it. The idea comes from Kent C. Dodds' talk "What I Changed to Beat a Million-Install AI Skill". Nobody here has watched the talk, so the audit works from the idea alone.

## How to read it

- **By hand** is a step the skill text asks the agent to do with its own reading and counting.
- **Script** is what a bundled tool would do. The tool lives in the skill folder, has its own tests, and `SKILL.md` tells the agent to run it.
- **Value** is a rough rank. High means the agent does the step in most runs, and a wrong answer costs a rework or a rejected PR. Medium means the step is common but a slip is cheap. Low means the step is rare or needs judgement that a script cannot hold.
- **Replaces a judgement** marks a place where the skill asks the agent to decide something that a program can decide with a rule.

Two skills already ship code. `decision-log` has `scripts/log.sh`. `why` has `git-why`. Both are plain POSIX sh or bash with no installs. New scripts use the Python 3.12 standard library or POSIX sh, so they run on Linux and on the Mac.

## Summary

| Skill | Best candidate script | Value |
| --- | --- | --- |
| `unslop` | `prose_check.py`: dashes, semicolons, long sentences, banned words | High, piloted |
| `commit-message` | `check_commit.py`: Conventional Commit subject and body rules | High, piloted |
| `technical-writing` | Extend `prose_check.py` with the style rules below | High |
| `copy-review` | Run `prose_check.py` on the added lines of a diff, plus a glossary check | High |
| `pr-description` | `check_pr.py`: title and body rules, length, paragraph size | High |
| `review-pr` | `build_review.py`: map findings to diff hunks, write `review.json` | High |
| `review-code` | `added_symbols.py`: new symbols and their callers | High |
| `implement-issue` | `next_issue.sh`: pick the oldest open issue that has no PR | High |
| `website-copy-review` | `page_facts.py`: titles, meta tags, links, status codes | High |
| `layered-graph-layout` | `layout.py`: rank, order, and place nodes by the rules | High, large effort |
| `commit-gate` | `install.sh` plus the hook template as a file | Medium |
| `git-rebase` | `rebase_todo.sh`: build the todo from `action:sha` pairs | Medium |
| `decision-log` | `verify.sh`: check that each evidence pointer resolves | Medium |
| `review-loop` | `context.sh` and a round ledger with the cap | Medium |
| `way-of-working` | `worktree_new.sh`: branch name check and worktree off `origin/main` | Medium |
| `why` | `pr_for_commit.sh` and a reformat-commit detector | Medium |
| `code-comments` | `comment_lint.py` on the comments a diff adds | Medium |
| `legible-code` | `test_shape.sh`: long tests, test-only exports, short names | Medium |
| `code-shape` | A sketch validator | Low |
| `grilling` | None worth building | Low |

## Per skill

### code-comments

- **By hand.** Find each comment that a diff adds. Count its sentences. Spot comments that narrate the next line or use "of" chains.
- **Script.** `comment_lint.py` reads `git diff -U0` and extracts added comment lines for Go, Python, shell, and TypeScript. It prints comments with more than two sentences, sentences over 25 words, and words from the `unslop` list.
- **Replaces a judgement.** "One sentence is the norm, two is the limit" becomes a count. "Does it answer why" stays a judgement.
- **Value.** Medium. The agent writes comments in nearly every change, but the count rule covers only part of the skill.

### code-shape

- **By hand.** Write the sketch with `+`, `~`, and `=` marks. Check that every new function has a package and a test, and that the implementation matches the exported signatures.
- **Script.** A validator that reads the sketch file and flags a function without a mark, a package, or a test. A second mode compares exported symbols in the sketch with the code.
- **Value.** Low. The sketch format is free text. A parser would force a format, which is a design decision for the operator.

### commit-gate

- **By hand.** Read the CI workflow. Copy the hook template out of `SKILL.md`. Adapt the staged-file test for each language. Write the `make setup` target.
- **Script.** Ship the hook template as `references/pre-commit` and add `scripts/install.sh`. The installer detects Go or Node from the repo files, writes `.githooks/pre-commit`, and sets `core.hooksPath`.
- **Replaces a judgement.** "No staged file can affect the suite" becomes a path pattern per language, stored in the script.
- **Value.** Medium. The step runs once per repo, but the inline template is 40 lines that the agent retypes and can mistype.

### commit-message

- **By hand.** Check the type prefix, the capital letter, the trailing period, and the length of the subject. Count words per sentence in the body. Make sure no attribution line is present.
- **Script.** `scripts/check_commit.py` does all of this and exits with 1 on a finding.
- **Replaces a judgement.** The whole format list. The why and the audience test stay judgement.
- **Value.** High. Every commit passes through the skill. See `evals/results/commit-message.md`.

### copy-review

- **By hand.** "Count words per sentence. Do not guess." "Grep for the words that compete for one meaning and count them." Look for em dashes and semicolons.
- **Script.** Run `prose_check.py` from `unslop` on the added lines of the diff. A second script reads the glossary and prints each term that a text uses under two names, with counts.
- **Replaces a judgement.** Sentence length, dash rules, and the count of competing words.
- **Value.** High. The skill already says to count, and a model counts words badly. The eval for `unslop` shows this.

### decision-log

- **By hand.** Before handing back, check that "every evidence pointer resolves and shows what the row claims". The agent opens each pointer by hand.
- **Script.** `scripts/verify.sh <logfile>` checks six columns per row, then tests each evidence cell. A commit hash must exist in `git`, a path must exist, and `file:line` must have that line.
- **Replaces a judgement.** "Does the pointer resolve" becomes a yes or no. "Does it show what the row claims" stays a judgement.
- **Value.** Medium. The skill is for long runs, so it fires less often.

### git-rebase

- **By hand.** List the commits, write the todo by hand, and quote it correctly inside `GIT_SEQUENCE_EDITOR`. A wrong quote hangs the rebase on an editor.
- **Script.** `scripts/rebase_todo.sh <base> fixup:abc123 drop:def456` builds the todo from the real log, keeps unnamed commits as `pick`, writes it to a temp file, and runs the rebase. It refuses a SHA that is not in the range.
- **Value.** Medium. The skill text itself contains a "won't work" line, which shows the quoting is error-prone.

### grilling

- **By hand.** Number the rounds and keep a list of open decisions.
- **Script.** None worth building. A tracker adds ceremony to a conversation.
- **Value.** Low.

### implement-issue

- **By hand.** Run `gh issue list` for two labels, merge the lists, sort by date, and pick the oldest. Then run `gh pr list` and look for a PR that already covers the issue.
- **Script.** `scripts/next_issue.sh` runs both listings and removes issues that an open PR closes or names. It prints the oldest issue as JSON with its number, title, body, and label.
- **Replaces a judgement.** "Oldest, and not yet in a PR" becomes a rule. The model reads PR bodies for "Closes #12" today.
- **Value.** High. The step opens every run, and a wrong pick wastes the whole run. The eval needs GitHub, so it is not part of this round.

### layered-graph-layout

- **By hand.** Rules 9 to 15 describe an algorithm: build column N from column N-1, order siblings, compute heights. The agent applies it by reading the rules.
- **Script.** `scripts/layout.py` reads an edge list and prints ELK JSON with the ports and the order already set. A check mode confirms that no edge is lost and that the output is deterministic.
- **Replaces a judgement.** "Sibling order" and "a node is as high as it can be".
- **Value.** High, but it is the largest build in this list. The rules are precise enough to test.

### legible-code

- **By hand.** Find tests that run long, find `export_test.go` files and other test-only doors, and find names with abbreviations.
- **Script.** `scripts/test_shape.sh` lists test functions over a line limit, files named `export_test.go`, and identifiers from an abbreviation list.
- **Replaces a judgement.** "No test-only doors" gets a file-name test. The rest stays judgement.
- **Value.** Medium. Go only.

### pr-description

- **By hand.** Count the characters (about 1000). Count sentences per paragraph (at most 6). Check the title for a prefix, a period, and the mood. Fetch the current body before an edit.
- **Script.** `scripts/check_pr.py <title> <body-file>` checks these and runs the prose rules. A second mode prints a diff between the live body and the last version, so a hand edit is never lost.
- **Replaces a judgement.** "About 1000 characters", "maximum 6 sentences", "no conventional-commit prefix".
- **Value.** High. This is the next pilot, because it has the same shape as `commit-message` and the same cheap grader.

### review-code

- **By hand.** "List what the change adds." Find each new exported name, file, flag, and option. Then find every caller of each one. Then find code that lost its last caller.
- **Script.** `scripts/added_symbols.py` reads the diff, extracts added definitions for Go, TypeScript, and Python, and counts references with `git grep`. A symbol with one reference, its own definition, is a cut candidate.
- **Replaces a judgement.** "Does a function lose its last caller" becomes a reference count.
- **Value.** High. The size check is a major part of the skill, and a model misses callers in large repos.

### review-loop

- **By hand.** Collect the base branch, the PR title and body, and the commit list for each reviewer brief. Count rounds against the cap of three. Keep the nits from each round.
- **Script.** `scripts/context.sh <pr>` prints the brief header. `scripts/rounds.sh` appends a round to a ledger, refuses a fourth round, and prints all nits at wrap-up.
- **Replaces a judgement.** "Three round cap" becomes a refusal.
- **Value.** Medium.

### review-pr

- **By hand.** Compute new-file line numbers from the `@@ -a,b +c,d @@` headers. Check each finding falls inside a hunk. Write `review.json`. Count the posted comments.
- **Script.** `scripts/build_review.py pr.diff findings.json` checks each path and line against the hunks. It moves an outside line to the nearest changed line and writes `review.json` with `commit_id`. It fails on a sentence over 25 words, an em dash, a semicolon, or a list.
- **Replaces a judgement.** "Anchor it to the nearest related changed line". GitHub rejects the whole review for one bad line, so the check has a real cost saving.
- **Value.** High. The eval needs a PR and `gh`, so it is not part of this round.

### technical-writing

- **By hand.** Count words per sentence. Find passive voice, slashes, "(s)", "simply", "please", "click here", semicolons, and em dashes. Check sentence-case headings.
- **Script.** Extend `unslop/scripts/prose_check.py` with a `--strict` mode for these rules. The skill and `unslop` then share one checker.
- **Replaces a judgement.** Everything in that list except the passive voice, which needs a parser. A rough pattern for "is/are/was/were" plus a past participle finds most cases.
- **Value.** High. Every other writing skill points here.

### unslop

- **By hand.** Scan for em dashes, semicolons, curly quotes, the AI vocabulary list, filler phrases, and sentences over 25 words.
- **Script.** `scripts/prose_check.py <file>` prints each hit with its rule number and exits with 1 on a finding. See `evals/results/unslop.md`.
- **Replaces a judgement.** Rules 7, 8, 9, 13, 19, 20, 23, 26, 28, and 31 for the patterns that have a fixed spelling.
- **Value.** High. The skill applies to all writing.

### way-of-working

- **By hand.** Create a worktree off `origin/main`, pick a branch name, remember the phase list, and write the final report.
- **Script.** `scripts/worktree_new.sh <type> <slug>` checks the name against `<type>/<slug>`, runs `git fetch`, and creates the worktree off `origin/main`.
- **Replaces a judgement.** The branch name format.
- **Value.** Medium. The skill is a long procedure with little arithmetic in it.

### website-copy-review

- **By hand.** Fetch the page source. Read the title, meta description, headings, links, and forms. Test each link for a status code. Test the path from the headline to the call to action.
- **Script.** `scripts/page_facts.py <url>` prints title, meta tags, headings, links with their status codes, and forms, as plain text. It uses `urllib` and `html.parser`.
- **Replaces a judgement.** "Test the conversion path" gets facts, so the agent judges the copy and not the plumbing.
- **Value.** High. The step is mechanical and the output is large to read by hand.

### why

- **By hand.** Find the PR for a commit, then read the PR body and review comments with three `gh` calls. Decide whether a commit only reformats.
- **Script.** `scripts/pr_for_commit.sh <sha>` prints the PR number, body, and review comments. `scripts/is_reformat.sh <sha>` compares `git show -w` with the empty result.
- **Replaces a judgement.** "A commit that only reformats" becomes a whitespace-insensitive diff test.
- **Value.** Medium. `git-why` has no test suite in this repo. Its tests belong in the upstream repo, or a copy here.

## Where a check can replace a judgement

These are the cases where the skill asks the agent to decide something that a rule decides.

| Skill | Judgement today | Check |
| --- | --- | --- |
| `unslop`, `technical-writing`, `copy-review` | "Is this sentence too long" | Word count over 25 |
| `unslop` | "Does this text use AI words" | Word list match |
| `commit-message` | "Is the subject a Conventional Commit" | A regular expression |
| `commit-message`, `pr-description` | "Is there an attribution line" | A string match |
| `pr-description` | "Is the body about 1000 characters" | A length count |
| `review-pr` | "Is the line inside the diff" | Hunk arithmetic |
| `review-code` | "Does the change leave code unused" | A reference count |
| `decision-log` | "Does every pointer resolve" | `git cat-file` and `test -e` |
| `git-rebase` | "Is the todo correct" | A SHA lookup in the range |
| `commit-gate` | "Can a staged file affect the suite" | A path pattern |
| `implement-issue` | "Which issue is next" | A sort and a filter |
| `why` | "Does this commit only reformat" | `git show -w` is empty |

## What the script cannot do

A script finds the form of bad writing, not the cause. A text can pass `prose_check.py` and still say nothing. A message can pass `check_commit.py` and give no reason. The skills keep their judgement rules for that. The eval cases therefore include checks that the facts survive, so a rewrite that deletes the content does not pass.

Two scripts would copy code from each other. `check_commit.py` and `prose_check.py` both count sentence words. A shared module is the next step if a third script needs the same code. A skill folder must stay self-contained, because `~/.agents/skills/<name>` links to one folder at a time.

## The pilots

The pilots are `unslop` and `commit-message`. Both are high value, both are used in nearly every session, and both have output that a regular expression or a counter can grade. That keeps the eval cheap and free of model grading. `review-pr`, `review-code`, and `implement-issue` rank as high, but their evals need a GitHub repo and `gh` access, which the eval sandbox does not provide.
