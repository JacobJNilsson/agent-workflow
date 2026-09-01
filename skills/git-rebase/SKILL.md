---
name: git-rebase
description: Perform interactive git rebases without opening an editor. Use when asked to squash, fixup, reorder, drop, or edit commits.
---

# Interactive rebase without an editor

Never run `git rebase -i` directly — it blocks on an editor. Always use
`GIT_SEQUENCE_EDITOR` with a heredoc instead.

## Workflow

1. Get the initial todo so you know the exact SHAs and order to work from:
   ```sh
   git rebase -i --no-commit <base>  # won't work — instead:
   git log --oneline <base>...HEAD
   ```
   Then construct the full todo manually.

2. Write the desired todo via heredoc:
   ```sh
   GIT_SEQUENCE_EDITOR="cat > \$1 <<'EOF'
   pick <sha-a> first commit
   fixup <sha-b> commit to fold in
   EOF" git rebase -i <base>
   ```

3. Verify: `git log --oneline <base>...HEAD`

4. Push: `git push --force-with-lease`

## On conflicts

```sh
# After resolving files:
git add <files>
GIT_EDITOR=true git rebase --continue
```
