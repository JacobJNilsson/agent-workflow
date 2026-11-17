# Eval results: commit-message

The change adds `skills/commit-message/scripts/check_commit.py`. `SKILL.md` tells the agent to run it on the message file until it exits with 0.

**Verdict: keep, with one caveat about the size of the gain.** The pass rate rises from 26% to 96%. `SKILL.md` shrinks from 351 to 347 words. Nearly all of the gain comes from one rule, the ban on attribution lines. Without that rule the old skill already scores 96%.

## Setup

- Model: `haiku`, the fast tier from `config/models.env`.
- Old skill: `main` at the branch point. New skill: this branch.
- 9 cases, 3 runs per case and arm, 54 `claude -p` calls for the final numbers.
- Cases: `evals/cases/commit-message.json`. Raw runs: `evals/results/commit-message.json`.
- The agent gets `change.diff` and the author's notes, and writes `msg.txt`. A script grades the file.
- A run passes when every check passes. The checks are:
  - A Conventional Commit subject with the expected type.
  - A capital letter after the colon, no trailing period, and at most 72 characters.
  - A blank line and a body.
  - No sentence over 25 words.
  - No em dash, en dash, or semicolon.
  - No `Co-Authored-By` or `Generated with` line.
- Several notes in the cases use past tense, em dashes, and semicolons on purpose. They tempt the agent to copy that style.

## Pass rate

| Case | Old | New |
| --- | --- | --- |
| bugfix-timeout | 0/3 | 2/3 |
| ci-pipeline | 0/3 | 3/3 |
| deps-scope | 1/3 | 3/3 |
| docs-only | 0/3 | 3/3 |
| feature-long-context | 0/3 | 3/3 |
| past-tense-notes | 1/3 | 3/3 |
| perf-numbers | 2/3 | 3/3 |
| refactor-rename | 1/3 | 3/3 |
| test-only | 2/3 | 3/3 |
| **All cases** | **7/27 (26%)** | **26/27 (96%)** |

The same runs without the attribution check (`run.py report commit-message --without Co-Authored`):

| | Old | New |
| --- | --- | --- |
| **All cases** | **26/27 (96%)** | **27/27 (100%)** |

## Where the gain comes from

- **Attribution.** The old arm wrote a `Co-Authored-By` line in 20 of 27 runs. The new arm did so in 1 of 27 runs. `claude -p` adds that line by default when the project settings do not turn it off. The eval loads project settings only (`--setting-sources project`), so it does not see your user settings. If your own settings already turn the line off, your gain is the smaller one.
- **Sentence length.** The old arm broke the 25-word limit in 1 of 27 runs. The new arm in 0 of 27.
- **Format rules.** Capital letter, trailing period, subject length, and the type prefix never failed in either arm. The fast model already follows them.

So the script is a safety net more than a fix. It catches the attribution line, a long sentence, and a dash, and it costs a few seconds.

## Cost and size

| | Old | New |
| --- | --- | --- |
| `SKILL.md` words | 351 | 347 |
| Turns per run | 5.1 | 8.1 |
| Cost for 27 runs | $0.10 | $0.13 |

The new arm costs about 40% more per run, because the agent writes the file, runs the script, and often runs it again. The amounts are small.

## Limits of this result

- The grader and the script share rules, so the check is not independent. A pass shows the agent obeys the rules, not that the message explains the why.
- The skill says "start capitalized". The repo's own recent commits use a lowercase description, for example `feat: settle the shape of the code`. The script follows the skill text. If you want lowercase, change the rule in the skill and in `check_commit.py` together.
- The 72-character subject limit is the usual git convention. The old skill did not state it.
- The subject type is pinned per case, for example `perf` for a speed change. `deps-scope` accepts `chore`, `build`, or `fix`, because all three fit a security bump.

## How the numbers were produced

- A first version of the new `SKILL.md` had 388 words and scored 25/27 against 9/27 for the old skill. That was longer than the old skill, so it failed the "simpler" rule. The file was cut to 347 words and the full eval ran again. The table above is the second run. The first run is in `evals/results/commit-message.v1.json`.
- In the first run, `deps-scope` pinned the type to `chore` and failed both arms on type. The case now accepts `chore`, `build`, or `fix`, and that case ran again.

Reproduce with `python3 evals/run.py run commit-message`.
