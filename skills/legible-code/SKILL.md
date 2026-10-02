---
name: legible-code
description: Rules for code that a second reader can follow without the author. Use when writing or reviewing Go, tests, or a package API, and when a review says the code is hard to follow, hides its calls, names its mechanism, or has tests that are too long.
---

# Legible code

The reader is a colleague who opens the package cold. Every rule below
serves that reader. Apply them while writing, and check them in review.

## Tests show the calls

- A test body shows the package's public calls. `Write`, `Mark` and
  `Recompute` appear in the test, not inside a helper.
- Helpers do two things: set up (`setup(t)` that builds the store, the
  graph and the fakes) and assert. A helper that hides the call under
  test hides what the test proves.
- A test states its numbers. Three legs at 1.0 give 3.0 for their
  sequence. A reader checks that in their head.
- The want is written out where the test is, with the value of every field
  it compares. A helper that builds the want hides what the test proves,
  even when it saves lines.

## A test proves one fact

- Name the fact in one sentence before you write the test, and make that
  sentence the test's name. If another test checks the fact through the
  same code, do not write a second test.
- Check a fact in the layer that produces it. A test of the domain layer
  checks the numbers and the requests sent to other services. A test
  through the HTTP API checks what the handler adds: the status, the
  error code, the fields in the response, and how many calls one request
  makes. It does not check again what the domain test checks.
- Compare only the fields the test is about. Skip the rest with the
  comparison library's ignore option, such as `cmpopts.IgnoreFields`,
  not with a helper. A footprint test does not spell out every leg.
- Do not test what the type rules out. A struct with no field for a
  nested value needs no test that nothing nests.
- Put a rule with many cases in a table. Each row states its input and
  its expected result. A row does not leave a field at zero for the loop
  to turn into a default.
- A test longer than about 40 lines gets a second look: fields it is not
  about, setup that a recipe could build, or two facts in one test. The
  number is a reason to look again, not a limit.

## No test-only doors

- Do not add setters in an `export_test.go` file to reach a cap, an age
  or a limit. Make the type configurable. Zero means the default.
- A limit a caller may want, such as how many items one run handles,
  is a parameter of the method, not a hidden field.

## Errors are values

- Never parse the text of an error. Match with `errors.Is` or `errors.As`.
  If a value must travel, carry it in the error type or beside it.
- Do not strip or rewrite an error's text for storage or logs. Store
  the value you need, or store nothing.

## Names say the effect

- A public name says what the caller gets. `RecomputeUntilDone`, not
  `Drain`. `Footprints`, not `Prices`.
- No abbreviations in SQL columns, identifiers, JSON fields, or enum
  values. `share_basis_points`, not `share_bp`. `coefficient`, not
  `coeff`. The accepted short forms stay: `ctx`, `tx`, `err`, `id`, and
  `i` in a loop.
- One word per concept across the package. When two words compete,
  count them, keep the one in wider use, and replace the other.
- A comment states a fact the code does not show. It does not narrate,
  and it does not describe the mechanism where the state will do.
