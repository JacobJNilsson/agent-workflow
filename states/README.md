# States

A workflow written as prose drifts. The steps change, a loop loses its cap, a
state appears in the diagram and never in the text. The agent reads the prose
and never notices.

A declaration is the same workflow as a small machine. The prose stays the
thing an agent reads. The declaration is the thing a check can read. This
directory holds the format and the check. It does not run anything.

## A declaration

One line per state, one per edge. State names are lowercase words. A value
with a space is quoted.

```states
prose ../../skills/way-of-working/SKILL.md

entry spec
entry review

state spec      waits=human     cap=5
state implement waits=worker
state done      waits=none      terminal

spec -> implement when="the author approves the spec"   human
spec -> spec      when="the author sends the spec back"  human  cap=5
implement -> done  when="the work shipped"
```

| Part | Meaning |
| --- | --- |
| `prose <path>` | The file that explains this workflow. Checked for drift |
| `entry <state>` | Where work can start. More than one is normal, because a review can start at the review |
| `state <name> waits=<who>` | A place where work waits. `who` is a human, a worker, a reviewer, an author, or none |
| `cap=<n>` | On a state or an edge. The loop through it runs at most n times |
| `terminal` | The state has no way out, and it is an ending |
| `<a> -> <b> when="<clause>"` | One way the machine moves |
| `human` | The edge needs a person to cross it. An agent must stop and ask |

`waits=human` marks the states where the machine stops for you. Every other
state is one an agent can run alone. That distinction is what a state machine
buys: the mechanical states run without you, and the rest hand back.

## The checks

Run:

```bash
node states/validate-states.mjs states/declarations/way-of-working.states
node states/test.mjs
```

| Check | Catches |
| --- | --- |
| syntax | A line nobody can read, or a misspelled key |
| target exists | An edge into a state nobody declared |
| no dead end | A state with no way out |
| has terminal | A machine that never finishes |
| cycle has cap | A loop that can run forever |
| reachable | A state no entry can reach |
| in prose | A state in the machine that the prose never mentions |

The last one is the reason this exists. Every other check catches a broken
machine. That one catches a machine and a document that have drifted apart.

## Two declarations to read

`declarations/sketch.states` is the first hand sketch of the workflow. The
validator rejects it six times, and every rejection is a real defect: no ending,
three uncapped loops, and two states the prose never mentions.

`declarations/way-of-working.states` is the same workflow after the changes
those rejections asked for. It passes.

## What this does not do

It does not run the workflow. Pi runs the mechanical states with subagents and
hands back at every `waits=human` state, and that runner is pi's job, not this
directory's. The declaration is the contract both sides read.
