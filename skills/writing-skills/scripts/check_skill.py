#!/usr/bin/env python3
"""Lint skill folders against the rules in writing-skills.

Usage: check_skill.py <skill-folder>...

Prints one line per finding as `<folder>: <message>`. Exits with 1 when any
folder has a finding, and with 0 when all are clean.
"""

import re
import sys
from pathlib import Path

MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_LINES = 500
RESERVED_WORDS = ("anthropic", "claude")
NAME_PATTERN = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
TRIGGER_PATTERN = re.compile(
    r"\bTRIGGER\b|\b(?i:use (when|for|before|at|after|whenever))\b"
)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BACKTICK_PATH = re.compile(r"`((?:scripts|references|assets)/[^`\s]+)`")


def parse_frontmatter(text):
    """Return (fields, error). Handles `key: value`, quoted values, and
    indented continuation lines, including `>` and `|` blocks."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "SKILL.md does not start with a --- frontmatter block"
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, "frontmatter has no closing ---"
    fields = {}
    key = None
    for line in lines[1:end]:
        match = re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match and not line[0].isspace():
            key = match.group(1)
            value = match.group(2).strip()
            fields[key] = "" if value in (">", "|", ">-", "|-") else value
        elif key is not None and line.strip():
            fields[key] = (fields[key] + " " + line.strip()).strip()
    for name, value in fields.items():
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            fields[name] = value[1:-1]
    return fields, None


def linked_paths(body):
    paths = []
    for target in MARKDOWN_LINK.findall(body):
        if re.match(r"[a-z][a-z0-9+.-]*:", target) or target.startswith(("#", "/")):
            continue
        paths.append(target.split("#")[0])
    paths.extend(BACKTICK_PATH.findall(body))
    return [p for p in dict.fromkeys(paths) if p and "<" not in p and "*" not in p]


def check_skill(folder):
    """Return the list of findings for one skill folder."""
    folder = Path(folder)
    skill_file = folder / "SKILL.md"
    if not skill_file.is_file():
        return ["SKILL.md is missing"]
    text = skill_file.read_text(encoding="utf-8")
    fields, error = parse_frontmatter(text)
    if error:
        return [error]

    findings = []
    name = fields.get("name", "")
    if not name:
        findings.append("frontmatter has no name")
    else:
        if name != folder.resolve().name:
            findings.append(f"name '{name}' does not match the folder '{folder.resolve().name}'")
        if len(name) > MAX_NAME:
            findings.append(f"name is {len(name)} characters, the limit is {MAX_NAME}")
        if not NAME_PATTERN.fullmatch(name):
            findings.append("name must use lowercase letters, digits, and single hyphens")
        for word in RESERVED_WORDS:
            if word in name:
                findings.append(f"name contains the reserved word '{word}'")

    description = fields.get("description", "")
    if not description:
        findings.append("frontmatter has no description")
    else:
        if len(description) > MAX_DESCRIPTION:
            findings.append(
                f"description is {len(description)} characters, the limit is {MAX_DESCRIPTION}"
            )
        if "<" in description or ">" in description:
            findings.append("description contains < or >, which the platform rejects as XML tags")
        if not TRIGGER_PATTERN.search(description):
            findings.append(
                "description does not say when to use the skill: add 'Use when ...' or 'TRIGGER when ...'"
            )

    line_count = len(text.splitlines())
    if line_count > MAX_LINES:
        findings.append(f"SKILL.md has {line_count} lines, the limit is {MAX_LINES}")

    for path in linked_paths(text):
        if not (folder / path).exists():
            findings.append(f"SKILL.md names '{path}', which does not exist")
    return findings


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    failed = False
    for arg in argv:
        folder = Path(arg)
        findings = check_skill(folder) if folder.is_dir() else [f"{arg} is not a folder"]
        label = str(folder).rstrip("/")
        if findings:
            failed = True
            for finding in findings:
                print(f"{label}: {finding}")
        else:
            print(f"{label}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
