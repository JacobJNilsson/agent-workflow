---
name: code-comments
description: Decides which code needs a comment and what that comment must answer, then checks each comment as a cold reader. TRIGGER when writing or reviewing code comments, doc comments, type or field comments, test fixtures, or test files, and when a review says a comment is unclear or a name needs explaining. Use with technical-writing, which governs the sentences.
---

# Code comments

The reader is a colleague who opens the file cold, months from now, with
no PR thread and no chat history. Every rule below serves that reader.
The `technical-writing` skill governs how a sentence reads. This skill
governs whether a comment exists and what it must contain.

## The test

Before a commit, read each new comment as the cold reader and ask two
questions. What is this for? When is it empty, absent, or skipped? If the
comment does not answer the question the reader will ask, it is not done.

One or two sentences is the norm. A longer comment is rare, and only a
file comment or a fixture comment earns one. The failure to watch for is
not length but a short comment that describes the data and skips the
purpose. Write the fact the reader needs first, then cut words, not
facts.

## What gets a comment

Comment these. Leave the rest alone.

- An exported type or field whose name does not say what it holds, when
  it is set, or when it is empty. Every optional field says when it is
  absent.
- A function whose name does not say what it returns. A function that
  returns a map says what the key is.
- A test fixture. Say what it builds and what the tests do with it. A
  fixture comment that lists the parts and skips the purpose fails the
  test above.
- A test file that checks one rule. State the rule once at the top, in
  the words the spec or the product uses. A reader must be able to say
  what the file tests without reading an assertion.
- A group of assertions in a test that together show one fact. One short
  line above the group saying what it shows.
- A guard, cap, limit, retry, timeout, or number. State the runtime
  reason it exists. If the reason is not known, find it before writing
  the comment. Never guess a reason.
- A coined word. When a name uses a word that is not in the codebase, the
  project glossary, or common use, define it once where it first appears
  or use a word that already exists. A word the author made up in one
  session is jargon to everyone else.

Do not comment these.

- What the next line does. The code shows it.
- A function whose name and body say what it does. Most functions.
- A fact another comment or the type already states.
- A case that cannot exist yet. A new field has no old data to be
  compatible with.
- A reason that answers a review. That belongs in the PR thread or the
  commit body, never in the code.

## What each kind must contain

- Type or field: what it holds, and when it is empty.
- Function: what it reads or returns, and the key of any map.
- Fixture: its shape, and what the tests do with it.
- Test file: the rule under test, and what happens when the rule is
  broken.
- Guard or number: the runtime reason, and what happens without it.
- TODO: a topic or a person in parentheses, and what remains. Never a
  ticket id. Tickets belong in commit messages and PR text.

## How to write it

- Say the state, not the mechanism that produced it. Name what a thing
  is, not the steps that made it.
- Say what a thing does, not how it feels. If a sentence cannot be
  restated as a fact, an instruction, or a number, cut it.
- One name per thing, across code, comments, and tests. When two words
  compete for one meaning, keep the one in wider use and replace the
  other.
- Plain words a contributor understands without looking them up. When a
  rare word fits exactly, still prefer the plain one.
- Active voice. Name the actor.
- No em-dashes, no semicolons. Split the sentence instead.
- Drop articles and lead-ins only where the sentence still reads one way.
- One thought per sentence. One or two sentences is the norm. A longer
  comment needs a fact the reader cannot get elsewhere, and even then
  only a file or fixture comment reaches a paragraph.
- A comment must agree with the code. When the code changes, the comment
  changes in the same commit or is deleted.
- A longer comment is stated once. When the same explanation is needed in
  two places, the code is asking to be refactored so that one place
  holds it. The other places point at that one by name, or say nothing.

## Review checklist

Apply to every comment a change adds or touches.

1. Does the comment answer what the thing is for?
2. Does it say when the thing is empty, absent, or skipped?
3. Does the file comment state the rule a test file checks?
4. Does every coined word have a definition or a replacement?
5. Does every guard or number carry its runtime reason?
6. Does any comment narrate the next line, repeat the type, or answer a
   review? Delete it.
7. Does the code contradict the comment? Fix one of them.
8. Does a longer comment appear twice? Keep one, and check whether the
   code should be refactored so that one place needs it.
9. Would a colleague say these words out loud?
