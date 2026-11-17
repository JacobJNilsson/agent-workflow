#!/usr/bin/env python3
"""Check a commit message against the commit-message skill rules that a script can see.

Usage: check_commit.py <message-file>   (use - for standard input)

Prints one line per finding as `line N: message`. A line that starts with `note:`
is advice and does not change the exit code.
Exit code: 0 when clean, 1 when there are findings, 2 on a usage or read error.
The script cannot judge the why, the audience test, or the voice. Read the message for those.
"""

import re
import sys

TYPES = "feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert"
SUBJECT = re.compile(rf"^(?:{TYPES})(?:\([^)\s]+\))?!?: (?P<description>\S.*)$")
MAX_SUBJECT = 72
MAX_WORDS = 25
NOT_IMPERATIVE = re.compile(r"^(?:\w+(?:ed|ing)|adds|fixes|removes|updates|changes|uses|makes|moves)$", re.IGNORECASE)
IMPERATIVE_EXCEPTIONS = {"embed", "speed", "bed", "feed", "seed", "need", "proceed", "succeed", "exceed", "bring", "string", "ping", "swing"}
BODY_RULES = [
    ("em dash, use a period or a comma", re.compile("—")),
    ("en dash, use a period or a comma", re.compile("–")),
    ("semicolon, write two sentences", re.compile(";")),
    ("curly quote, use a straight quote", re.compile("[‘’“”]")),
    ("attribution line, remove it", re.compile(r"co-authored-by|generated with|\U0001F916", re.IGNORECASE)),
]
TRAILER = re.compile(r"^(?:BREAKING CHANGE|Closes|Fixes|Refs|Signed-off-by)\b", re.IGNORECASE)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
INLINE_CODE = re.compile(r"`[^`\n]*`")


def check_subject(subject):
    findings = []
    match = SUBJECT.match(subject)
    if not match:
        findings.append((1, f"subject must start with `<type>[scope]: <description>`, with a type from: {TYPES.replace('|', ', ')}"))
        return findings, []
    description = match.group("description")
    if not description[0].isupper():
        findings.append((1, "the description must start with a capital letter"))
    if subject.rstrip().endswith("."):
        findings.append((1, "the subject must not end with a period"))
    if len(subject) > MAX_SUBJECT:
        findings.append((1, f"the subject has {len(subject)} characters, the limit is {MAX_SUBJECT}"))
    notes = []
    first = description.split()[0]
    if NOT_IMPERATIVE.match(first) and first.lower() not in IMPERATIVE_EXCEPTIONS:
        notes.append((1, f"{first!r} may not be imperative. Write 'Add', not 'Added' or 'Adds'"))
    return findings, notes


def body_sentences(lines):
    """Yield (line number, sentence) for the prose of the body."""
    block, start = [], 0

    def flush():
        if block:
            text = INLINE_CODE.sub("code", " ".join(block))
            for sentence in SENTENCE_END.split(text):
                yield start, sentence

    for number, line in lines:
        if not line.strip() or TRAILER.match(line):
            yield from flush()
            block = []
        elif LIST_ITEM.match(line):
            yield from flush()
            block, start = [line.strip()], number
        else:
            if not block:
                start = number
            block.append(line.strip())
    yield from flush()


def check_message(message):
    """Return (findings, notes) as lists of (line number, text)."""
    lines = message.rstrip("\n").split("\n")
    if not message.strip():
        return [(1, "the message is empty")], []
    findings, notes = check_subject(lines[0])
    if len(lines) > 1 and lines[1].strip():
        findings.append((2, "leave a blank line between the subject and the body"))
    if len(lines) == 1 or not "\n".join(lines[1:]).strip():
        notes.append((1, "no body. Add the why unless the subject says it all"))
    for number, line in enumerate(lines, start=1):
        for text, pattern in BODY_RULES:
            if pattern.search(line):
                findings.append((number, text))
    numbered = list(enumerate(lines, start=1))[1:]
    for number, sentence in body_sentences(numbered):
        words = len(sentence.split())
        if words > MAX_WORDS:
            findings.append((number, f"sentence has {words} words, the limit is {MAX_WORDS}: {sentence[:50]!r}"))
    return sorted(findings), sorted(notes)


def main(argv):
    if len(argv) != 1 or (argv[0].startswith("-") and argv[0] != "-"):
        print("usage: check_commit.py <message-file>", file=sys.stderr)
        return 2
    try:
        text = sys.stdin.read() if argv[0] == "-" else open(argv[0], encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as error:
        print(f"check_commit: cannot read {argv[0]}: {error}", file=sys.stderr)
        return 2
    findings, notes = check_message(text)
    for number, text in findings:
        print(f"line {number}: {text}")
    for number, text in notes:
        print(f"note: line {number}: {text}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
