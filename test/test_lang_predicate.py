"""One language predicate serves the validator and `get_tts`.

Both sites ask whether a language tag names English, and both must give one
answer for any tag. The tests compare the two sites to each other, so a change
to one site alone fails here whatever it decides.

The predicate reads the primary subtag: cut at the first "-" or "_", strip the
whitespace on both sides of the cut, fold the case, and accept "en" and "eng".
"""
import unittest

from ovos_tts_plugin_SAM import SAMTTS, SAMTTSValidator, is_english


class _FakeTTS:
    """The validator reads tts.lang and nothing else."""

    def __init__(self, lang):
        self.lang = lang


def _validator_accepts(lang):
    """True if validate_lang accepts `lang`."""
    try:
        SAMTTSValidator(_FakeTTS(lang)).validate_lang()
    except ValueError:
        return False
    return True


def _get_tts_accepts(lang):
    """True if get_tts accepts `lang`.

    `get_tts` runs the binary once the language check passes, so acceptance is
    read from the binary: it is replaced with a recorder, and the call is
    counted. A rejection raises before the binary is touched, and an acceptance
    that never reached the binary fails the assertion at the end.
    """
    tts = SAMTTS.__new__(SAMTTS)  # no binary build, no config
    calls = []
    tts.binary = "/nonexistent/sam"
    tts.pitch = tts.throat = tts.mouth = tts.speed = 1
    import ovos_tts_plugin_SAM as mod
    real_call = mod.subprocess.call
    mod.subprocess.call = lambda *a, **kw: calls.append(a) or 0
    try:
        tts.get_tts("hello", "/dev/null", lang=lang)
    except ValueError:
        return False
    finally:
        mod.subprocess.call = real_call
    assert calls, "get_tts accepted the language but never ran the binary"
    return True


# Tags that need a stated answer, because two reasonable predicates disagree on
# them. The value is the answer both sites must give.
SETTLED = {
    " en-AU ": True,      # whitespace around a tag is not part of it
    "en_US": True,        # an underscore tag names English
    "eng": True,          # ISO 639-2/639-3 for English
    "english": False,     # a language name, not a code
    "ENGLISH-x": False,   # the same name, and "-x" is not a region
}

# Tags with whitespace inside them. A configuration that carries one speaks:
# `ovos_spec_tools.standardize_lang`, which the TTS template applies to
# `self.lang`, passes such a tag through unchanged, so it reaches the predicate
# as written.
INNER_WHITESPACE = ("en -US", " en - AU ", "en\t-US", "en _US")

# Plain tags, English and not English both. The control: a predicate that
# answers False to everything, or True to everything, fails here.
PLAIN = {
    "en": True,
    "en-US": True,
    "EN-gb": True,
    "en-us": True,
    "pt-PT": False,
    "de": False,
    "nl-BE": False,
}


class TestTheTwoSitesAgree(unittest.TestCase):
    def test_both_sites_give_one_answer_for_every_tag(self):
        """The constraint the one predicate exists to hold. The two answers are
        compared to each other and not to a list, so a change to one site alone
        fails here whatever answer it picks."""
        for lang in list(SETTLED) + list(PLAIN):
            with self.subTest(lang=lang):
                self.assertEqual(_validator_accepts(lang),
                                 _get_tts_accepts(lang))

    def test_the_answer_for_each_settled_tag(self):
        """Agreement alone is satisfied by a predicate that refuses every tag,
        so each answer is pinned as a value."""
        for lang, accepted in SETTLED.items():
            with self.subTest(lang=lang):
                self.assertEqual(_validator_accepts(lang), accepted)
                self.assertEqual(_get_tts_accepts(lang), accepted)

    def test_the_answer_for_each_plain_tag(self):
        """English and not English both, so a predicate that answers one way to
        everything fails."""
        for lang, accepted in PLAIN.items():
            with self.subTest(lang=lang):
                self.assertEqual(_validator_accepts(lang), accepted)
                self.assertEqual(_get_tts_accepts(lang), accepted)


class TestWhitespaceInsideATag(unittest.TestCase):
    """A tag with whitespace inside it names English and speaks.

    The whitespace is stripped on both sides of the cut, so the primary subtag
    is `en` whether the space sits before the tag, after it, or against the
    separator.
    """

    def test_both_sites_accept_a_tag_with_inner_whitespace(self):
        for lang in INNER_WHITESPACE:
            with self.subTest(lang=lang):
                self.assertTrue(is_english(lang))
                self.assertTrue(_validator_accepts(lang))
                self.assertTrue(_get_tts_accepts(lang))

    def test_inner_whitespace_does_not_make_a_non_english_tag_english(self):
        """The strip must not reach past the primary subtag."""
        for lang in ("pt -PT", " de - DE ", "e n", "e-n"):
            with self.subTest(lang=lang):
                self.assertFalse(is_english(lang))
                self.assertFalse(_validator_accepts(lang))
                self.assertFalse(_get_tts_accepts(lang))


class TestIsEnglish(unittest.TestCase):
    """The helper on its own, at the edges the two call sites do not reach."""

    def test_a_non_string_is_not_a_tag(self):
        for lang in (None, 42, [], object()):
            with self.subTest(lang=lang):
                self.assertFalse(is_english(lang))

    def test_the_empty_tag_is_not_english(self):
        for lang in ("", "   ", "-", "_"):
            with self.subTest(lang=lang):
                self.assertFalse(is_english(lang))

    def test_a_tag_that_only_starts_with_the_letters_is_not_english(self):
        """A prefix is not enough. Every string that begins with `en` and is
        not a code is refused, which is a class and not a list: the tags below
        are samples of it, and the en dash belongs to it because an en dash is
        not the separator.
        """
        for lang in ("english", "enm", "enochian", "en1", "enx",
                     "ENGLISH-x", "en–US"):
            with self.subTest(lang=lang):
                self.assertFalse(is_english(lang))
                self.assertFalse(_validator_accepts(lang))
                self.assertFalse(_get_tts_accepts(lang))

    def test_the_underscore_and_the_hyphen_cut_at_the_same_place(self):
        self.assertEqual(is_english("en_US"), is_english("en-US"))
        self.assertEqual(is_english("pt_BR"), is_english("pt-BR"))


class TestGetTTSKeepsItsMissingLanguageBehaviour(unittest.TestCase):
    """A missing language synthesises.

    `get_tts` tests `lang` for a value before it asks the predicate, and the
    predicate answers False for None, so dropping that guard would turn a
    missing language into a refusal.
    """

    def test_no_language_synthesises(self):
        self.assertTrue(_get_tts_accepts(None))

    def test_the_empty_language_synthesises(self):
        self.assertTrue(_get_tts_accepts(""))


if __name__ == "__main__":
    unittest.main()
