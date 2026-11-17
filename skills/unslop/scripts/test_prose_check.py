import os
import subprocess
import sys
import tempfile
import unittest

import prose_check

HERE = os.path.dirname(os.path.abspath(__file__))


def rules(text, **kwargs):
    return [rule for _, rule, _ in prose_check.check_text(text, **kwargs)]


class CheckText(unittest.TestCase):
    def test_clean_text_has_no_findings(self):
        self.assertEqual(prose_check.check_text("The job retries three times. Then it stops.\n"), [])

    def test_em_dash_is_rule_13(self):
        self.assertEqual(rules("The job retries — then stops."), [13])

    def test_spaced_hyphen_is_rule_13_and_a_plain_hyphen_is_fine(self):
        self.assertEqual(rules("The job retries - then stops."), [13])
        self.assertEqual(rules("The well-known job stops."), [])

    def test_an_indented_list_marker_is_not_a_dash(self):
        self.assertEqual(rules("Intro:\n  - First item.\n  - Second item."), [])

    def test_semicolon_has_no_rule_number(self):
        self.assertEqual(rules("It retries; it stops."), [0])

    def test_curly_quotes_are_rule_19(self):
        self.assertEqual(rules("Set “mode” to fast."), [19, 19])

    def test_ai_vocabulary_is_rule_7_and_ignores_case(self):
        self.assertEqual(rules("Additionally, we delve into it."), [7, 7])

    def test_a_word_inside_another_word_does_not_match(self):
        self.assertEqual(rules("The landscaper arrived."), [])

    def test_filler_and_fancy_words(self):
        self.assertEqual(rules("In order to utilize it, press go."), [23, 31])

    def test_sentence_of_26_words_is_flagged_and_25_is_not(self):
        twenty_five = " ".join(["word"] * 25) + "."
        self.assertEqual(rules(twenty_five), [])
        self.assertEqual(rules(" ".join(["word"] * 26) + "."), [28])

    def test_max_words_option_changes_the_limit(self):
        self.assertEqual(rules("one two three four.", max_words=3), [28])

    def test_two_short_sentences_on_one_line_are_not_one_long_sentence(self):
        self.assertEqual(rules(" ".join(["word"] * 15 + ["end."] + ["word"] * 15 + ["end."])), [])

    def test_a_sentence_wrapped_over_lines_counts_as_one(self):
        wrapped = "\n".join(["word word word word word"] * 6) + "."
        self.assertEqual(rules(wrapped), [28])

    def test_code_fence_and_inline_code_are_skipped(self):
        text = "Run `a; b` now.\n\n```\nx = 1; y = 2 — z\n```\n"
        self.assertEqual(prose_check.check_text(text), [])

    def test_list_items_are_separate_sentences(self):
        item = "- " + " ".join(["word"] * 15)
        self.assertEqual(rules("\n".join([item, item])), [])

    def test_table_cells_are_separate_sentences(self):
        cell = " ".join(["word"] * 15)
        table = f"| A | B |\n| --- | --- |\n| {cell} | {cell} |\n"
        self.assertEqual(rules(table), [])
        self.assertEqual(rules(f"| A |\n| --- |\n| {' '.join(['word'] * 26)} |\n"), [28])

    def test_finding_carries_the_line_number(self):
        found = prose_check.check_text("Fine.\n\nIt retries; it stops.\n")
        self.assertEqual(found[0][0], 3)


class CommandLine(unittest.TestCase):
    def run_script(self, text, *extra):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(text)
        self.addCleanup(os.unlink, handle.name)
        return subprocess.run(
            [sys.executable, os.path.join(HERE, "prose_check.py"), *extra, handle.name],
            capture_output=True, text=True,
        )

    def test_exit_0_on_clean_text(self):
        self.assertEqual(self.run_script("It works.\n").returncode, 0)

    def test_exit_1_and_a_location_on_findings(self):
        done = self.run_script("It works; it stays.\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn(":1: [technical-writing]", done.stdout)

    def test_exit_2_on_a_missing_file(self):
        done = subprocess.run([sys.executable, os.path.join(HERE, "prose_check.py"), "/no/such/file"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)

    def test_exit_2_without_arguments(self):
        done = subprocess.run([sys.executable, os.path.join(HERE, "prose_check.py")], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)


if __name__ == "__main__":
    unittest.main()
