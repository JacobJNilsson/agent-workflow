---
name: luigi-rebase-merge-commits
description: luigi PRs are rebase-merged, every commit lands on main as is, so each commit must build and intermediate-state comments are acceptable history
metadata:
  type: feedback
---

Merges PRs by rebase. Every commit of a PR lands on main unchanged.

**Why:** merging stacked PRs together does not hide an intermediate
state, because each commit still lands on main.

**How to apply:** make every commit on a branch build and vet on its own.
A comment that is true at its commit and removed by a later commit is
fine. Do not offer to merge PRs to hide an intermediate state.
