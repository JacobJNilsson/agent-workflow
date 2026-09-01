---
name: git-why
description: Find why a line of code is the way it is, by reading the commit reasoning behind it instead of a blame table. Use before changing a line whose purpose is unclear, when a comment and the code disagree, or when a test or guard looks arbitrary.
---

# Why is this line here

`git blame` answers "who and when". That is rarely the question. The question
is "why", and the answer sits in the commit message body.

Reading raw blame is also expensive and misleading:

- `git blame -w` on a 25 KB file prints 58 KB. It costs more than reading the
  source, and it returns hashes and dates rather than reasons.
- A commit that only reflows prose MASKS the real reason. Blame reports the
  reflow commit, whose message says nothing about the line.

Use `git-why` instead. It reads a line range, groups the lines by commit, and
prints the commit MESSAGES that explain them.

## Use it

```sh
git-why <file> <line>
git-why <file> <start>-<end>
git-why <file>                 # whole file, ranked commits, no blame table
```

`git why` works too, because git dispatches any `git-*` on PATH.

Useful options: `-n` caps the commits printed, `-b` caps body lines,
`--ignore-revs-file` names a reflow-commit list explicitly.

Source and README: https://github.com/JacobJNilsson/git-why

## When to reach for it

- Before you change or delete a line whose purpose is not obvious. The commit
  body often names the incident that put it there.
- When a comment and the code disagree. The commit says which one moved.
- When a flag, a guard, or a test looks arbitrary. Examples worth checking:
  `-p 1` on a test command, a lockfile pin, a timeout value.
- Before you "simplify" something. A short line can carry a long reason.

## What it cannot tell you

The output is only as good as the commit messages. A repository that squashes
a feature into one commit returns one long message about the whole feature,
not about your line. Read that as a limit of the history, not of the tool.

If the answer names a commit that only reformats, and that commit MOVED bytes
without changing words, add it to `.git-blame-ignore-revs`. The next reader
then sees through it.

This does not work for a commit that REWROTE prose, such as one splitting a
sentence to meet a length rule. git re-attributes an ignored line only when it
can match that line in a parent version, and rewritten text has no counterpart
there. Read the other commits in the range instead.
