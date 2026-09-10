---
name: grilling
description: Interviews the user in rounds until a plan, design, or spec has no silent assumptions. TRIGGER at the spec step of a task, when the user says grill me, stress-test this, poke holes, or asks whether a plan is complete, and before a spec is called good. SKIP when the user gives a fully specified task.
---

# Grilling

Interview the user until you share one understanding of the work. Treat the
plan as a design tree. Every decision branches into the decisions that hang
off it.

## Rounds

Work the tree in rounds. The frontier is every decision whose prerequisites
are settled, so you can ask it now without a guess at an answer you have
not heard. Ask the whole frontier in one round. Number each question and
give your recommended answer. Then stop and wait for the answers.

A round looks like this:

```
Q1. <question title>
<question body, with the choices when there are choices>
Recommended: <your answer, one or two sentences>

Q2. <question title>
...
```

Each round of answers reshapes the tree. Settled decisions push the
frontier outward and unblock the questions that depended on them. Recompute
the frontier and ask the next round. A question whose answer depends on
another open question in the same round belongs to a later round.

## Facts and decisions

Facts are your job. Decisions are the user's.

When a question needs a fact from the repository, the spec repo, or a tool,
find it. Spawn an investigation agent with the model override your
instructions require, or read it yourself when it is one file. Do not ask
the user for anything you can look up. Do not block the round on it. A
running investigation is an unsettled prerequisite, so only the questions
downstream of it wait. Ask the rest of the frontier now.

Put each decision to the user and wait. Do not answer a decision for them,
even when the recommended answer looks obvious.

## Done

The session is done when the frontier is empty: every branch visited,
nothing left silently assumed. Say so, and summarise the settled decisions
in one list. Do not act on the plan until the user confirms the summary.

Source: adapted from the `grilling` skill by Matt Pocock
(github.com/mattpocock/skills, MIT).
