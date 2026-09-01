---
name: simplicity-check
description: Judge whether an implementation should exist at all, and whether the goal needs less code. Returns a verdict and does not change code. Use when changes are ready for review, or when asked whether an implementation is over-built, needed, or could be simpler.
---

# Simplicity check

Correct code that nobody needs is waste. Correct code that is three times
larger than the goal requires is also waste, and it costs every reader and
every agent that meets it later.

A correctness reviewer asks "is this right". It almost never asks "should this
exist". This check asks the second question. It is a review. It reports a
verdict and stops. It does not change code, and it does not decide what
happens next.

## When to run it

Run it once, on the whole change. Scope is a judgement about the change as a
whole. Asking it again after every fix invites churn and second-guessing of a
decision already taken.

## How to run it

Spawn ONE fresh subagent. Do not perform this check yourself, for the same
reason you do not review your own code.

Give the subagent:

- The diff, and the commit range.
- The REQUIREMENT the change serves: the issue, the spec, or the user's
  request, in the user's own words where possible.
- The repository conventions, and where existing helpers live.
- The instruction to read the surrounding code, not the diff alone. A
  simplification usually depends on something that already exists.
- The instruction to report only. The subagent must not edit files.

## What the subagent must judge

Ask it these questions, in this order.

1. **Does every part trace to the requirement?** Take each file, type, flag,
   option and abstraction. Name the part of the requirement it serves. Anything
   that traces to nothing is the first candidate to delete.

2. **Does the repository, the standard library, or the language already do
   this?** Reimplementation is the most common source of avoidable code. Say
   what already exists and where.

3. **Would a smaller mechanism reach the same goal?** Compare against the
   simplest thing that could work. Name the smaller design, and say what it
   would cost.

4. **Is anything built for a need that has not arrived?** An interface with one
   implementation, a flag with one value, a parameter every caller passes the
   same way, a hook nobody calls. Speculative generality is the YAGNI case.

5. **Do the tests test the code, or the framework?** A test that restates the
   implementation, or that proves the language works, carries cost and catches
   nothing.

6. **What is the smallest change that satisfies the requirement?** State it,
   even when the answer is what was written.

## The rule that keeps this honest

**Do not propose a simpler alternative you have not checked against the real
failure modes.**

A smaller design that fails a requirement is not simpler. It is broken and
short. Before proposing a cut, find how the current code behaves under the
cases the requirement names, and show that the smaller version survives them.
If a prior review already proved a case, that case is evidence, and the
proposal must answer it.

The typical failure: a reviewer calls a long guard disproportionate and
proposes a short replacement that matches raw text, while an earlier review
already proved that a raw-text version fails on one input. The cheap
alternative fails the exact test the expensive one passes.

## Complexity that earns its place

Some complexity is correct, and this check must be able to say so.

Complexity earns its place when it carries a reason: an incident that happened,
a failure mode proven by a test, a boundary the platform depends on. Complexity
does not earn its place when it carries an expectation about the future.

Judge the reason, not the line count. Report "this is proportionate, and here
is why" as readily as a cut. Do NOT manufacture simplifications to look
useful. A check that always finds something is a check nobody can trust.

## The verdict

The subagent returns one of three:

- **SHIP AS IS.** The change is the smallest thing that meets the requirement,
  or its extra weight carries a stated reason.
- **SIMPLIFY FIRST.** Name each removal, the lines it saves, and the evidence
  that the requirement still holds without it.
- **QUESTION THE REQUIREMENT.** The change is a reasonable answer to the stated
  goal, but the goal itself looks unnecessary, already met, or far more
  expensive than the problem.

Every verdict names what it examined, so a reader can tell a real check from a
rubber stamp.

## Output

Report the verdict to the user as it came back, including a SHIP AS IS. The
reason a change is large is worth stating once, where a reader will find it.
What to do with the verdict is the caller's decision, not this skill's.
