from os.path import expanduser, isfile

import os
import re
import shutil
import subprocess
from ovos_plugin_manager.templates.tts import TTS, TTSValidator
from ovos_utils import classproperty
from ovos_utils.log import LOG


_PRIMARY_SUBTAG = re.compile(r"[-_]")

#: The primary subtags this plugin answers to. "en" is the BCP-47 code the
#: plugin advertises in SAMTTSPluginConfig. "eng" is the ISO 639-2/639-3 code
#: for the same language, and a caller that uses it means English.
_ENGLISH_SUBTAGS = frozenset(("en", "eng"))


def is_english(lang) -> bool:
    """Return True if ``lang`` names English.

    One question, one answer, for every site that asks it. The validator and
    ``get_tts`` both call this, so a tag cannot pass the language gate at load
    and then be refused at synthesis.

    The primary subtag decides: cut ``lang`` at the first ``"-"`` or ``"_"``,
    strip the whitespace on both sides of the cut, fold the case, and compare
    against :data:`_ENGLISH_SUBTAGS`. So all of ``"en"``, ``"en-US"``,
    ``"en_US"``, ``"EN-gb"``, ``"eng"``, ``" en-AU "`` and ``"en -US"`` name
    English.

    A prefix is not enough. Every string that begins with ``en`` and is not a
    code is refused: ``"english"``, ``"ENGLISH-x"``, ``"enx"``, ``"en1"``, and a
    tag written with an en dash in place of the hyphen are all outside the
    separator rule above.

    A non-string, including ``None``, is not a tag and returns False. Each call
    site tests ``lang`` for a value before it asks, and keeps its own behaviour
    for a missing one.
    """
    if not isinstance(lang, str):
        return False
    primary = _PRIMARY_SUBTAG.split(lang.strip(), maxsplit=1)[0]
    return primary.strip().lower() in _ENGLISH_SUBTAGS


class SAMTTS(TTS):
    """
    DESCRIPTION          SPEED     PITCH     THROAT    MOUTH
    Elf                   72        64        110       160
    Little Robot          92        60        190       190
    Stuffy Guy            82        72        110       105
    Little Old Lady       82        32        145       145
    Extra-Terrestrial    100        64        150       200
    SAM                   72        64        128       128
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, audio_ext="wav",
                         validator=SAMTTSValidator(self))
        # The binary is resolved at the first synthesis, not here. The plugin
        # manager constructs the class before it calls validator.validate(),
        # so a build that fails in __init__ hides the language rejection: a
        # caller asking for a language SAM does not speak saw a make error
        # instead of the validator's message.
        self._binary = None
        self.voice = self.voice or "SAM"
        self.set_voice()

    @property
    def binary(self):
        """Path of the vidarh/SAM binary, found or built at first use."""
        if self._binary is None:
            self._binary = self._find_binary()
        return self._binary

    @binary.setter
    def binary(self, value):
        self._binary = value

    def _find_binary(self):
        """Locate the vidarh/SAM binary, building it if needed.

        A bare ``sam`` on PATH cannot be trusted: CI runners (and some user
        systems) ship the AWS SAM CLI, a Click program that rejects the
        ``-pitch``/``-throat`` flags this plugin uses. Always validate that the
        discovered binary speaks the vidarh interface before using it.
        """
        configured = self.config.get("binary")
        candidates = [configured,
                      shutil.which("sam"),
                      expanduser('~/.local/bin/sam')]
        for binary in candidates:
            if binary and isfile(binary) and self._is_vidarh_sam(binary):
                return binary
        # nothing usable found, build it from source
        self.compile_and_install_software()
        return expanduser('~/.local/bin/sam')

    @staticmethod
    def _is_vidarh_sam(binary):
        """Return True if ``binary`` is the vidarh/SAM CLI (not AWS SAM CLI)."""
        try:
            proc = subprocess.run([binary], capture_output=True, text=True,
                                  timeout=10)
            usage = (proc.stdout or "") + (proc.stderr or "")
        except Exception:
            return False
        return "-pitch" in usage and "-throat" in usage

    def set_voice(self, voice=None):
        if voice:
            self.voice = voice
        self.pitch, self.throat, self.mouth, self.speed = self.get_voice_params(self.voice)

    @staticmethod
    def get_voice_params(voice):
        pitch = 64
        throat = 128
        mouth = 128
        speed = 72
        if voice.lower() == "elf":
            pitch = 64
            throat = 110
            mouth = 160
            speed = 72
        elif voice.lower() == "little robot":
            pitch = 60
            throat = 190
            mouth = 190
            speed = 92
        elif voice.lower() == "stuffy guy":
            pitch = 72
            throat = 110
            mouth = 105
            speed = 82
        elif voice.lower() == "little old lady":
            pitch = 32
            throat = 145
            mouth = 145
            speed = 82
        elif voice.lower() == "extra-terrestrial":
            pitch = 64
            throat = 150
            mouth = 200
            speed = 100
        return pitch, throat, mouth, speed

    @staticmethod
    def compile_and_install_software():
        """Use the subprocess module to compile/install the C software."""
        dest_path = os.path.expanduser('~/.local/bin/')
        if os.path.exists(dest_path + 'sam'):
            return  # binary exists no need to build it
        elif not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)

        try:
            src_path = '/tmp/SAM'
            if not os.path.exists(src_path):
                LOG.info("Fetching SAM")
                # Git clone
                repo = 'https://github.com/vidarh/SAM'
                subprocess.check_call(f'git clone {repo} {src_path}', shell=True)

            LOG.info("Building SAM")
            # compile the software
            subprocess.check_call("make", cwd=src_path, shell=True)

            # install the binary
            cmd = f'cp {src_path}/sam {dest_path}'
            subprocess.check_call(cmd, cwd=src_path, shell=True)
        except Exception as e:
            LOG.error("FAILED TO COMPILE S.A.M. - https://github.com/vidarh/SAM")
            LOG.warning("binary missing: ~/.local/bin/sam")
            raise
        return True

    def get_tts(self, sentence, wav_file, lang=None, voice=None,
                pitch=None, speed=None, mouth=None, throat=None):
        if lang and not is_english(lang):
            # ValueError, the type the validator raises for this condition. One
            # condition answers with one type, so a caller catches one type,
            # and the message carries no quotes rendered into it.
            raise ValueError("only english is supported")
        if voice:
            # TODO validate voice is valid
            pitch2, throat2, mouth2, speed2 = self.get_voice_params(voice)
            pitch = pitch or pitch2
            throat = throat or throat2
            mouth = mouth or mouth2
            speed = speed or speed2
        subprocess.call(
            [self.binary,
             "-pitch", str(pitch or self.pitch),
             "-speed", str(speed or self.speed),
             "-mouth", str(mouth or self.mouth),
             "-throat", str(throat or self.throat),
             "-wav", wav_file,
             sentence])

        return wav_file, None

    @classproperty
    def available_languages(cls) -> set:
        """Return languages supported by this TTS implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set(SAMTTSPluginConfig.keys())


class SAMTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(SAMTTSValidator, self).__init__(tts)

    def validate_lang(self):
        if not is_english(self.tts.lang):
            # ValueError, not a bare Exception: the value is wrong, which is
            # what ValueError says, and a caller can catch it without also
            # swallowing every programming error in the same block.
            raise ValueError('SAMTTS only supports english')

    def validate_connection(self):
        pass

    def get_tts_class(self):
        return SAMTTS


SAMTTSPluginConfig = {
    "en": [
        {"voice": "SAM",
         "meta": {"gender": "male", "display_name": "SAM", "offline": True, "priority": 90}},
        {"voice": "elf",
         "meta": {"gender": "neutral", "display_name": "Elf", "offline": True, "priority": 91}},
        {"voice": "little robot",
         "meta": {"gender": "neutral", "display_name": "Little Robot", "offline": True, "priority": 92}},
        {"voice": "stuffy guy",
         "meta": {"gender": "male", "display_name": "Stuffy Guy", "offline": True, "priority": 93}},
        {"voice": "little old lady",
         "meta": {"gender": "female", "display_name": "Little Old Lady", "offline": True, "priority": 94}},
        {"voice": "extra-terrestrial",
         "meta": {"gender": "neutral", "display_name": "Extra-Terrestrial", "offline": True, "priority": 95}}
    ]
}

if __name__ == "__main__":
    e = SAMTTS()
    e.set_voice("elf")
    ssml = """Hello world"""
    e.get_tts(ssml, "sam.wav", voice="extra-terrestrial")
