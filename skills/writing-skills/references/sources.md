# Sources

These are the sources behind `writing-skills`. Each entry says what it is, what the skill took from it, and where it disagrees with another source. Read on 2026-11-18. Pages move, so check a number against the source before you rely on it.

## Primary sources

### Anthropic, Agent Skills overview

https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

The old address, `docs.claude.com/en/docs/agents-and-tools/agent-skills/overview`, redirects here. Taken from it:

- The three loading levels. Metadata is always loaded, at about 100 tokens per skill. The `SKILL.md` body loads when the skill triggers. Other files load only when read.
- `name` is at most 64 characters, uses lowercase letters, digits, and hyphens, and cannot contain the reserved words `anthropic` and `claude`.
- `description` is not empty, at most 1,024 characters, and has no XML tags.
- Script code never enters the context. Only the output does.

### Anthropic, Skill authoring best practices

https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Taken from it:

- "Concise is key." Assume the model is already smart.
- The description says what the skill does and when to use it. Write it in third person, because it goes into the system prompt.
- Keep the `SKILL.md` body under 500 lines. Keep references one level deep from `SKILL.md`. Add a table of contents to a reference file over 100 lines.
- Prefer scripts for deterministic work. Say whether the agent runs a script or reads it. Scripts handle their errors and do not leave the agent to guess.
- Build evaluations before extensive documentation. Use at least three scenarios and a baseline without the skill. Test with each model you target.
- Write the skill with one Claude and test it with another on real tasks. Feed what the second one does back into the skill.
- A checklist at the end of the page. The `writing-skills` checklist extends it.

### Anthropic, Claude Code skills

https://code.claude.com/docs/en/skills

Taken from it:

- When a skill is the right tool: "when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact."
- Claude Code fields beyond the spec: `when_to_use`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `paths`, and more. The combined `description` and `when_to_use` text is cut at 1,536 characters in the skill listing.
- The 500-line limit is "a tip, not a hard limit."
- Unknown frontmatter fields are ignored in Claude Code.

### Agent Skills specification

https://agentskills.io/specification

An open format that Anthropic published. Taken from it:

- `name` must match the parent folder name. It uses 1 to 64 lowercase letters, digits, and single hyphens, with no leading or trailing hyphen.
- `description` has 1 to 1,024 characters. It says what the skill does and when to use it.
- Optional fields: `license`, `compatibility` (at most 500 characters), `metadata`, and `allowed-tools` (experimental).
- The folder layout: `SKILL.md`, `scripts/`, `references/`, `assets/`.
- Keep `SKILL.md` under 500 lines and under about 5,000 tokens.

### Agent Skills guides on agentskills.io

- Best practices: https://agentskills.io/skill-creation/best-practices.md
- Optimizing descriptions: https://agentskills.io/skill-creation/optimizing-descriptions.md
- Evaluating skills: https://agentskills.io/skill-creation/evaluating-skills.md
- Using scripts: https://agentskills.io/skill-creation/using-scripts.md

Taken from them:

- Write the description in the imperative: "Use this skill when ...". Err on the side of being pushy, because agents under-trigger.
- Test a description with about 20 queries. Make 8 to 10 of them should-trigger and 8 to 10 should-not-trigger, and make the negatives near misses. Run each query three times. Hold out part of the set to check the result. Choose the best iteration by the held-out score, not the last one.
- An eval runs each test case twice, with the skill and without it, or with the previous version of the skill. Grade with assertions that name concrete evidence. Drop assertions that pass in both arms.
- A script must not prompt for input. It prints `--help`, sends data to stdout and diagnostics to stderr, keeps its output small, and uses exit codes.

### Anthropic, skills repository and skill-creator

- https://github.com/anthropics/skills
- https://raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/SKILL.md

Taken from them:

- The skill-creator loop: draft, run test prompts with and without the skill, review the outputs, improve, repeat.
- "Make the skill descriptions a little bit 'pushy'", because Claude tends to undertrigger. Put all "when to use" information in the description and not in the body.
- Bundle a script when every test run wrote a similar helper script on its own.
- Add a table of contents to a reference file over 300 lines. The best-practices page says 100 lines. See the disagreements below.

### Anthropic engineering, Equipping agents for the real world with Agent Skills

https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

Published 2025-10-16. Taken from it:

- The agent sees only name and description at startup, so these two fields decide whether the skill loads.
- Progressive disclosure keeps bundled content out of the context until the agent needs it.
- Start with evaluation. Find the gaps on representative tasks, then build the skill in small steps.
- A script runs without its source or its input entering the context, and its result is deterministic.

## Practitioner sources

### Jesse Vincent, superpowers `writing-skills`

https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md

Taken from it:

- The description holds triggering conditions only, never a summary of the workflow. An agent that reads a workflow summary in the description may follow the summary and skip the body. The author reports one case of this.
- Write the skill as test-driven development. Run a baseline without the skill and watch it fail before you write. The rule covers edits as well.
- Choose the form of a rule from the failure you saw. A prohibition fixes a rule violation. It does not fix a shaping problem.
- Do not make a skill of a project convention. Put it in the instructions file. Automate a mechanical constraint that a pattern or a validator can enforce.
- Run a bundled script through its interpreter, as in `python3 scripts/tool.py`, because some packagers drop the executable bit.

### Vercel, AGENTS.md outperforms skills in our agent evals

https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals

Published 2026-01-27. Taken from it:

- On their Next.js 16 evals, the agent never invoked the skill in 56% of cases. Passing was 53%, equal to no documentation.
- A compressed docs index in `AGENTS.md` passed 100%. A skill that fires unreliably does worse than context that is always there.
- The wording of the instruction that points to a skill changes how the agent uses it.
- Skills still suit action-specific workflows that a user triggers on purpose.

This is one vendor's eval on one framework's documentation. It does not measure skill quality in general. It does show why a trigger description needs a test.

### Simon Willison, Claude Skills are awesome, maybe a bigger deal than MCP

https://simonwillison.net/2025/Oct/16/claude-skills/

Taken from it: a skill costs a few dozen tokens until it loads, a pre-written script makes a result reliable, and a skill is "Markdown with a tiny bit of YAML metadata and some optional scripts." The post gives no authoring rules.

### Kent C. Dodds, "What I Changed to Beat a Million-Install AI Skill"

https://www.youtube.com/watch?v=WCAxkDOdhSs

Not read. YouTube blocks this machine. A search of his blog (https://kentcdodds.com/blog), its RSS feed, and his GitHub profile found no written version, no transcript, and no skills repository. His closest post, https://kentcdodds.com/blog/introducing-kody-your-personal-software-factory, argues for durable hosted code over a `SKILL.md` file but says nothing about changing a skill. The operator reports that the talk says to ship tested scripts and to prove a change with an eval. The skill teaches those two points from the operator's brief and from the sources above, not from the talk.

## Where the sources disagree

| Topic | One view | Other view | What `writing-skills` does |
| --- | --- | --- | --- |
| Voice of the description | Third person: "Processes Excel files." (best-practices) | Imperative: "Use this skill when ..." (agentskills.io) | Write what the skill does in a short third-person phrase, then triggers in the imperative: "Use when ...". The checker accepts both. |
| Content of the description | What the skill does and when to use it (Anthropic) | Triggering conditions only, never the workflow (superpowers) | State the purpose in one short phrase. Never list the steps. Put the triggers after it. |
| Pushiness | Be a little pushy, because agents under-trigger (skill-creator, agentskills.io) | Not mentioned (best-practices). A "MUST invoke" instruction anchored agents on the skill (Vercel) | Name the phrases and situations plainly. Add skip conditions. Test with near misses instead of shouting. |
| Reliability of triggers | Claude loads a skill when the description fits (Anthropic) | The agent skipped the skill in 56% of cases (Vercel) | Treat a description as code that needs a test. Put always-needed rules in `AGENTS.md`. |
| `name` and the folder | Must match (spec) | Defaults to the folder and can differ (Claude Code docs) | The checker requires a match, because the spec and the symlinks in this repo need it. |
| Required `description` | Required (spec, platform) | Recommended, with a fallback to the first paragraph (Claude Code docs) | Always write it. |
| Length limits | 1,024 characters for `description` (spec, platform) | 1,536 for `description` plus `when_to_use` in the listing (Claude Code docs) | The checker uses 1,024. Do not rely on the larger number. |
| Table of contents | Over 100 lines (best-practices) | Over 300 lines (skill-creator) | Add one over 100 lines. It costs little. |
| Reserved words | `anthropic` and `claude` (platform) | None (spec). `anthropic-skills` and `synced` (Claude Code docs) | The checker rejects `anthropic` and `claude` in a name. |
| Where references live | `references/` (spec, skill-creator) | Files at the skill root, such as `REFERENCE.md` (platform) | Use `references/`, as the spec does and as `decision-log` does here. |
| Test rigor | At least three evals, no runner provided (best-practices) | A failing baseline before every edit (superpowers) | Use a script grader and a before and after run for any change that claims a gain. |
| Unknown frontmatter keys | Ignored (Claude Code) | A hard error outside Claude Code (portability note in the same docs) | Use only the spec fields unless the skill needs a Claude Code field. |
