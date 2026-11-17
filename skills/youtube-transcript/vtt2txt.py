#!/usr/bin/env python3
"""Convert a WebVTT subtitle file from yt-dlp to plain text.

Usage: vtt2txt.py FILE.vtt [--stamp SECONDS]

Without --stamp the output is one block of paragraphs. With --stamp N the
output starts a new paragraph about every N seconds and prefixes it with
[H:MM:SS] or [M:SS], so a quote can be located in the video.

Auto-generated captions repeat each line as the caption rolls. This script
drops a cue line that the previous cue already showed.
"""
import argparse
import html
import re
import sys

TIMING = re.compile(
    r"^(?:(\d+):)?(\d{2}):(\d{2})\.(\d{3})\s+-->\s+(?:(?:\d+:)?\d{2}:\d{2}\.\d{3})"
)
TAG = re.compile(r"<[^>]*>")


def start_seconds(match):
    hours, minutes, seconds = match.group(1), match.group(2), match.group(3)
    return int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds)


def clock(total):
    hours, rest = divmod(total, 3600)
    minutes, seconds = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def read_cues(text):
    """Return a list of (start_seconds, [clean lines]) for each cue."""
    cues = []
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        match = TIMING.match(line)
        if match:
            current = (start_seconds(match), [])
            cues.append(current)
            continue
        if current is None:
            continue  # header, NOTE and STYLE blocks come before the first cue
        if not raw.rstrip("\r\n"):
            current = None  # only an empty line ends a cue, a lone space does not
            continue
        clean = html.unescape(TAG.sub("", line)).strip()
        if clean:
            current[1].append(clean)
    return cues


def dedupe(cues):
    """Return (start, line) pairs without lines the previous cue showed."""
    out = []
    previous = []
    for start, lines in cues:
        for line in lines:
            if line not in previous:
                out.append((start, line))
        previous = lines
    return out


def paragraphs(pairs, stamp):
    if not stamp:
        return [" ".join(line for _, line in pairs)]
    result = []
    bucket = None
    words = []
    for start, line in pairs:
        if bucket is None or start - bucket >= stamp:
            if words:
                result.append(f"[{clock(bucket)}] " + " ".join(words))
            bucket, words = start, []
        words.append(line)
    if words:
        result.append(f"[{clock(bucket)}] " + " ".join(words))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("vtt")
    parser.add_argument("--stamp", type=int, default=0, metavar="SECONDS")
    args = parser.parse_args()
    with open(args.vtt, encoding="utf-8") as handle:
        text = handle.read().lstrip("﻿")
    pairs = dedupe(read_cues(text))
    if not pairs:
        sys.exit("no caption text found in " + args.vtt)
    print("\n\n".join(paragraphs(pairs, args.stamp)))


if __name__ == "__main__":
    main()
