import json
import re
import unittest

import graders
import run


def ok(text, **spec):
    return graders.grade(text, spec)[0]


class Graders(unittest.TestCase):
    def test_matches_and_not_matches(self):
        self.assertTrue(ok("a b", type="matches", pattern="a"))
        self.assertFalse(ok("a b", type="matches", pattern="z"))
        self.assertTrue(ok("a b", type="not_matches", pattern="z"))
        self.assertFalse(ok("a b", type="not_matches", pattern="b"))

    def test_flags_i_ignores_case_and_anchors_see_each_line(self):
        self.assertTrue(ok("x\nHello", type="matches", pattern="^hello", flags="i"))

    def test_max_sentence_words_boundary(self):
        self.assertTrue(ok(" ".join(["w"] * 25) + ".", type="max_sentence_words", limit=25))
        self.assertFalse(ok(" ".join(["w"] * 26) + ".", type="max_sentence_words", limit=25))

    def test_max_sentence_words_skips_code_and_splits_list_items(self):
        long_code = "```\n" + " ".join(["w"] * 40) + "\n```\n"
        self.assertTrue(ok(long_code, type="max_sentence_words", limit=25))
        items = "- " + " ".join(["w"] * 20) + "\n- " + " ".join(["w"] * 20) + "\n"
        self.assertTrue(ok(items, type="max_sentence_words", limit=25))

    def test_max_first_line(self):
        self.assertTrue(ok("abc\nlonger second line", type="max_first_line", limit=3))
        self.assertFalse(ok("abcd\n", type="max_first_line", limit=3))

    def test_command_uses_the_exit_code(self):
        self.assertTrue(ok("", type="command", cmd="true", cwd="."))
        self.assertFalse(ok("", type="command", cmd="false", cwd="."))


class Presets(unittest.TestCase):
    def passes(self, checks, text):
        return all(graders.grade(text, c)[0] for c in checks)

    def test_prose_preset_rejects_each_tell(self):
        checks = run.prose_preset("t")
        self.assertTrue(self.passes(checks, "It works. It stays.\n"))
        self.assertTrue(self.passes(checks, "Intro.\n\n- First item.\n- Second item.\n"))
        for bad in ["a — b.", "a; b.", "a “b”.", "Additionally, it works.", "a - b.", " ".join(["w"] * 30) + "."]:
            self.assertFalse(self.passes(checks, bad), bad)

    def test_prose_code_preset_allows_semicolons(self):
        self.assertTrue(self.passes(run.prose_preset("t", semicolons=False), "Run `a; b`.\n"))

    def test_commit_preset(self):
        checks = run.commit_preset({})
        good = "fix: Raise the timeout\n\nUploads failed on large files.\n"
        self.assertTrue(self.passes(checks, good))
        for bad in [
            "fix: raise the timeout\n\nWhy.\n",
            "fix: Raise the timeout.\n\nWhy.\n",
            "Raise the timeout\n\nWhy.\n",
            "fix: Raise the timeout\nWhy.\n",
            "fix: Raise the timeout\n\nWhy; and more.\n",
            "fix: Raise the timeout\n\nWhy.\n\nCo-Authored-By: x\n",
            "fix: " + "A" * 70 + "\n\nWhy.\n",
        ]:
            self.assertFalse(self.passes(checks, bad), bad)

    def test_commit_preset_pins_type_and_scope(self):
        checks = run.commit_preset({"type": "chore", "scope": "deps"})
        self.assertTrue(self.passes(checks, "chore(deps): Bump yaml\n\nWhy.\n"))
        self.assertFalse(self.passes(checks, "chore: Bump yaml\n\nWhy.\n"))
        self.assertFalse(self.passes(checks, "fix(deps): Bump yaml\n\nWhy.\n"))


class Stream(unittest.TestCase):
    def test_parse_stream_reads_result_cost_and_script_use(self):
        events = [
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {}},
                {"type": "tool_use", "name": "Bash", "input": {"command": "python3 scripts/check.py f"}},
            ]}},
            {"type": "result", "result": "done", "total_cost_usd": 0.5, "num_turns": 3},
        ]
        info = run.parse_stream("\n".join(json.dumps(e) for e in events) + "\nnot json\n")
        self.assertEqual((info["output"], info["cost"], info["turns"]), ("done", 0.5, 3))
        self.assertTrue(info["script_used"] and info["skill_used"])

    def test_parse_stream_keeps_an_error_result(self):
        info = run.parse_stream(json.dumps({"type": "result", "result": "boom", "is_error": True}))
        self.assertEqual(info["error"], "boom")


class Without(unittest.TestCase):
    def test_a_failure_that_matches_the_pattern_is_ignored(self):
        record = {"error": "", "checks": [{"ok": False, "detail": "found 'Co-Authored-By'"}]}
        self.assertTrue(run.passed_without(record, "Co-Authored"))
        self.assertFalse(run.passed_without(record, "other"))
        self.assertFalse(run.passed_without({**record, "error": "timeout"}, "Co-Authored"))


class Cases(unittest.TestCase):
    def test_every_case_file_loads_and_has_checks(self):
        for path in (run.EVALS / "cases").glob("*.json"):
            cases = run.load_cases(path.stem, None)
            self.assertTrue(5 <= len(cases) <= 10, path.name)
            for case in cases:
                self.assertTrue(case["checks"], case["id"])
                self.assertTrue(re.fullmatch(r"[a-z0-9-]+", case["id"]), case["id"])

    def test_render_reports_pass_counts_per_arm(self):
        records = [
            {"case": "a", "arm": "old", "passed": False, "cost": 0.1, "script_used": False},
            {"case": "a", "arm": "new", "passed": True, "cost": 0.1, "script_used": True},
        ]
        table = run.render(records)
        self.assertIn("| a | 0/1 | 1/1 |", table)
        self.assertIn("100%", table)


if __name__ == "__main__":
    unittest.main()
