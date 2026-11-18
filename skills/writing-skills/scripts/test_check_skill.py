import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_skill

HERE = Path(__file__).resolve().parent
GOOD_DESCRIPTION = "Does a thing. Use when asked to do the thing, and skip for other things."


def make_skill(root, name="demo", description=GOOD_DESCRIPTION, body="# Demo\n", fm_name=None, extra=()):
    folder = Path(root) / name
    folder.mkdir()
    fm_name = name if fm_name is None else fm_name
    (folder / "SKILL.md").write_text(
        f"---\nname: {fm_name}\ndescription: {description}\n---\n\n{body}", encoding="utf-8"
    )
    for relative in extra:
        target = folder / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x", encoding="utf-8")
    return folder


class CheckSkill(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def findings(self, **kwargs):
        return check_skill.check_skill(make_skill(self.tmp.name, **kwargs))

    def test_good_skill_has_no_findings(self):
        self.assertEqual(self.findings(), [])

    def test_missing_skill_file(self):
        folder = Path(self.tmp.name) / "empty"
        folder.mkdir()
        self.assertEqual(check_skill.check_skill(folder), ["SKILL.md is missing"])

    def test_missing_frontmatter(self):
        folder = Path(self.tmp.name) / "plain"
        folder.mkdir()
        (folder / "SKILL.md").write_text("# Plain\n", encoding="utf-8")
        self.assertIn("frontmatter", check_skill.check_skill(folder)[0])

    def test_unclosed_frontmatter(self):
        folder = Path(self.tmp.name) / "open"
        folder.mkdir()
        (folder / "SKILL.md").write_text("---\nname: open\n", encoding="utf-8")
        self.assertIn("closing", check_skill.check_skill(folder)[0])

    def test_name_must_match_folder(self):
        found = self.findings(fm_name="other")
        self.assertEqual(len(found), 1)
        self.assertIn("does not match the folder", found[0])

    def test_name_must_use_the_allowed_characters(self):
        found = self.findings(name="Demo_Skill", fm_name="Demo_Skill")
        self.assertTrue(any("lowercase" in f for f in found))

    def test_name_of_65_characters_fails_and_64_passes(self):
        long_ok = "a" * 64
        long_bad = "a" * 65
        self.assertEqual(self.findings(name=long_ok), [])
        self.assertTrue(any("limit is 64" in f for f in self.findings(name=long_bad)))

    def test_reserved_word_in_name_fails(self):
        found = self.findings(name="my-claude-helper")
        self.assertTrue(any("reserved word 'claude'" in f for f in found))

    def test_description_of_1024_characters_passes_and_1025_fails(self):
        base = "Use when needed. "
        ok = base + "x" * (1024 - len(base))
        bad = base + "x" * (1025 - len(base))
        self.assertEqual(self.findings(name="at-limit", description=ok), [])
        self.assertTrue(any("limit is 1024" in f for f in self.findings(name="over", description=bad)))

    def test_description_without_a_trigger_phrase_fails(self):
        found = self.findings(description="Cut AI tells from any writing. Must always apply.")
        self.assertEqual(len(found), 1)
        self.assertIn("Use when", found[0])

    def test_trigger_phrases_are_accepted(self):
        phrases = ("TRIGGER when editing prose.", "Use for docs.", "Writes x. use before commits.")
        for number, text in enumerate(phrases):
            self.assertEqual(self.findings(name=f"skill-{number}", description=text), [])

    def test_missing_description_fails(self):
        folder = Path(self.tmp.name) / "bare"
        folder.mkdir()
        (folder / "SKILL.md").write_text("---\nname: bare\n---\nbody\n", encoding="utf-8")
        self.assertEqual(check_skill.check_skill(folder), ["frontmatter has no description"])

    def test_angle_brackets_in_description_fail(self):
        found = self.findings(description="Use when a <tag> appears.")
        self.assertEqual(len(found), 1)
        self.assertIn("XML", found[0])

    def test_folded_description_is_joined(self):
        folder = Path(self.tmp.name) / "folded"
        folder.mkdir()
        (folder / "SKILL.md").write_text(
            "---\nname: folded\ndescription: >\n  Does a thing.\n  Use when asked.\n---\nbody\n",
            encoding="utf-8",
        )
        self.assertEqual(check_skill.check_skill(folder), [])

    def test_quoted_values_lose_their_quotes(self):
        folder = Path(self.tmp.name) / "quoted"
        folder.mkdir()
        (folder / "SKILL.md").write_text(
            '---\nname: "quoted"\ndescription: \'Use when quoted.\'\n---\nbody\n', encoding="utf-8"
        )
        self.assertEqual(check_skill.check_skill(folder), [])

    def test_500_lines_pass_and_501_fail(self):
        head = 5  # the frontmatter and the blank line before the body
        ok = "x\n" * (500 - head)
        bad = "x\n" * (501 - head)
        self.assertEqual(self.findings(body=ok), [])
        self.assertTrue(any("501 lines" in f for f in self.findings(name="long", body=bad)))

    def test_markdown_link_to_missing_file_fails(self):
        found = self.findings(body="See [the guide](references/guide.md).\n")
        self.assertEqual(found, ["SKILL.md names 'references/guide.md', which does not exist"])

    def test_markdown_link_to_existing_file_passes(self):
        found = self.findings(body="See [the guide](references/guide.md#top).\n", extra=["references/guide.md"])
        self.assertEqual(found, [])

    def test_backtick_script_path_must_exist(self):
        found = self.findings(body="Run `scripts/run.sh` first.\n")
        self.assertEqual(found, ["SKILL.md names 'scripts/run.sh', which does not exist"])

    def test_urls_and_anchors_are_not_checked(self):
        body = "[a](https://example.com/x) [b](#top) [c](mailto:a@b.c)\n"
        self.assertEqual(self.findings(body=body), [])

    def test_placeholders_and_globs_are_not_checked(self):
        body = "Write `references/<name>.md` and read `references/*.md`.\n"
        self.assertEqual(self.findings(body=body), [])


class CommandLine(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(HERE / "check_skill.py"), *args], capture_output=True, text=True
        )

    def test_clean_folder_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = make_skill(tmp)
            result = self.run_cli(str(folder))
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip().endswith("demo: ok"))

    def test_finding_exits_1_and_names_the_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = make_skill(tmp, description="No trigger here.")
            result = self.run_cli(str(folder) + "/")
        self.assertEqual(result.returncode, 1)
        self.assertIn("demo: description does not say when", result.stdout)

    def test_not_a_folder_is_a_finding(self):
        result = self.run_cli("/nonexistent/skill")
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not a folder", result.stdout)

    def test_no_arguments_exits_2(self):
        self.assertEqual(self.run_cli().returncode, 2)


if __name__ == "__main__":
    unittest.main()
