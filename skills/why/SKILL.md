---
name: why
description: Finds the reason behind code, a change, a review comment, or a number, from commit bodies, PR threads, issues, and logs. TRIGGER when asked why something is the way it is or why a colleague chose or wrote something, before you change or delete a line whose purpose is unclear, when a comment and the code disagree, before you run git blame or git log, and when a guard, flag, threshold, or test looks arbitrary. SKIP when the question is only who or when.
---

# Why

Find the forces that gave the code its shape. Report what the record says,
separate from what you infer.

## Sources, in this order

1. **The commit bodies behind the lines.** Run `git-why` on the line range.
   It groups the lines by commit and prints the messages that explain
   them. This is the first step, before any `git blame` or `git log`.
2. **The file history.** `git log --follow --oneline -- <file>` for the
   commits that touched the file, with PR numbers in the subjects.
3. **The PR thread.** For each substantive commit, the PR body, reviews, and
   review comments:

   ```sh
   gh pr view <n> --json title,body,reviews,comments,closingIssuesReferences
   gh api repos/<owner>/<repo>/pulls/<n>/comments --jq '.[] | {path, line, body}'
   ```

   A review comment often holds the reason a line looks the way it does.
4. **Linked issues and the spec repo.** Issues the PR closes, and the
   feature doc in the spec repo if the workspace has one.
5. **Logs.** When the code reacts to a runtime signal, such as a retry, a
   timeout, a guard, or a threshold, read the logs. The workspace
   instructions name the log source and its tooling.

A search that finds nothing is a finding. Say which sources you read and
which returned nothing.

## Run git-why

```sh
git-why <file> <line>
git-why <file> <start>-<end>
git-why <file>                 # whole file, ranked commits, no blame table
```

`git why` works too, because git runs any `git-*` on PATH. Options go before
the file. `-n` caps the commits printed, `-b` caps body lines, and
`--ignore-revs-file` names a reflow-commit list.

The script ships in this skill directory. If the command is missing, link it
into a PATH directory:

```sh
ln -s ~/.agents/skills/why/git-why ~/.local/bin/git-why
```

Source and README: https://github.com/JacobJNilsson/git-why

## Report

Keep three parts apart:

- **Found.** What the record states, each with its citation: a commit hash,
  a PR number, a comment permalink, an issue, or a log query.
- **Inferred.** What you conclude from the found facts. Say what it rests
  on.
- **Unknown.** What no source answers. Name the source that would.

When the question precedes a change, end with what to preserve, what is
free to change, and what to avoid.

Never invent a caller, a commit, or a reason. Recency is not authority: the
current shape is often the sum of several earlier decisions. Trace back.

## Limits of the record

The output is only as good as the commit messages. A repository that
squashes a feature into one commit returns one long message about the whole
feature, not about your line. That is a limit of the history, not of the
tool.

If `git-why` names a commit that only reformats, and that commit moved bytes
without a change to the words, add it to `.git-blame-ignore-revs`. The next
reader then gets the commit before it. This does not work for a commit that
rewrote prose, for example one that split a sentence to meet a length rule.
Git re-attributes an ignored line only when it finds that line in a parent
version. Read the other commits in the range instead.

Source: the pstack `why` skill (github.com/cursor/plugins, MIT) gave the
source order and the found, inferred, unknown split.
