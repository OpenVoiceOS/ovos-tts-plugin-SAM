"""The validator's rejection path, and its exception type.

`validate_lang` raised a bare `Exception`. A caller that wants to handle an
unsupported language then has to catch `Exception`, which also swallows every
programming error in the same block. The type is asserted here so a later
rewrite of this message cannot widen it back.

The plugin loader (`ovos_plugin_manager.tts`) catches `Exception` around
`validate()` and re-raises without reading the type, and nothing in the
organisation matches on this message, both checked before the change. So the
effect is on a caller, not on the loader.

T-5157 chose `ValueError` for the same condition in ovos-tts-plugin-pico, and
T-5207 chose `RuntimeError` for a missing binary in ovos-tts-plugin-espeakNG.
"""
import unittest

from ovos_tts_plugin_SAM import SAMTTS, SAMTTSValidator


class _FakeTTS:
    """The validator reads tts.lang and nothing else."""

    def __init__(self, lang):
        self.lang = lang


def _validator(lang):
    return SAMTTSValidator(_FakeTTS(lang))


class TestValidateLang(unittest.TestCase):
    def test_an_unsupported_language_raises_valueerror(self):
        with self.assertRaises(ValueError) as caught:
            _validator("pt-PT").validate_lang()
        self.assertIn("SAMTTS only supports english", str(caught.exception))

    def test_the_class_is_exactly_valueerror(self):
        """A decision, not a safety net.

        The test above already rejects every type that is too wide, the bare
        `Exception` included, because `assertRaises(ValueError)` does not
        accept a parent class. This one adds only the other direction: a
        subclass of `ValueError`, such as a future
        `UnsupportedLanguageError(ValueError)`, would fail here. That is
        deliberate. A narrowing of this type is a decision to take on purpose,
        with the caller's `except ValueError` in mind, rather than a change
        that lands unnoticed.
        """
        with self.assertRaises(ValueError) as caught:
            _validator("pt-PT").validate_lang()
        self.assertIs(type(caught.exception), ValueError)

    def test_english_is_accepted(self):
        """The control. Without it a validator that rejected everything would
        pass the tests above. The tags cover the split, the case fold and the
        strip the validator performs."""
        for lang in ("en", "en-US", "EN-gb", " en-AU ", "en-us"):
            with self.subTest(lang=lang):
                self.assertIsNone(_validator(lang).validate_lang())


class TestGetTTSRejectsNonEnglish(unittest.TestCase):
    """The synthesis path answers with the same type as the validator.

    One condition answers with one type, so a caller that handles an
    unsupported language catches `ValueError` alone and reads a message with no
    quotes rendered into it.

    Which tags the two sites refuse is a separate constraint, held in
    `test_lang_predicate.py`. These tests use `pt-PT`, which both sites refuse,
    so they measure the type and not the predicate.
    """

    def test_a_non_english_language_raises_valueerror(self):
        tts = SAMTTS.__new__(SAMTTS)  # no binary build, no config
        with self.assertRaises(ValueError) as caught:
            tts.get_tts("ola", "/dev/null", lang="pt-PT")
        self.assertEqual(str(caught.exception), "only english is supported")

    def test_the_message_carries_no_embedded_quotes(self):
        """What `KeyError` did to the text a caller logs."""
        tts = SAMTTS.__new__(SAMTTS)
        with self.assertRaises(ValueError) as caught:
            tts.get_tts("ola", "/dev/null", lang="pt-PT")
        self.assertNotIn("'", str(caught.exception))
        self.assertEqual(str(KeyError("only english is supported")),
                         "'only english is supported'")


if __name__ == "__main__":
    unittest.main()
