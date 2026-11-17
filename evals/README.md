# Skill evals

`evals/run.py` runs a skill's test cases with the old skill and with the new skill. It reports the pass rate of each. A script grades every output, so no model decides who wins.

## Why a small harness and not the existing tools

I read two existing tools before I wrote this one.

- **`skill-creator`** (Anthropic plugin). It runs a with-skill run and a baseline run per case through subagents. For an existing skill, the baseline is a snapshot of the old version. A grader subagent, a model, judges each expectation (`agents/grader.md`). Its `run_eval.py` tests whether a skill description triggers. It has no call budget, and a model judges the output. I want a regular expression or an exit code to judge, and a hard limit on calls.
- **`claude plugin eval`**. It runs cases from `evals/**/case.yaml` or `prompt.md` plus `graders/*.md`, with a `--judge-model` option. Its baseline arm is "no plugin". I did not try it. The help text describes model graders, and an old-versus-new comparison would need two plugin copies. The skills here are a plain folder of skills and not a plugin.

The harness here is about 400 lines of standard-library Python. It fits the three needs of this repo: old versus new from git, script graders, and a call ledger. If the repo becomes a plugin, move the cases to `claude plugin eval` and keep the graders.

## Run it

```sh
python3 evals/run.py run <skill>                # 3 runs per case, old (main) against new (working tree)
python3 evals/run.py run <skill> --runs 1 --case release-note-dashes
python3 evals/run.py run <skill> --old-ref none # no skill at all as the baseline
python3 evals/run.py run <skill> --dry-run      # show the plan and the call count
python3 evals/run.py report <skill>             # print the table from the saved runs
python3 evals/run.py report <skill> --without 'Co-Authored'   # ignore failed checks that match
python3 -m unittest discover -s evals           # test the harness
```

What a run does:

1. Reads the fast tier model from `config/models.env` (`AGENT_MODEL_FAST`).
2. Copies the skill into a fresh temp directory, under `.claude/skills/<skill>`. The new arm copies the working tree. The old arm runs `git archive <old-ref>`, which defaults to `main`.
3. Writes the case's `files` into that directory.
4. Runs `claude -p` there with `--setting-sources project`, so your user skills and settings stay out. The agent may use `Bash`, `Read`, `Write`, and `Edit`.
5. Grades the output and the files with `graders.py`.
6. Writes `evals/results/<skill>.json`. A run with `--case` replaces only the records of those cases.

The cases for each skill need the working tree to hold the new skill and `main` to hold the old one. Commit the change on a branch and leave `main` alone.

## The call limit

Every `claude -p` call adds a row to `evals/results/ledger.tsv`. Before it starts, `run.py` adds the planned calls to the rows already there. It stops if the sum passes 200. The limit holds for the whole repo and not for one run. Raise it with `--max-calls`.

A skill with 10 cases and 3 runs costs 60 calls, 30 for each arm. Change a skill, run it again, and the cost doubles. Use `--case` and `--runs 1` while you work, and run the full set once at the end.

## Case files

A case file is `evals/cases/<skill>.json`:

```json
{
  "skill": "unslop",
  "cases": [
    {
      "id": "release-note-dashes",
      "prompt": "Use the unslop skill to edit draft.md. Save the result in draft.md.",
      "files": {"draft.md": "The job retries — up to 3 times."},
      "target": "draft.md",
      "preset": "prose",
      "checks": [{"type": "matches", "target": "draft.md", "pattern": "3 times"}]
    }
  ]
}
```

- `id` uses lowercase letters, digits, and hyphens.
- `files` are written into the run directory before the agent starts.
- `checks` is a list. A run passes when every check passes.
- `target` names the file a check reads. Without it, a check reads the agent's final answer, which is `"output"`.
- `preset` adds a standard list of checks for `target`. `prose` adds the dash, quote, 25-word, banned-word, and semicolon checks. `prose-code` leaves out the semicolon check. `commit` adds the Conventional Commit checks for `msg.txt`, and the optional case fields `type` and `scope` pin the type and scope.

Check types, from `graders.py`:

| Type | Passes when |
| --- | --- |
| `matches` | The regular expression matches. `flags: "i"` ignores case. `^` and `$` match at each line. |
| `not_matches` | The regular expression does not match. |
| `max_sentence_words` | No sentence has more than `limit` words. Code and inline code do not count. |
| `max_first_line` | The first line has at most `limit` characters. |
| `min_words` | The text has at least `limit` words. |
| `command` | The shell command `cmd` exits with 0 in the run directory. |

Write a facts check for each case, for example `matches` with the number that must survive. Without it, an agent passes a prose case by deleting the text. Keep each pattern loose. `free[- ]plan` is better than `free plan`, because a good rewrite may hyphenate.

## Add an eval for a new skill

1. Write 5 to 10 cases in `evals/cases/<skill>.json`. Give each one a trap that the old skill fails. A case that both arms pass tells you nothing.
2. Run it once with `--runs 1 --old-ref none` to see whether the checks can fail at all.
3. Make the change to the skill on a branch. Run `python3 evals/run.py run <skill>`.
4. Write `evals/results/<skill>.md` with the table, the cost, the size of `SKILL.md`, and the limits. Say so if the change did not help, and keep the old skill.

## Read the numbers with care

- Three runs per case is a small sample. A single flip of 3/3 to 2/3 is noise.
- The grader and a skill script often share a rule, such as the 25-word limit. The eval shows that the agent follows the rule. It does not show that the text is better.
- The harness loads project settings only. Defaults that your user settings change, such as the `Co-Authored-By` line, show up in the old arm. The commit-message results explain one such case.
- The fast model passes most format rules without help. Expect the gains to be small and to sit in the rules that need counting.
