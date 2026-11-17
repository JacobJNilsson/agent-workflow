# Eval results: unslop

The change adds `skills/unslop/scripts/prose_check.py`. `SKILL.md` tells the agent to run it before and after the rewrite.

**Verdict: keep.** The pass rate rises from 80% to 100%. `SKILL.md` shrinks from 998 to 989 words.

## Setup

- Model: `haiku`, the fast tier from `config/models.env`.
- Old skill: `main` at the branch point. New skill: this branch.
- 10 cases, 3 runs per case and arm, 60 `claude -p` calls for the final numbers.
- Cases: `evals/cases/unslop.json`. Raw runs: `evals/results/unslop.json`.
- The agent gets `draft.md` with AI tells and the prompt "Use the unslop skill to edit draft.md". A script grades the saved file.
- A run passes when every check passes. The checks are:
  - No em dash, en dash, or spaced hyphen.
  - No semicolon, except in the code case.
  - No curly quote.
  - No sentence over 25 words.
  - None of a list of banned words.
  - Each key fact is still present.

## Pass rate

| Case | Old | New |
| --- | --- | --- |
| ai-vocabulary | 3/3 | 3/3 |
| code-block-kept | 3/3 | 3/3 |
| hyphen-dashes | 3/3 | 3/3 |
| long-doc-mixed | 1/3 | 3/3 |
| long-sentences | 0/3 | 3/3 |
| many-long-sentences | 2/3 | 3/3 |
| one-long-sentence | 3/3 | 3/3 |
| pr-body-list | 3/3 | 3/3 |
| quotes-and-filler | 3/3 | 3/3 |
| release-note-dashes | 3/3 | 3/3 |
| **All cases** | **24/30 (80%)** | **30/30 (100%)** |

All 6 old failures are the 25-word limit. The old agent splits most long sentences but keeps one of 26 or more words. In the new arm the script ran in 30 of 30 runs and it reports each long sentence with its line. The old arm never had a script to run.

## Cost and size

| | Old | New |
| --- | --- | --- |
| `SKILL.md` words | 998 | 989 |
| Turns per run | 5.1 | 7.2 |
| Cost for 30 runs | $0.11 | $0.12 |

The new arm costs about 16% more per run, because the agent runs the script at least twice.

## Limits of this result

- The grader and the script count words the same way. The result shows that the agent follows the 25-word rule with the script. It does not show that the text reads better.
- Five of ten cases were already saturated at 3/3 for the old skill. Only the length rule separates the arms.
- Cases are synthetic and short. A real README may behave differently.
- The change to `SKILL.md` also trims the wording of rules 14 and 27 to make the file shorter. Those rules are judgement rules, and no check grades them.
- After these runs, `prose_check.py` got two fixes that I found when I ran it on this repo's docs. Each table cell now counts as its own text, where a whole table counted as one long sentence before. An indented list marker no longer counts as a spaced hyphen. No case has a table or an indented list, and unit tests cover both.

## How the numbers were produced

- A first run of 8 cases (48 calls) hit a bug in the grader. The dash pattern also matched a Markdown list marker, so `pr-body-list` failed in both arms. The pattern was fixed and that case ran again, 6 more calls. Only the second run appears in the table.
- Two smoke calls for one case came before the full run. They are in `evals/results/ledger.tsv` and not in the table.

Reproduce with `python3 evals/run.py run unslop`.
