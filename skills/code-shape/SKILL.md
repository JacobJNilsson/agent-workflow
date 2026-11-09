---
name: code-shape
description: Use when a spec is settled and before the first implementation brief, when a fix or a feature needs new functions or packages, and when the user asks which functions, packages, or tests a change needs.
---

# Code shape

Sketch the shape of a change before anyone writes it. The sketch names the
functions and types the change needs, the package each one lives in, the calls
between them, and the tests that prove the change. It has no function bodies.
Settle the shape in short rounds, then hand it to the implementation agents as
their target.

## Scale the effort to the change

Two signals set the size: the number of new exported names, and whether the
change needs a new package. An exported name is one that code outside its
package calls.

| Size | Signal | Sketch | Who approves |
| --- | --- | --- | --- |
| Trivial | No new exported names | None. The brief names the function to change and the test to add. | Nobody |
| Small | A few new functions in existing packages | One round | You, and you show the sketch to the user with the brief summary |
| Large | A new package, or a flow that crosses packages | Rounds until the user approves | The user |

When a small sketch grows a new package, treat it as large.

## Sketch the functions first

1. Start at the entry point: the handler, command, job, or event that starts
   the behaviour.
2. Walk the spec's flow in order. Write each step as a function signature with
   a one-line contract: what it takes, what it returns, and how it fails.
3. Mark each function as `+` new, `~` changed, or `=` existing and unchanged.
4. Add the types that the signatures need. List the fields of a new type.

Leave the packages open for now, so the existing layout does not decide the
design.

## Reuse before you add

For each new function, search the repo for one that already does the job.
Search by behaviour, not only by name. When the search spans more than a few
packages, send it to an Explore agent on the fast tier. Reuse an existing
function over a new one. Mark a reused function as `=`, or as `~` when it needs
a change.

## Place the functions in packages

Group the functions by the data they work on and by who calls them. Put a group
in an existing package when it fits that package's purpose. Otherwise, propose
a new package and state its purpose in one sentence. Write down which package
calls which. A cycle means a group is in the wrong package.

## Propose the tests

List the tests with the sketch. Each test names the function it calls, the
situation it sets up, and the result it expects. Choose tests that prove the
spec. A test for every code path costs time and proves nothing extra.

- Write one test for each behaviour that the spec states.
- Write one test for each failure that a user or a caller would notice.
- For a bug fix, write the regression test that fails against the unfixed
  code.
- Skip a test for a branch that only passes an error on, and for a state that
  no caller can reach.

Prefer a test of an exported function over a test of a private helper. That
test still holds when the implementation splits the function into other
helpers.

## Check the sketch

- Each function does one job, and its name says that job.
- The change adds as few exported names as it can.
- The calls read top-down from the entry point.
- No package depends on a package that depends on it.
- Each behaviour in the spec has at least one test.

## Write it by hand

Write the sketch as a plain listing in chat, not as stub code. The listing
works for any language:

```
package billing (existing)
  + Invoice(ctx, orderID) (Invoice, error)   builds an invoice from a paid order
  ~ Total(lines) Money                       now includes VAT
package vatrate (new): looks up the VAT rate for a country on a date
  + Rate(country, date) (Rate, error)        fails with ErrUnknownCountry
calls: api.Pay -> billing.Invoice -> vatrate.Rate

tests
  billing.Invoice: a paid order with two lines gives an invoice with VAT on each line
  billing.Invoice: an unpaid order fails with ErrNotPaid
  vatrate.Rate: a date before a rate change gives the old rate
```

## Iterate in short rounds

Show the sketch, take the corrections, and redo only the parts they touch. Keep
each round to one listing and one set of corrections. Stop when the sketch
passes the checks and the approver from the size table agrees. A correction
that moves product behaviour goes to the spec first.

## Hand the sketch to the implementation

Paste the sketch into every implementation brief as the target shape. The
exported signatures bind the implementation agent, the same way the spec does.
The agent may split any function into private helpers, and may name and
arrange those helpers freely. An agent that needs a different exported
signature, a new exported name, or a different package reports it with its
suggestion. You decide, together with the user when the sketch was large.

The proposed tests are the minimum. The agent adds a test when the code shows a
case that the sketch missed.

A reviewer judges the implementation against the sketch. The reviewer flags an
exported signature that changed without a report.
