#!/usr/bin/env python3
"""Run a skill's eval cases with the old and the new skill, and report pass rates.

Usage:
  evals/run.py run <skill> [--runs 3] [--old-ref main] [--case ID] [-j 4]
  evals/run.py report <skill>

The runner copies the skill into a fresh temp directory, runs `claude -p` there
with the fast tier model, and grades the output with scripts (see graders.py).
Every `claude -p` call is appended to results/ledger.tsv, and the runner stops
before it passes the call limit.
"""

import argparse
import concurrent.futures
import datetime
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
from pathlib import Path

import graders

EVALS = Path(__file__).resolve().parent
ROOT = EVALS.parent
RESULTS = EVALS / "results"
LEDGER = RESULTS / "ledger.tsv"
CALL_LIMIT = 200
RUN_TIMEOUT_SECONDS = 300
ARMS = ("old", "new")
ledger_lock = threading.Lock()


def fast_model():
    """Read the fast tier model from config/models.env."""
    for line in (ROOT / "config" / "models.env").read_text().splitlines():
        if line.startswith("AGENT_MODEL_FAST="):
            return line.split("=", 1)[1].strip()
    sys.exit("config/models.env has no AGENT_MODEL_FAST")


def ledger_count():
    if not LEDGER.exists():
        return 0
    return max(0, len(LEDGER.read_text().splitlines()) - 1)


def ledger_add(skill, arm, case, run):
    with ledger_lock:
        RESULTS.mkdir(exist_ok=True)
        if not LEDGER.exists():
            LEDGER.write_text("ts\tskill\tarm\tcase\trun\n")
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with LEDGER.open("a") as handle:
            handle.write(f"{stamp}\t{skill}\t{arm}\t{case}\t{run}\n")


def skill_source(skill, arm, old_ref, scratch):
    """Return the directory that holds the skill for an arm, or None for no skill."""
    if arm == "new":
        return ROOT / "skills" / skill
    if old_ref == "none":
        return None
    target = scratch / "old"
    if not target.exists():
        archive = subprocess.run(
            ["git", "archive", old_ref, f"skills/{skill}"],
            cwd=ROOT, capture_output=True,
        )
        if archive.returncode != 0:
            return None
        target.mkdir(parents=True)
        tmp_tar = scratch / "old.tar"
        tmp_tar.write_bytes(archive.stdout)
        with tarfile.open(tmp_tar) as tar:
            tar.extractall(target, filter="data")
    found = target / "skills" / skill
    return found if found.exists() else None


def parse_stream(stdout):
    """Pull the final text, cost, and tool use out of claude's stream-json output."""
    info = {"output": "", "cost": 0.0, "turns": 0, "error": "", "script_used": False, "skill_used": False}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get("type")
        if kind == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                if block.get("name") == "Skill":
                    info["skill_used"] = True
                if block.get("name") == "Bash" and "scripts/" in json.dumps(block.get("input", {})):
                    info["script_used"] = True
        elif kind == "result":
            info["output"] = event.get("result") or ""
            info["cost"] = event.get("total_cost_usd") or 0.0
            info["turns"] = event.get("num_turns") or 0
            if event.get("is_error"):
                info["error"] = info["output"][:200]
    return info


def run_once(skill, arm, case, run_number, source, model, keep):
    workdir = Path(tempfile.mkdtemp(prefix=f"eval-{skill}-{arm}-"))
    try:
        if source is not None:
            shutil.copytree(source, workdir / (".claude") / "skills" / skill)
        for name, content in case.get("files", {}).items():
            path = workdir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        command = [
            "claude", "-p", case["prompt"], "--model", model,
            "--setting-sources", "project",
            "--allowedTools", "Bash Read Write Edit",
            "--permission-mode", "acceptEdits",
            "--no-session-persistence", "--max-turns", "15",
            "--output-format", "stream-json", "--verbose",
        ]
        ledger_add(skill, arm, case["id"], run_number)
        info = {"output": "", "cost": 0.0, "turns": 0, "error": "", "script_used": False, "skill_used": False}
        try:
            done = subprocess.run(
                command, cwd=workdir, capture_output=True, text=True,
                stdin=subprocess.DEVNULL, timeout=RUN_TIMEOUT_SECONDS,
            )
            info = parse_stream(done.stdout)
            if not info["output"] and not info["error"]:
                info["error"] = (done.stderr or "no result event")[:200]
        except subprocess.TimeoutExpired:
            info["error"] = f"timeout after {RUN_TIMEOUT_SECONDS}s"
        results = []
        for spec in case["checks"]:
            target = spec.get("target", "output")
            if target == "output":
                text = info["output"]
            else:
                path = workdir / target
                text = path.read_text() if path.exists() else ""
                if not path.exists():
                    results.append({"type": spec["type"], "target": target, "ok": False, "detail": "file missing"})
                    continue
            ok, detail = graders.grade(text, {**spec, "cwd": str(workdir)})
            results.append({"type": spec["type"], "target": target, "ok": ok, "detail": detail})
        graded = case["checks"][0].get("target", "output") if case["checks"] else "output"
        sample = info["output"] if graded == "output" else (workdir / graded).read_text() if (workdir / graded).exists() else ""
        return {
            "skill": skill, "arm": arm, "case": case["id"], "run": run_number,
            "passed": bool(results) and all(r["ok"] for r in results) and not info["error"],
            "checks": results, "script_used": info["script_used"], "skill_used": info["skill_used"],
            "cost": info["cost"], "turns": info["turns"], "error": info["error"],
            "sample": sample[:1500],
        }
    finally:
        if not keep:
            shutil.rmtree(workdir, ignore_errors=True)


def prose_preset(target, semicolons=True):
    """The prose rules a script can grade: the same rules the writing skills state."""
    checks = [
        {"type": "not_matches", "target": target, "pattern": "[—–]|\\S[ \\t]--?[ \\t]+\\S"},
        {"type": "not_matches", "target": target, "pattern": "[‘’“”]"},
        {"type": "max_sentence_words", "target": target, "limit": 25},
        {"type": "not_matches", "target": target, "flags": "i",
         "pattern": "\\b(additionally|crucial|delves?|enduring|pivotal|tapestry|testament|vibrant|utili[sz]e|leverag\\w+|facilitat\\w+|in order to|due to the fact that)\\b"},
    ]
    if semicolons:
        checks.append({"type": "not_matches", "target": target, "pattern": ";"})
    return checks


COMMIT_TYPES = "feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert"


def commit_preset(case, target="msg.txt"):
    """The commit message rules a script can grade."""
    kind = case.get("type", COMMIT_TYPES)
    scope = f"\\({case['scope']}\\)" if case.get("scope") else "(?:\\([^)\\s]+\\))?"
    return [
        {"type": "matches", "target": target, "pattern": f"\\A(?:{kind}){scope}!?: [A-Z]"},
        {"type": "not_matches", "target": target, "pattern": "\\A[^\\n]*\\.[ \\t]*$"},
        {"type": "max_first_line", "target": target, "limit": 72},
        {"type": "matches", "target": target, "pattern": "\\A[^\\n]+\\n\\n\\S"},
        {"type": "max_sentence_words", "target": target, "limit": 25},
        {"type": "not_matches", "target": target, "pattern": "[—–;]"},
        {"type": "not_matches", "target": target, "flags": "i", "pattern": "co-authored-by|generated with"},
    ]


def load_cases(skill, only):
    data = json.loads((EVALS / "cases" / f"{skill}.json").read_text())
    cases = data["cases"]
    if only:
        cases = [c for c in cases if c["id"] in only]
    for case in cases:
        preset = case.get("preset")
        if preset == "commit":
            case["checks"] = commit_preset(case) + case.get("checks", [])
        elif preset:
            case["checks"] = case.get("checks", []) + prose_preset(
                case["target"], semicolons=preset != "prose-code"
            )
    return cases


def cmd_run(args):
    cases = load_cases(args.skill, args.case)
    planned = len(cases) * args.runs * len(ARMS)
    used = ledger_count()
    print(f"{planned} calls planned, {used} already in the ledger, limit {args.max_calls}")
    if used + planned > args.max_calls:
        sys.exit("refusing to run: this would pass the call limit")
    model = fast_model()
    scratch = Path(tempfile.mkdtemp(prefix="eval-scratch-"))
    sources = {arm: skill_source(args.skill, arm, args.old_ref, scratch) for arm in ARMS}
    for arm, source in sources.items():
        print(f"arm {arm}: {source if source else 'no skill'}")
    if args.dry_run:
        shutil.rmtree(scratch, ignore_errors=True)
        return
    jobs = [(arm, case, n) for case in cases for arm in ARMS for n in range(1, args.runs + 1)]
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [
            pool.submit(run_once, args.skill, arm, case, n, sources[arm], model, args.keep)
            for arm, case, n in jobs
        ]
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            records.append(record)
            mark = "pass" if record["passed"] else "FAIL"
            print(f"{mark} {record['arm']} {record['case']} #{record['run']} {record['error']}", flush=True)
    out = RESULTS / f"{args.skill}.json"
    RESULTS.mkdir(exist_ok=True)
    if args.case and out.exists():
        # A partial rerun replaces the records of its own cases and keeps the rest.
        kept = [r for r in json.loads(out.read_text())["runs"] if r["case"] not in args.case]
        records = kept + records
    records.sort(key=lambda r: (r["case"], r["arm"], r["run"]))
    out.write_text(json.dumps({"skill": args.skill, "model": model, "old_ref": args.old_ref, "runs": records}, indent=1) + "\n")
    shutil.rmtree(scratch, ignore_errors=True)
    print(render(records))


def passed_without(record, without):
    """A run passes when it has no error and every failed check matches the `without` pattern."""
    if record["error"]:
        return False
    failed = [c for c in record["checks"] if not c["ok"]]
    return all(re.search(without, c["detail"]) for c in failed) if without else not failed


def render(records, without=None):
    """Make the pass-rate table. With `without`, ignore failed checks whose detail matches it."""
    if without:
        records = [{**r, "passed": passed_without(r, without)} for r in records]
    lines = ["| Case | Old | New |", "| --- | --- | --- |"]
    cases = sorted({r["case"] for r in records})
    totals = {arm: [0, 0] for arm in ARMS}
    for case in cases:
        cells = []
        for arm in ARMS:
            runs = [r for r in records if r["case"] == case and r["arm"] == arm]
            passed = sum(r["passed"] for r in runs)
            totals[arm][0] += passed
            totals[arm][1] += len(runs)
            cells.append(f"{passed}/{len(runs)}")
        lines.append(f"| {case} | {cells[0]} | {cells[1]} |")
    cells = [f"**{p}/{t} ({100 * p // max(t, 1)}%)**" for p, t in (totals[a] for a in ARMS)]
    lines.append(f"| All cases | {cells[0]} | {cells[1]} |")
    cost = {arm: sum(r["cost"] for r in records if r["arm"] == arm) for arm in ARMS}
    used = {arm: sum(r["script_used"] for r in records if r["arm"] == arm) for arm in ARMS}
    count = {arm: sum(1 for r in records if r["arm"] == arm) for arm in ARMS}
    lines.append("")
    for arm in ARMS:
        lines.append(f"- {arm}: script run in {used[arm]}/{count[arm]} runs, cost ${cost[arm]:.2f}")
    return "\n".join(lines)


def cmd_report(args):
    data = json.loads((RESULTS / f"{args.skill}.json").read_text())
    print(render(data["runs"], args.without))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run the cases for old and new")
    run.add_argument("skill")
    run.add_argument("--runs", type=int, default=3)
    run.add_argument("--old-ref", default="main", help="git ref of the old skill, or 'none' for no skill")
    run.add_argument("--case", action="append", help="run only this case id")
    run.add_argument("-j", "--jobs", type=int, default=4)
    run.add_argument("--max-calls", type=int, default=CALL_LIMIT)
    run.add_argument("--keep", action="store_true", help="keep the run directories")
    run.add_argument("--dry-run", action="store_true")
    run.set_defaults(func=cmd_run)
    report = sub.add_parser("report", help="print the table from a saved run")
    report.add_argument("skill")
    report.add_argument("--without", help="regex: ignore failed checks whose detail matches it")
    report.set_defaults(func=cmd_report)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
