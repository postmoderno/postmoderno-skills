"""Regression cases for common X counting rules and the draft-checker CLI.

These cases do not claim full twitter-text conformance.
"""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/x-posts/scripts/check_x_post.py"
SPEC = importlib.util.spec_from_file_location("check_x_post", SCRIPT)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class CountingTests(unittest.TestCase):
    def test_unicode_weights_and_normalisation(self):
        for text, expected in [
            ("hello", 5), ("café", 4), ("cafe\u0301", 4),
            ("你好", 4), ("日本語", 6), ("hello…", 7),
            ("“hi”—yes", 8), ("Привет", 6), ("مرحبا", 5),
        ]:
            with self.subTest(text=text):
                self.assertEqual(checker.weighted_length(text)[0], expected)

    def test_common_emoji_sequences(self):
        for text in ["🚀", "👍🏽", "👨‍👩‍👧‍👦", "🏳️‍🌈", "🇨🇾", "1️⃣", "1⃣", "©️"]:
            with self.subTest(text=text):
                self.assertEqual(checker.weighted_length(text), (2, 1))
        self.assertEqual(checker.weighted_length("🚀🚀"), (4, 2))

    def test_digit_with_variation_selector_is_not_a_keycap(self):
        self.assertEqual(checker.weighted_length("1\ufe0f"), (3, 0))

    def test_urls_have_fixed_weight(self):
        for text in [
            "https://example.com", "http://example.com/a/very/long/path",
            "example.com", "postmoderno.io/blog/launch",
            "example.com?source=x", "example.com#details",
            "example.com:8080/path?q=x", "https://en.wikipedia.org/wiki/Go_(programming_language)",
        ]:
            with self.subTest(text=text):
                self.assertEqual(checker.weighted_length(text)[0], 23)

    def test_external_punctuation_is_not_part_of_url(self):
        for text, expected in [
            ("https://example.com.", 24), ("(https://example.com)", 25),
            ("https://en.wikipedia.org/wiki/Go_(programming_language).", 24),
            ("<https://example.com>", 25),
            ('"https://example.com"', 25),
        ]:
            with self.subTest(text=text):
                self.assertEqual(checker.weighted_length(text)[0], expected)

    def test_email_and_code_are_not_bare_domains(self):
        for text in ["hello@example.com", "config.json", "example.completely"]:
            with self.subTest(text=text):
                self.assertEqual(checker.find_urls(text), [])

    def test_nfc_does_not_corrupt_reported_url(self):
        result = checker.check_post("cafe\u0301 https://example.com", 280)
        self.assertEqual(result["urls"], ["https://example.com"])
        self.assertEqual(result["length"], 28)
        self.assertEqual(result["raw_length"], 25)
        self.assertTrue(result["estimated"])

    def test_weighted_limit_boundaries(self):
        for text, ok in [("a" * 280, True), ("a" * 281, False),
                         ("界" * 140, True), ("界" * 141, False),
                         ("a" * 256 + " https://example.com", True),
                         ("a" * 257 + " https://example.com", False)]:
            with self.subTest(length=len(text)):
                self.assertEqual(checker.check_post(text, 280)["ok"], ok)


class WorkflowTests(unittest.TestCase):
    def run_cli(self, text, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              input=text, text=True, capture_output=True, check=False)

    def test_separate_options_and_thread_posts(self):
        result = self.run_cli("First\n---\nSecond\n===\nAlternative", "--json")
        self.assertEqual(result.returncode, 0)
        options = json.loads(result.stdout)
        self.assertEqual([len(o["posts"]) for o in options], [2, 1])

    def test_cli_exit_status_and_custom_limit(self):
        self.assertEqual(self.run_cli("a" * 281).returncode, 1)
        self.assertEqual(self.run_cli("hello", "--limit", "4").returncode, 1)
        self.assertEqual(self.run_cli("hello", "--limit", "5").returncode, 0)
        self.assertNotEqual(self.run_cli(" \n---\n===\n").returncode, 0)

    def test_slop_and_bait_are_advisory(self):
        text = "🚀 Unlock seamless posting. Like & RT @alice @bob #SaaS #AI #Growth #Launch"
        result = self.run_cli(text, "--json")
        self.assertEqual(result.returncode, 0)
        post = json.loads(result.stdout)[0]["posts"][0]
        self.assertEqual(post["mentions"], ["@alice", "@bob"])
        self.assertEqual(len(post["hashtags"]), 4)
        self.assertTrue(any("engagement bait" in n for n in post["notes"]))
        self.assertTrue(any("possible AI tell" in n for n in post["notes"]))

    def test_mentions_exclude_email_and_invalid_handles(self):
        result = checker.check_post("a@b.com @real_user @abcdefghijklmnop @пример", 280)
        self.assertEqual(result["mentions"], ["@real_user"])

    def test_mention_note_counts_distinct_accounts(self):
        repeated = checker.check_post("thanks @alice, and @Alice again", 280)
        self.assertFalse(any("accounts mentioned" in n for n in repeated["notes"]))
        two = checker.check_post("thanks @alice and @bob", 280)
        self.assertTrue(any(n.startswith("2 accounts mentioned") for n in two["notes"]))


if __name__ == "__main__":
    unittest.main()
