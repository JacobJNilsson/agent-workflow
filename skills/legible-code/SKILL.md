---
name: legible-code
description: Rules for code that a second reader can follow without the author. Use when writing or reviewing Go, tests, or a package API, and when a review says the code is hard to follow, hides its calls, or names its mechanism.
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
- One word per concept across the package. When two words compete,
  count them, keep the one in wider use, and replace the other.
- A comment states a fact the code does not show. It does not narrate,
  and it does not describe the mechanism where the state will do.
