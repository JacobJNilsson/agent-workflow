---
name: commit-gate
description: Sets up a tracked git pre-commit hook that blocks a commit when lint, build, or tests fail, installed with one make target. TRIGGER when asked to add a pre-commit hook, a commit gate, git hooks, or to block commits that fail tests or lint. Covers Go and Node repos, and the pre-push tier for slow suites.
---

# Commit gate

A commit gate is a pre-commit hook that runs the repo's checks and stops
the commit when one fails. Set it up so that the hook is tracked, one
command installs it, and it runs the same targets as CI.

## Rules

1. **Track the hook.** The hook script lives in the repo, not only in
   `.git/hooks`. A hook that lives only in `.git/hooks` is lost on a fresh
   clone and missing in every worktree. Put it in `.githooks/` and point
   `core.hooksPath` at that directory. Worktrees share the repo config,
   so one install covers all of them.

2. **One install command.** Add a `make setup` target that runs
   `git config core.hooksPath .githooks`. State the command in the repo's
   README and agent instructions. A dependency on a hook manager (husky,
   lefthook, pre-commit) adds a package for a task that git does alone.
   Only add one if the repo already uses it.

3. **Call make targets, not tools.** The hook runs `make lint`, `make
   test`, and `make build`, or a `make check` that combines them. CI runs
   the same targets. Then the hook and CI cannot drift.

4. **Verify, do not mutate.** The hook runs after the files are staged. A
   step that rewrites files (`go mod tidy`, a formatter with `-w`) commits
   the stale staged version. Use the check forms: `go mod tidy -diff`,
   `gofumpt -l`, `prettier --check`. Tell the user to run the fix target
   by hand.

5. **Skip fast, never silently.** When no staged file can affect the
   checks (docs only), exit early, but print what was staged and which
   tier ran. An empty scope that passes without output hides a broken
   gate.

6. **Escalate on gate and toolchain changes.** A staged `Makefile`,
   `go.mod`, lint config, or `.githooks/` file changes what every check
   means. Run the full gate for those, whatever else is staged.

7. **Keep the bar, shrink the blast radius.** When the full suite is too
   slow for a commit loop, the pre-commit tier checks only the packages
   the staged files can affect, at the same bar. Add a `pre-push` hook
   that runs the full gate. Pre-push and CI stay the definition of green.

8. **Prepare the environment.** Cd to the repo top level. Put the
   toolchain on `PATH` for GUI clients, which do not read the shell
   profile: source the nix profile, or `direnv export`, or use `nix
   develop --command`. If tests shell out to git, unset `GIT_DIR`,
   `GIT_INDEX_FILE`, `GIT_WORK_TREE`, and the other `GIT_*` location
   variables first, or a test operates on the real repo.

9. **Name the escape hatch.** `git commit --no-verify` always exists.
   Add `SKIP_PRE_COMMIT=1` for the case where the user wants the hook to
   say that it was skipped. Do not skip in any other case.

## Template

`.githooks/pre-commit`:

```bash
#!/usr/bin/env bash
# Commit gate. Install with `make setup`. Bypass with SKIP_PRE_COMMIT=1.
set -euo pipefail

if [ "${SKIP_PRE_COMMIT:-}" = "1" ]; then
	echo "pre-commit: skipped (SKIP_PRE_COMMIT=1)"
	exit 0
fi

cd "$(git rev-parse --show-toplevel)"
unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE GIT_OBJECT_DIRECTORY GIT_PREFIX

staged=$(git diff --cached --name-only --diff-filter=ACMR)
if ! printf '%s\n' "$staged" | grep -qE '\.go$|^go\.(mod|sum)$|^Makefile$|^\.golangci\.ya?ml$|^\.githooks/'; then
	echo "pre-commit: no staged file affects the gate, skipping. Staged:"
	printf '  %s\n' $staged
	exit 0
fi

echo "pre-commit: make check"
make check
```

`Makefile`:

```make
.PHONY: setup check lint build test

setup:
	git config core.hooksPath .githooks

check: lint build test

lint:
	golangci-lint run ./...

build:
	go build ./...

test:
	go test ./...
```

Make the hook executable: `chmod +x .githooks/pre-commit`. Git ignores a
hook without the execute bit and says nothing.

## Per language

- **Go:** `lint` runs golangci-lint, or the repo's custom build of it.
  `check` includes `go mod tidy -diff` and `go vet ./...` when CI runs
  them. The file pattern in the template covers Go.
- **Node:** `check` runs `npm run typecheck`, `npm run lint`, and
  `npx vitest run` (or the repo's test runner, in non-watch mode). The
  file pattern is `\.(ts|tsx|js|jsx|json)$|^package(-lock)?\.json$`.
  Use `--max-warnings 0` on eslint so a warning also blocks.
- **Mixed repos:** one hook, one pattern per language, one `check` target
  per language, and the hook runs the targets whose pattern matched.

## Steps

1. Read the CI workflow. List the commands it runs. Those are the gate.
2. Find or add the make targets for them. Confirm each one passes on a
   clean checkout before you wire the hook, or the first commit fails on
   a pre-existing problem.
3. Write `.githooks/pre-commit` from the template. Adapt the file
   pattern and the environment lines. Add `.githooks/pre-push` with
   `make check` when the pre-commit tier is scoped.
4. Add `make setup`. Run it. Run the hook by hand once:
   `.githooks/pre-commit`.
5. Move any hook that lives only in `.git/hooks` into `.githooks/`, or
   delete it. Two hooks that run in sequence confuse the user about
   which one failed.
6. Document `make setup` in the README and in `AGENTS.md`.
7. Commit the hook, the Makefile change, and the docs in one commit. The
   commit itself runs the new gate.

## What not to do

- Do not run the gate on the worktree and then commit a partial stage
  without saying so. A partial commit (`git commit -p`) passes the gate
  on the worktree, not on what is committed. Pre-push and CI catch it.
- Do not weaken a check to make the hook faster. Scope it instead.
- Do not let the hook install itself from a postinstall or from a test.
  Installs are explicit.
