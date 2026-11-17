"""Graders for eval checks. Each grader is a plain function of the graded text.

A grader returns (ok, detail). The detail says what failed, so a failing
case can be debugged without a rerun. No grader calls a model.
"""

import re
import subprocess

FENCE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
INLINE_CODE = re.compile(r"`[^`\n]*`")
BLOCK_START = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|>)")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def sentences(text):
    """Split prose into sentences. Code fences and inline code do not count."""
    text = FENCE.sub("", text)
    text = INLINE_CODE.sub("code", text)
    blocks, current = [], []
    for line in text.splitlines():
        if not line.strip():
            blocks.append(" ".join(current))
            current = []
        elif BLOCK_START.match(line) and current:
            blocks.append(" ".join(current))
            current = [line.strip()]
        else:
            current.append(line.strip())
    blocks.append(" ".join(current))
    found = []
    for block in blocks:
        found.extend(s for s in SENTENCE_END.split(block) if s.strip())
    return found


def _flags(spec):
    flags = re.MULTILINE
    if "i" in spec.get("flags", ""):
        flags |= re.IGNORECASE
    return flags


def matches(text, spec):
    ok = re.search(spec["pattern"], text, _flags(spec)) is not None
    return ok, "" if ok else f"no match for /{spec['pattern']}/"


def not_matches(text, spec):
    hit = re.search(spec["pattern"], text, _flags(spec))
    return hit is None, "" if hit is None else f"found {hit.group(0)!r}"


def max_sentence_words(text, spec):
    limit = spec["limit"]
    too_long = [s for s in sentences(text) if len(s.split()) > limit]
    if not too_long:
        return True, ""
    return False, f"{len(too_long)} sentence(s) over {limit} words, first: {too_long[0][:80]!r}"


def max_first_line(text, spec):
    first = text.splitlines()[0] if text.strip() else ""
    ok = len(first) <= spec["limit"]
    return ok, "" if ok else f"first line has {len(first)} characters"


def min_words(text, spec):
    count = len(text.split())
    return count >= spec["limit"], f"{count} words"


def command(text, spec):
    """Run a shell command in the run directory. Exit code 0 passes."""
    done = subprocess.run(
        spec["cmd"], shell=True, cwd=spec["cwd"], capture_output=True, text=True, timeout=60
    )
    return done.returncode == 0, (done.stdout + done.stderr).strip()[:200]


GRADERS = {
    "matches": matches,
    "not_matches": not_matches,
    "max_sentence_words": max_sentence_words,
    "max_first_line": max_first_line,
    "min_words": min_words,
    "command": command,
}


def grade(text, spec):
    return GRADERS[spec["type"]](text, spec)
