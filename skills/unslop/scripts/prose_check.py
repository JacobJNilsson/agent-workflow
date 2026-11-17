#!/usr/bin/env python3
"""Find the mechanical AI tells in prose: the findings of the unslop skill that a script can see.

Usage: prose_check.py [--max-words N] <file>...   (use - for standard input)

Prints one line per finding as `path:line: [rule N] message`.
Code fences and inline code are skipped.
Exit code: 0 when clean, 1 when there are findings, 2 on a usage or read error.
The script cannot judge passive voice, rule of three, or tone. Read the text for those.
"""

import re
import sys

MAX_WORDS = 25

WORD_RULES = [
    (7, "AI vocabulary, use a plain word", r"additionally|crucial|delves?|enduring|enhance[sd]?|fostering|garner(?:s|ed)?|interplay|intricate|landscape|pivotal|showcas(?:e|es|ed|ing)|tapestry|testament|underscor(?:e|es|ed|ing)|vibrant"),
    (8, 'fancy way to say "is", write "is" or "has"', r"serves as|stands as|boasts"),
    (9, 'write the point directly instead of "not just X, but Y"', r"not just\b[^.!?]*\bbut\b"),
    (20, "chatbot phrase, delete it", r"i hope this helps|let me know if|certainly!|of course!|great question"),
    (23, "filler phrase, shorten or delete it", r"in order to|due to the fact that|it is important to note that"),
    (26, "abstract metaphor noun, use the concrete word", r"substrate|nexus|locus|vantage|bedrock|paradigm|north star|flywheel|endgame|gold-plating"),
    (31, "fancy word, use the plain one", r"utili[sz]e[sd]?|leverag(?:e|es|ed|ing)|facilitat(?:e|es|ed|ing)|numerous|in the event that"),
]
WORD_RULES = [(n, msg, re.compile(r"\b(?:" + pattern + r")\b", re.IGNORECASE)) for n, msg, pattern in WORD_RULES]

CHAR_RULES = [
    (13, "em dash, use a period or a comma", "—"),
    (13, "en dash, use a period or a comma", "–"),
    (13, "spaced hyphen used as a dash, use a period or a comma", " - "),
    (13, "spaced double hyphen used as a dash, use a period or a comma", " -- "),
    (0, "semicolon, write two sentences", ";"),
    (19, "curly quote, use a straight quote", "‘"),
    (19, "curly quote, use a straight quote", "’"),
    (19, "curly quote, use a straight quote", "“"),
    (19, "curly quote, use a straight quote", "”"),
]

EMOJI = re.compile("[\U0001F300-\U0001FAFF✅✨⭐✔❌]")
FENCE = re.compile(r"^\s*```")
INLINE_CODE = re.compile(r"`[^`\n]*`")
BLOCK_START = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|>|\|)")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def prose_lines(text):
    """Yield (line number, text) for each line outside a code fence, with inline code blanked."""
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, INLINE_CODE.sub("code", line)


def blocks(lines):
    """Group prose lines into blocks. A blank line, a list item, or a heading starts a new block."""
    current = []
    for number, line in lines:
        if not line.strip():
            if current:
                yield current
            current = []
        elif BLOCK_START.match(line) and current:
            yield current
            current = [(number, line)]
        else:
            current.append((number, line))
    if current:
        yield current


def check_text(text, max_words=MAX_WORDS):
    """Return the findings of one text as (line, rule, message) tuples, sorted by line."""
    findings = []
    lines = list(prose_lines(text))
    for number, line in lines:
        for rule, message, char in CHAR_RULES:
            # A list marker at the start of the line is not a dash.
            if char in line.lstrip():
                findings.append((number, rule, message))
        for rule, message, pattern in WORD_RULES:
            for hit in pattern.finditer(line):
                findings.append((number, rule, f"{message}: {hit.group(0)!r}"))
        if EMOJI.search(line):
            findings.append((number, 18, "decorative emoji, remove it"))
    for block in blocks(lines):
        start = block[0][0]
        joined = " ".join(line.strip() for _, line in block)
        if joined.startswith("|"):
            # A table row: each cell is its own text, and a separator row has none.
            cells = [c for c in joined.strip("|").split("|") if c.strip(" :-")]
        else:
            cells = [joined]
        for sentence in (s for cell in cells for s in SENTENCE_END.split(cell)):
            words = len(sentence.split())
            if words > max_words:
                findings.append((start, 28, f"sentence has {words} words, the limit is {max_words}: {sentence[:60]!r}"))
    return sorted(findings)


def format_finding(path, finding):
    line, rule, message = finding
    label = f"rule {rule}" if rule else "technical-writing"
    return f"{path}:{line}: [{label}] {message}"


def main(argv):
    max_words = MAX_WORDS
    args = list(argv)
    if args[:1] == ["--max-words"] and len(args) >= 2 and args[1].isdigit():
        max_words = int(args[1])
        args = args[2:]
    if not args or args[0].startswith("-") and args[0] != "-":
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: prose_check.py [--max-words N] <file>...", file=sys.stderr)
        return 2
    total = 0
    for path in args:
        try:
            text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError) as error:
            print(f"prose_check: cannot read {path}: {error}", file=sys.stderr)
            return 2
        for finding in check_text(text, max_words):
            print(format_finding(path, finding))
            total += 1
    if total:
        print(f"{total} finding(s). Fix them, then run the script again.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
