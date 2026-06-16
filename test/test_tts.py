import os
import wave
import tempfile
import unittest

from ovos_tts_plugin_SAM import SAMTTS


class TestVoiceParams(unittest.TestCase):
    def test_default_sam_voice(self):
        pitch, throat, mouth, speed = SAMTTS.get_voice_params("SAM")
        self.assertEqual((pitch, throat, mouth, speed), (64, 128, 128, 72))

    def test_named_voices(self):
        self.assertEqual(SAMTTS.get_voice_params("elf"), (64, 110, 160, 72))
        self.assertEqual(SAMTTS.get_voice_params("little robot"), (60, 190, 190, 92))
        self.assertEqual(SAMTTS.get_voice_params("extra-terrestrial"), (64, 150, 200, 100))

    def test_unknown_voice_falls_back_to_sam(self):
        self.assertEqual(SAMTTS.get_voice_params("nope"), (64, 128, 128, 72))


class TestSAMTTS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # instantiation builds the `sam` binary from source if missing
        cls.tts = SAMTTS(config={"lang": "en-us"})

    def test_available_languages(self):
        self.assertEqual(self.tts.available_languages, {"en"})

    def test_set_voice_updates_params(self):
        self.tts.set_voice("elf")
        self.assertEqual(
            (self.tts.pitch, self.tts.throat, self.tts.mouth, self.tts.speed),
            (64, 110, 160, 72),
        )

    def test_get_tts_creates_valid_wav(self):
        path = os.path.join(tempfile.mkdtemp(), "sam_out.wav")
        wav_file, _ = self.tts.get_tts("Hello world", path)
        self.assertTrue(os.path.isfile(wav_file))
        self.assertGreater(os.path.getsize(wav_file), 0)
        with wave.open(wav_file, "rb") as f:
            self.assertGreater(f.getnframes(), 0)
            self.assertGreater(f.getframerate(), 0)

    def test_non_english_raises(self):
        path = os.path.join(tempfile.mkdtemp(), "sam_pt.wav")
        with self.assertRaises(KeyError):
            self.tts.get_tts("ola mundo", path, lang="pt-pt")


if __name__ == "__main__":
    unittest.main()
