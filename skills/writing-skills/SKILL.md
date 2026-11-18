---
name: writing-skills
description: Writes a new skill or improves an existing one so that it loads at the right time and then works. TRIGGER when asked to create, write, edit, review, shorten, or fix the triggering of a skill or a SKILL.md, when a skill loads at the wrong time or never loads, and before you add a script to a skill. SKIP for a rule that applies to one repo only. That goes in its AGENTS.md.
---

# Writing skills

A skill is a folder that an agent loads on demand. The agent reads only the
name and description of every installed skill. It reads the rest when the
description matches. Most failures start there. A good body behind a bad
description never runs.

## Is a skill the right tool

Pick the cheapest tool that does the job.

| The need | The tool |
| --- | --- |
| A fact or rule for one repo, needed in every session | `AGENTS.md` in that repo. A skill that must always load is a rule, not a skill. |
| A mechanical rule that a program can check | A hook, a lint, or a CI check. It enforces the rule every time. |
| A multi-step procedure or a body of knowledge that matters only for some tasks | A skill. It costs about 100 tokens until it loads. |
| A step that is the same every run | A script inside a skill, which `SKILL.md` tells the agent to run. |
| A one-off instruction | The prompt. |

Check these before you start:

- The agent does the task badly without the skill. Run the task once with no
  skill and write down what went wrong. If it went well, write no skill.
- The skill covers one coherent unit of work. Two jobs that never share a
  trigger are two skills.
- Another team could use it. Keep company names and paths out. A skill that
  needs them belongs in that company's spec repo.

## Folder layout

```
skill-name/
  SKILL.md          required, the only file the agent always reads
  scripts/          code the agent runs, with its tests
  references/       text the agent reads when a step says so
  assets/           templates and files that the output uses
```

- The folder name is the skill name. Use lowercase letters, digits, and single
  hyphens.
- The folder is self-contained. `~/.agents/skills/<name>` links to one folder,
  so a skill cannot import from a sibling skill.
- Link each file from `SKILL.md` one level deep, with the step that needs it.
  A reference that links to another reference gets read in part.
- Keep the README out of the folder. `skills/README.md` lists every skill.

## Frontmatter

```yaml
---
name: skill-name
description: Does X. Use when ... SKIP when ...
---
```

| Field | Rule |
| --- | --- |
| `name` | Required. At most 64 characters. Lowercase letters, digits, single hyphens. Equals the folder name. No `anthropic` or `claude`. |
| `description` | Required. At most 1,024 characters. No `<` or `>`. Says when to use the skill. |
| `compatibility`, `license`, `metadata`, `allowed-tools` | Optional. Add one only when you need it. |

Claude Code adds fields such as `disable-model-invocation` and `paths`. Other
tools reject them, so add them only for a skill that runs in Claude Code.
`references/sources.md` lists where the sources disagree on these limits.

## The description is a trigger

The description is not a summary. It tells the model when to load the skill,
and the model decides from it alone. Write it in this order:

1. One short phrase for what the skill does.
2. `TRIGGER when` or `Use when`, then the situations that must load it. Name
   the words a user types, the moments in the work, and the signals in code.
3. `SKIP when` and the nearest case that must not load it.

Rules:

- Never list the steps of the skill. The agent may follow the list and skip
  the body.
- Write facts the model can match: "when a comment and the code disagree",
  not "for documentation help".
- Write in third person or the imperative. Never "I can" or "you can".
- Put every "when to use" fact here. The body loads too late to help.
- Keep it under 1,024 characters. Most good ones need 300 to 600.
- Make a skill that is too quiet a little louder. Do not shout.
  Add the phrases that failed to match. Capital letters and "MUST" make the
  agent over-trust the skill.

`references/description-examples.md` has good and bad descriptions from the
skills in this repo, with rewrites. Read it before you write a description.

## Test the description

A description is code, and code needs a test. Vercel measured an agent that
skipped an available skill in 56% of cases. Test yours:

1. Write 16 to 20 prompts. Half should load the skill. Half are near misses
   that share words with it but must not load it.
2. Run each prompt three times in a fresh session with the skill installed.
   Record whether the skill loaded.
3. Edit the description where a prompt fails. Keep a few prompts out of the
   edits, then check the final text against those.

A description that passes all the should-load prompts and loads on a near miss
needs a `SKIP` line. A description that misses a prompt needs that phrase.

## Write the body

- Aim for 100 lines. The limit is 500 lines. Past that, move detail to
  `references/` and say in `SKILL.md` when to read it.
- Assume the agent is smart. State what it does not know: your repo's rules,
  the order of steps, the trap it falls into. Cut what a competent agent does
  without being told.
- State the rule, then the reason. A rule with a reason holds better.
- Number the steps that must run in order. Use bullets for rules without order.
- Name what the agent must not do. Skills fail most on an action the author
  assumed nobody would take.
- Give one default and one escape. "Use `pdfplumber`. For scanned pages, use
  OCR." Do not list five tools.
- Say whether a file is to be run or to be read. "Run `scripts/<name>.py`" and
  "Read `references/<name>.md`" mean different things.
- Match the other skills here: active voice, at most 25 words per sentence, no
  em dashes, no semicolons. Follow `technical-writing` and `unslop`.
- Write what is true now. Leave out dates, version numbers that will age, and
  the history of how you wrote the skill.

## Put mechanical steps in scripts

A model counts words badly and forgets a rule it read 200 lines earlier. A
script gives the same answer on every run, and its code never enters the
context. Move a step into a script when it has a fixed rule, such as a count,
a format check, a lookup, or a command with tricky quoting.

- Keep judgement in the text. A script finds the form of a defect and not its
  cause.
- Use the Python 3.12 standard library or POSIX sh. Nothing to install.
- The script reads files or arguments and never prompts. It prints findings on
  stdout, diagnostics on stderr, and exits 0 for clean, 1 for findings, 2 for
  misuse. It prints a usage line without arguments.
- Put the tests next to it as `scripts/test_<name>.py`. Test each rule with a
  passing input, a failing input, and the edge at each limit.
- `SKILL.md` tells the agent to run it: "Run `python3 scripts/<name>.py <file>`
  until it exits 0." Name the interpreter, because a packager may drop the
  executable bit.
- Run the tests before you commit: `python3 -m unittest discover -s scripts`.
- When the script has a bug, fix the script and its test. Do not add a rule to
  the text that works around it.

## Prove a change with an eval

A change to a skill is a claim that the agent now does better. Test the claim.

1. Write 5 to 10 cases, each with a prompt and a check that a script can grade.
   Give each case a trap that the old skill fails.
2. Run each case several times with the old skill and with the new skill. A
   baseline of no skill shows whether the skill helps at all.
3. Grade with a regular expression, a count, or an exit code. A model that
   grades the model flatters it. Include a check that the facts survive, so a
   run cannot pass by deleting the content.
4. Compare the pass rates. Keep the change only when the rate rises and the
   `SKILL.md` did not grow without reason. If it did not help, say so and keep
   the old skill.
5. Three runs per case is a small sample. One flip from 3 of 3 to 2 of 3 is
   noise.

When the repo has `evals/` and `docs/skill-scripts-audit.md`, read
`evals/README.md` and use `evals/run.py`. When it does not, run the same loop
by hand with `claude -p` in a temporary folder.

## Check the folder

Run the checker on the skill folder before you say it is done:

```sh
python3 scripts/check_skill.py skills/<name>
```

It checks the frontmatter, the name against the folder, the description
length and its trigger phrase, the length of `SKILL.md`, and that each linked
file exists. It exits 1 on any finding. Its own tests run with
`python3 -m unittest discover -s scripts` in this folder. It cannot judge
whether the description matches the real triggers. The checklist covers that.

## Checklist

Do all of these before you call a skill done.

- [ ] The task went badly without the skill, and you know how.
- [ ] A skill is the right tool, not `AGENTS.md`, a hook, or a script alone.
- [ ] `name` equals the folder name and follows the charset rule.
- [ ] The description says when to use the skill, names user phrases and
      moments, and has a `SKIP` line when a near miss exists.
- [ ] The description lists no steps and uses no `<` or `>`.
- [ ] You ran should-load and near-miss prompts, three times each.
- [ ] `SKILL.md` is under 500 lines. It is closer to 100 when it can be.
- [ ] Each file in `references/` is linked from `SKILL.md`, one level deep.
- [ ] Each step with a fixed rule is a script, and the script has tests that
      pass.
- [ ] `SKILL.md` tells the agent to run each script, with the interpreter.
- [ ] A before and after eval shows the change helps, or you say it does not.
- [ ] `scripts/check_skill.py` exits 0 on the folder.
- [ ] No company names, personal paths, or dates that will age.
- [ ] The text follows `technical-writing` and `unslop`.
- [ ] `skills/README.md` lists the skill.

See `references/sources.md` for the sources behind these rules.
