@~/AGENTS.md

# Subagent model policy (Claude Code specific)

Never spawn subagents on Fable 5. Subagents inherit the session model by
default, and the Fable 5 usage limit is too small for agent fan-outs. When
the session itself runs on Fable 5, pass an explicit `model` override
(opus or sonnet) on EVERY Agent call, workers and reviewers alike. Fable
is for the main conversation loop only.
