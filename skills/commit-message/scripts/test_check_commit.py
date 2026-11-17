import os
import subprocess
import sys
import tempfile
import unittest

import check_commit

HERE = os.path.dirname(os.path.abspath(__file__))
GOOD = "feat: Add retry to the upload worker\n\nUploads failed on flaky links. The worker now retries three times before it reports an error.\n"


def findings(message):
    return [text for _, text in check_commit.check_message(message)[0]]


def notes(message):
    return [text for _, text in check_commit.check_message(message)[1]]


class Subject(unittest.TestCase):
    def test_good_message_has_no_findings(self):
        self.assertEqual(check_commit.check_message(GOOD), ([], []))

    def test_missing_type_is_a_finding(self):
        self.assertIn("subject must start", findings("Add retry\n\nWhy.")[0])

    def test_unknown_type_is_a_finding(self):
        self.assertTrue(findings("feature: Add retry\n\nWhy."))

    def test_scope_and_breaking_mark_are_accepted(self):
        self.assertEqual(findings("fix(api)!: Reject empty ids\n\nThe API accepted them."), [])

    def test_lowercase_description_is_a_finding(self):
        self.assertEqual(findings("fix: add retry\n\nWhy."), ["the description must start with a capital letter"])

    def test_trailing_period_is_a_finding(self):
        self.assertEqual(findings("fix: Add retry.\n\nWhy."), ["the subject must not end with a period"])

    def test_subject_of_72_characters_passes_and_73_fails(self):
        ok = "fix: " + "A" * 67
        self.assertEqual(len(ok), 72)
        self.assertEqual(findings(ok + "\n\nWhy."), [])
        self.assertEqual(len(findings(ok + "A\n\nWhy.")), 1)

    def test_past_tense_gets_a_note_and_not_a_finding(self):
        message = "fix: Added retry\n\nWhy."
        self.assertEqual(findings(message), [])
        self.assertEqual(len(notes(message)), 1)

    def test_imperative_exception_gets_no_note(self):
        self.assertEqual(notes("fix: Speed up the loader\n\nWhy."), [])


class Body(unittest.TestCase):
    def test_missing_blank_line_is_a_finding(self):
        self.assertEqual(findings("fix: Add retry\nWhy."), ["leave a blank line between the subject and the body"])

    def test_no_body_is_a_note(self):
        self.assertEqual(len(notes("fix: Add retry")), 1)

    def test_em_dash_and_semicolon_are_findings(self):
        self.assertEqual(len(findings("fix: Add retry\n\nIt retries — twice; then stops.")), 2)

    def test_subject_is_checked_for_dashes_too(self):
        self.assertEqual(len(findings("fix: Add retry — twice\n\nWhy.")), 1)

    def test_attribution_line_is_a_finding(self):
        self.assertEqual(len(findings("fix: Add retry\n\nWhy.\n\nCo-Authored-By: Someone")), 1)

    def test_long_sentence_is_a_finding_with_its_line(self):
        long_sentence = " ".join(["word"] * 26) + "."
        found = check_commit.check_message(f"fix: Add retry\n\nShort one.\n\n{long_sentence}\n")[0]
        self.assertEqual([number for number, _ in found], [5])

    def test_sentence_of_25_words_passes(self):
        self.assertEqual(findings("fix: Add retry\n\n" + " ".join(["word"] * 25) + "."), [])

    def test_wrapped_sentence_counts_as_one(self):
        wrapped = "\n".join(["word word word word word"] * 6) + "."
        self.assertEqual(len(findings("fix: Add retry\n\n" + wrapped)), 1)

    def test_trailer_lines_are_not_sentences(self):
        trailer = "Closes " + " ".join(["#1"] * 30)
        self.assertEqual(findings("fix: Add retry\n\nWhy.\n\n" + trailer), [])

    def test_empty_message_is_a_finding(self):
        self.assertEqual(findings(""), ["the message is empty"])


class CommandLine(unittest.TestCase):
    def run_script(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
            handle.write(text)
        self.addCleanup(os.unlink, handle.name)
        return subprocess.run([sys.executable, os.path.join(HERE, "check_commit.py"), handle.name], capture_output=True, text=True)

    def test_exit_0_on_a_good_message(self):
        self.assertEqual(self.run_script(GOOD).returncode, 0)

    def test_exit_0_when_only_notes(self):
        done = self.run_script("fix: Added retry\n\nWhy.\n")
        self.assertEqual(done.returncode, 0)
        self.assertIn("note:", done.stdout)

    def test_exit_1_with_a_line_number(self):
        done = self.run_script("fix: add retry\n\nWhy.\n")
        self.assertEqual(done.returncode, 1)
        self.assertTrue(done.stdout.startswith("line 1:"))

    def test_exit_2_on_a_missing_file(self):
        done = subprocess.run([sys.executable, os.path.join(HERE, "check_commit.py"), "/no/such/file"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)


if __name__ == "__main__":
    unittest.main()
