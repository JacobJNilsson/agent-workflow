---
name: review-code
description: Use when asked to review, check, or look over code, a diff, a commit range, or a PR, and when a change is ready for review. Also use when asked whether a change is over-built, needed at all, or could be smaller.
---

# Review code

You review code against three things: the task it claims to satisfy, the
repo's own rules, and the tests that cover it. You also judge its size. Could
less code, with fewer names that other packages can see, reach the same goal?
You report what you find. You do not fix it.

## Read before you judge

1. The repo rules: `AGENTS.md`, `REVIEW.md`, `STYLEGUIDE.md`, and anything
   they point to. `REVIEW.md` holds the rules that a reviewer checks in this
   repo. A finding that contradicts a repo rule is real. A finding that
   ignores one is noise.
2. The task or spec the change claims to satisfy.
3. The diff. For a PR, review the local branch. What GitHub shows is stale once
   anyone pushes.
4. The code around the diff, and every caller of what the diff adds. Most cuts
   depend on code that already exists, so you have to read it.
5. The tests over the changed code. Run them if you can. Then read each test
   the change adds as a colleague who opens the file cold, against the test
   rules of the `legible-code` skill. Those rules count as repo rules. Check
   each test that the change adds or changes for the three kinds of lying
   test in "Find the tests that lie". Wiring that repeats across test bodies
   is a finding.

## What counts as a finding

Report only problems this change caused, or made reachable. Each finding needs
proof from the code: the file and line, a failing test or a reproduction, or a
contradiction with a stated contract.

Drop anything you cannot support:

- A style preference the repo does not rule on.
- A risk in code this change did not touch.
- A restatement of what a linter or type checker can tell you.

Do not ask for defensive code. A coding agent fixes every finding it gets, so a
request for a guard leaves behind code that guards against nothing. These are
not findings:

- A guard for input that no caller can produce.
- Error handling for a state that the types or the data model rule out.
- A second check of a value that the code upstream already checked.
- A test for a path that this change did not create or change.
- A rename, a split, or a move that the repo rules do not ask for.

If you believe a caller can produce the input, name the caller. Then it is a
finding.

The list above covers requests that add code or move it. A request to delete
code, or to unexport a name, is a size finding. The next section covers those.

## Find the tests that lie

A green test can lie. It passes, and it would still pass if the code were
wrong. Check each test that the change adds or changes for the three kinds
below. Each one is a `concern`. Name the kind in the finding, and give the
probe that proves it. The `legible-code` skill defines the names.

### A tautological test restates the code

The test takes its want from the code under test. It copies a literal from
the code, or it builds the want with the function that the code uses. A wrong
rule then passes, because the test copies the mistake.

Probe: make the code wrong in a way the spec forbids, and keep the copied part
the same. If the test still passes, it is tautological.

Example: a function builds a prompt from a template file. The test reads the
same file and checks that the prompt contains each phrase of the file.

```go
func BuildPrompt() string { return readTemplate("main.md") }

func TestBuildPromptHasRules(t *testing.T) {
	got := BuildPrompt()
	for _, phrase := range strings.Split(readTemplate("main.md"), "\n") {
		if !strings.Contains(got, phrase) {
			t.Errorf("prompt lacks %q", phrase)
		}
	}
}
```

The want comes from the template, and the code returns the template. If
someone adds "Merge by hand on Fridays" to `main.md`, the test still passes.

Fix: take the want from the spec or the task. A test may pin exact words when
a spec or a decision record names them as the contract. Then the test name
says so.

### A structure-sensitive test checks how, not what

The test fails when private code changes and nothing that a caller sees
changes. It counts calls to private functions, reads private fields, walks a
type with reflection, or matches source text.

Probe: picture a refactor that keeps every result a caller can see. If the
test fails under that refactor, it is structure-sensitive.

Example: this test comes from a rejected first version of a change. It walks
every field of `Task` with reflection to prove that an edit keeps the task's
state.

```go
func TestEditKeepsState(t *testing.T) {
	before := Task{Name: "a", State: Running}
	after := Edit(before, "b")
	v := reflect.ValueOf(after)
	for i := 0; i < v.NumField(); i++ {
		name := v.Type().Field(i).Name
		if name != "Name" && !reflect.DeepEqual(
			v.Field(i).Interface(),
			reflect.ValueOf(before).Field(i).Interface()) {
			t.Errorf("field %s changed", name)
		}
	}
}
```

The test reads the layout of the type, not the result of the edit. A new
private field or a renamed one breaks it, and no caller sees a change. The
fix compares whole values:
`want := Task{Name: "b", State: Running}` and `if after != want`.

Fix: assert on what the public call returns, stores, or sends. A call to a
fake counts as a result only when the call is the effect, such as a request
to another service.

### A test with a drifted fake cannot fail

The test runs against a fake that answers differently from the real
dependency. The test passes, and the real run fails.

Probe: for each fake that the test uses, name what the real dependency does in
the same case. Point at its docs, a recorded response, or a live run. If
nobody can name it, the fake is a guess.

Example: a tool reads a verdict that an agent reports through a command. The
test drives a fake agent.

```go
func fakeAgent(t *testing.T, bin string) {
	// Calls the tool with plain arguments, outside any sandbox.
	exec.Command(bin, "report", "done", "looks good").Run()
}
```

The real agent runs inside a sandbox. It sent its verdict through a
here-document, and the sandbox blocked the call before it reached the tool.
The test passed the whole time, because the fake never met the sandbox.

Fix: copy the fake's answers from the dependency's docs or from a recorded
response, and say which in the fake's comment. When the case depends on the
environment, such as a sandbox, run the test in that environment. If you
cannot, say so in the report.

A test with no assertion cannot fail either. It raises the coverage and
proves nothing. Report it as a `concern` too.

## Judge the size

An exported name shows up in the package docs and in autocomplete, so the next
person or agent has to read it to know whether they need it. Once another
package calls it, it cannot change without a change to that caller too. An
option that every caller sets the same way still needs a test and a line in the
docs. A full review judges the size of the whole change. A fix check judges
the size of the fix diff only.

### List what the change adds

Before you judge, list every one of these that the diff adds, or makes visible
to more code:

- An exported function, type, method, constant, or variable.
- An exported field on a type.
- A package, module, or file.
- A flag, a setting, an environment variable, or an option on a function.
- A parameter on an existing function.
- An endpoint, a command, or a message type.
- An interface or an abstract type.
- A dependency.

For each one, search the repo and count the callers outside its own package and
outside the tests. Put the list in the report as a table:

| Added | Where | Callers outside the package | Cut |
| --- | --- | --- | --- |
| `func ParseRow` | `ingest/row.go:14` | 0 | unexport |
| package `ingest/rowutil` | `ingest/rowutil/` | 1, `ingest` | fold into `ingest` |
| option `WithRetries` | `client/client.go:40` | 2, both pass 3 | delete, use 3 |

If a row has no cut, say why the item stays. Leave no row out. A table with
fewer rows than the diff adds is a review that did not look.

### Apply the cuts

Each pattern below is a finding, unless you can state a reason to keep the code:

- **No caller outside the package.** Unexport it.
- **Exported only so a test can reach it.** Unexport it, and test through the
  API that real callers use.
- **A package or a file with one importer.** Fold it into the importer.
- **An option or a parameter that every caller sets to the same value.** Delete
  it and use the value.
- **An interface with one implementation and no second one in the task.**
  Delete the interface and use the type.
- **A function that only passes its arguments to another function.** Delete it
  and call the other function.
- **A type that only wraps another type.** Use the other type.
- **Code that the repo, a dependency, the standard library, or the language
  already provides.** Delete it, and name what exists and where.
- **Something that no part of the task needs.** Delete it. This includes flags,
  hooks, and extension points for a need that has not come up.
- **A second step that could happen inside a step that already runs.** Move it
  into that step. A flag set inside the write that creates the row needs no
  second call, and no repair job for a crash between the two calls.
- **Memory that grows with the data and has no limit.** A cache with no
  capacity, or a list kept for the life of the process. Say how large the real
  data is.
- **A test that proves the framework or the language works.** Delete it.

Then state the smallest change that satisfies the task, in two or three
sentences. If that is the change you were given, say so.

### Find what the change left unused

A change often leaves old code that nothing uses any more. Nothing fails, so the
tests pass and the code stays. In one change, new code replaced a module of six
functions. Two reviews passed the change, and neither saw that nothing called
the module any more.

Look at the code the change touched and the code next to it: callers, callees,
tests, flags, configuration, state fields, docs, and agent instructions. Ask:

1. Does a function, type, or file lose its last caller?
2. Does a flag, option, or parameter now always get the same value?
3. Does a branch, fallback, or guard handle a case the change made impossible?
4. Do two paths now do the same thing?
5. Does a test check behaviour that the change removed?
6. Does a doc or comment describe behaviour the code no longer has?

Each yes is a finding, and the fix deletes the code. To prove it, search the
whole repo for callers, including other build tags, generated code, and scripts.
The deletion must not change anything a user or a test can see.

Code that was already unused before this change is not a finding. List it at the
end of the report under `Unused before this change`, with its path.

### Check each cut against the task

A smaller design that fails the task is broken, not simpler. For each cut, name
the cases in the task and the tests that the smaller version must pass, and
show that it passes them. If an earlier review or a test proved a case, the cut
must still pass that case.

Keep complexity that has a reason behind it: an incident, a failure that a test
proves, or a boundary that other code depends on. A guess about future needs is
not a reason. When you keep something large, say why in its table row.

## Check a fix

A fix check gets the findings that a fix answers, and the diff of that fix.
It answers three questions:

1. Does the fix resolve each finding? Give the proof, as for a finding.
2. Does the fix add a defect? Report it as a finding.
3. Does the fix make the code bigger than it needs to be? Run the size check
   on the fix diff: list what the fix adds, apply the cuts, and look for code
   that the fix left unused.

Leave the rest of the change alone, because a full review already judged it.
Report a finding outside the fix diff only when the fix caused it. One example
is a function whose last caller the fix deleted.

## Severity

| Level | Meaning |
| --- | --- |
| `critical` | Wrong behaviour, data loss, a security hole, or a broken contract. |
| `concern` | A real defect, a missing test on a path this change introduced, a lying test, a size cut, or code the change left unused. |
| `nit` | Small and optional. Say what improves and why. |

Size cuts and unused code are concerns, not nits. The review loop never fixes a
nit, so a cut filed as a nit reaches the author unfixed.

## Verdict

End with one line:

- `Request changes` when a critical or concern item stands.
- `Approve with nits` when only nits stand.
- `Approve` when nothing stands.
- `Needs discussion` when the finding is a product or scope decision for the
  engineer, not a defect to fix. Use it when the task itself looks unneeded,
  already done, or far more expensive than the problem it solves.

## Reporting

Start with the size table. Then group the findings by severity, most severe
first. For each finding give the file and line, what is wrong, the proof, and
the smallest fix you would accept. For a size cut, also say how many lines it
deletes.

Do not describe the code that is correct. A part of the change with no finding
needs no report.

Leave prose alone. Do not grade comments, commit messages, or docs wording.
Flag a comment or a doc only when it states something false about the code.

Say what you did not check, and why. A review that skipped the database layer is
not a clean review of the database layer.

## Related skills

- `review-pr` runs this skill against a GitHub PR and stages the findings as a
  pending review.
- `review-loop` runs this skill repeatedly with fixes in between. The loop owns
  the mechanics. This skill owns the judgement.
