---
name: legible-code
description: Rules for code that a second reader can follow without the author. Use when writing or reviewing Go, tests, or a package API, and when a review says the code is hard to follow, hides its calls, names its mechanism, or has tests that are too long or use testify.
---

# Legible code

The reader is a colleague who opens the package cold. Every rule below
serves that reader. Apply them while writing, and check them in review.

## Words for these rules

These terms name a pattern in a few words. Use them in code, briefs, and
findings with the meaning below, and with no other meaning.

- **Deep module.** A package or type with a small public API over a lot of
  behaviour. A caller learns little and gets much.
- **Shallow module.** A package or type whose public API is about as large as
  the code behind it. A function that only passes its arguments on is the
  smallest case.
- **Single source of truth.** One place holds a fact, such as a word, a limit,
  or a rule. Every other place reads the fact from there.
- **Fake.** A stand-in for a real dependency in a test. A mock and a stub are
  fakes too.
- **Seam.** A field or a parameter where a test puts a fake in place of a real
  dependency. The constructor sets the real one.
- **Test-only door.** Code that exists only so that a test can reach private
  state.
- **Tautological test.** A test that takes its want from the code under test,
  so it passes whatever the code does.
- **Structure-sensitive test.** A test that fails when private code changes
  and nothing that a caller sees changes.
- **Drifted fake.** A fake that answers differently from the real dependency,
  so the test passes and the real run fails.

The `review-code` skill holds the probe for each kind of lying test.

## Tests show the calls

- A test body shows the package's public calls. `Write`, `Mark` and
  `Recompute` appear in the test, not inside a helper.
- A helper sets up, such as `setup(t)` that builds the store, the graph
  and the fakes. Checks stay in the test body, as the next section says.
  A helper that hides the call under test hides what the test proves.
- A test body holds the case, not the wiring. The database, the queue
  client, the worker and the log capture go in one setup helper that the
  file's tests share. The body states the inputs the case is about, makes
  the call and states the want.
- Two tests that repeat the same wiring lines mean the setup helper is
  missing. Write it with the second test.
- The error check sits on the line under the call it checks. The blank
  lines go before the call and after its error check.
- A test states its numbers. Three legs at 1.0 give 3.0 for their
  sequence. A reader checks that in their head.
- The want is written out where the test is, with the value of every field
  it compares. A helper that builds the want hides what the test proves,
  even when it saves lines.

## Tests check with the standard library

Go tests check results with the standard library and go-cmp. They do not
use testify.

- Check an error with `if err != nil { t.Fatalf("<call>: %s", err) }`.
  The message names the call that failed.
- Compare with
  `if d := cmp.Diff(want, got); d != "" { t.Fatalf("<what> diff (-want, +got):\n%s", d) }`.
  The message states the order of the diff.
- Assign before you check. The call under test assigns `got` and `err` on
  its own line. The want is a named variable. Never call a function
  inside an error check or inside `cmp.Diff`.
- Do not add testify to a test. In a file that uses testify, write each
  new or changed test with the standard library. Each change removes some
  testify, until the file has none.
- To compare JSON, decode the expected text into one value and the body
  into another. Decode each on its own line with its own error check.
  Then compare the two values with `cmp.Diff`. Do not write an assertion
  helper for it.

Before, the calls hide inside the assertions:

```go
require.NoError(t, store.Write(ctx, item))
assert.Equal(t, Item{ID: "a", Count: 3}, mustRead(t, store, "a"))
```

After, each call has its own line and each check names what it checks:

```go
err := store.Write(ctx, item)
if err != nil {
	t.Fatalf("Write: %s", err)
}

got, err := store.Read(ctx, "a")
if err != nil {
	t.Fatalf("Read: %s", err)
}
want := Item{ID: "a", Count: 3}
if d := cmp.Diff(want, got); d != "" {
	t.Fatalf("item diff (-want, +got):\n%s", d)
}
```

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
