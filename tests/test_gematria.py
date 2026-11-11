"""Regression tests for the Gematria plugin.

Covers issue #5: "cicada cipher plugin includes dots in rune count".
Characters that are not runes (dots, commas, other punctuation) were
counted as runes, and to_index() raised ValueError on them.

Run with: python3 -m unittest discover -s tests -t .
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.cicada.cicada.gematria import Latin, Runes  # noqa: E402
from plugins.Gematria import Gematria  # noqa: E402

# The plugin exposes the rune alphabet; fall back to the library's own
# definition so the tests still collect if the plugin lacks it.
RUNE_ALPHA = getattr(
    __import__("plugins.Gematria", fromlist=["RUNE_ALPHA"]),
    "RUNE_ALPHA",
    Runes("").alpha,
)


class FakeServer:
    def code_block(self, text):
        return text


class FakeBot:
    def __init__(self):
        self.server = FakeServer()
        self.messages = []

    def msg(self, target, text, follows=None):
        self.messages.append(text)


class FakeMessage:
    target = "test"
    content = ""


class PluginHarness:
    """Runs the real Gematria plugin methods without a live bot."""

    def __init__(self):
        self.bot = FakeBot()
        self.message = FakeMessage()

    # Borrow the real implementations without running __init__ (which needs
    # a full bot with a command interface).
    is_prime = Gematria.is_prime
    format_output = Gematria.format_output
    format_summary = Gematria.format_summary
    cipher = Gematria.cipher
    sum_index = Gematria.sum_index


def run_cipher(text, **kwargs):
    """Run the plugin's cipher and return the message it would send."""
    plugin = PluginHarness()
    plugin.cipher(plugin.message, text, **kwargs)
    return plugin.bot.messages[-1]


def run_sum_index(text, runic=False):
    """Run the plugin's sum_index and return the number it would send."""
    plugin = PluginHarness()
    plugin.sum_index(plugin.message, text, runes=runic)
    return plugin.bot.messages[0]


def rune_count_of(text):
    """The rune count the plugin should report for `text`."""
    return sum(1 for c in Latin(text).to_runes().text if c in RUNE_ALPHA)


class TestRuneCount(unittest.TestCase):
    def test_dots_are_not_counted_as_runes(self):
        """The reported bug: a dot inflated the rune count."""
        self.assertIn("Rune Count: 10", run_cipher("hello. world"))
        self.assertIn("Rune Count: 10", run_cipher("hello world"))

    def test_rune_count_ignores_all_non_rune_characters(self):
        for text in [
            "hello. world",
            "hello, world",
            "abc!def",
            "a.b.c",
            "hello...world",
            "hello world",
            "test",
        ]:
            with self.subTest(text=text):
                expected = rune_count_of(text)
                self.assertIn(f"Rune Count: {expected}", run_cipher(text))

    def test_rune_count_matches_number_of_rune_columns(self):
        """Rune count must equal the number of runes actually displayed."""
        for text in ["hello. world", "abc,def!ghi", "a.b c"]:
            with self.subTest(text=text):
                expected = rune_count_of(text)
                self.assertIn(f"Rune Count: {expected}", run_cipher(text))


class TestCipherOutput(unittest.TestCase):
    def test_cipher_does_not_crash_on_dots(self):
        self.assertIn("Rune Count: 10", run_cipher("hello. world"))

    def test_cipher_does_not_crash_on_punctuation(self):
        for text in ["abc,def!ghi", "a.b.c", "hello,world.foo", "test!", "?!"]:
            with self.subTest(text=text):
                self.assertIsInstance(run_cipher(text), str)

    def test_index_row_stays_aligned_with_rune_columns(self):
        """Every rune keeps a column; non-runes leave a blank, not a shift."""
        out = run_cipher("abc,def!ghi")
        lines = out.split("\n")
        rune_row = next(i for i, l in enumerate(lines) if "ᚪ" in l)
        self.assertEqual(len(lines[rune_row + 2]), len(lines[rune_row]))

    def test_clean_input_output_unchanged(self):
        """Text with only letters still produces the same layout as before."""
        out = run_cipher("test")
        self.assertIn("ᛏ  ᛖ  ᛋ  ᛏ", out)
        self.assertIn("16 18 15 16", out)
        self.assertIn("Rune Count: 4", out)


class TestToIndex(unittest.TestCase):
    def test_to_index_returns_blank_for_non_rune_characters(self):
        """Non-runes must not raise, and must keep their column."""
        self.assertEqual(Runes("ᚻᛖᛚᛚᚩ").to_index(), [8, 18, 20, 20, 3])
        self.assertEqual(Runes("ᚻᛖᛚᛚᚩ. ᚹ").to_index(), [8, 18, 20, 20, 3, " ", " ", 7])

    def test_to_index_keeps_column_count(self):
        for text in ["ᚻᛖᛚᛚᚩ. ᚹᚩᚱᛚᛞ", "a.b", "ᛏᛖᛋᛏ"]:
            with self.subTest(text=text):
                self.assertEqual(len(Runes(text).to_index()), len(text))


class TestSumIndex(unittest.TestCase):
    def test_sum_index_ignores_dots(self):
        self.assertEqual(run_sum_index("hello. world"), run_sum_index("hello world"))

    def test_sum_index_does_not_crash_on_punctuation(self):
        for text in ["hello.world", "a,b,c", "abc!def", "hello.world.foo"]:
            with self.subTest(text=text):
                self.assertIsInstance(run_sum_index(text), int)

    def test_sum_index_matches_clean_equivalent(self):
        self.assertEqual(run_sum_index("abc,def!ghi"), run_sum_index("abcdefghi"))


if __name__ == "__main__":
    unittest.main()
