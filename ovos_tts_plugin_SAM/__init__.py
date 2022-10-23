import os
import subprocess
from distutils.spawn import find_executable
from os.path import expanduser, isfile

from ovos_plugin_manager.templates.tts import TTS, TTSValidator
from ovos_utils.log import LOG


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
        self.binary = self.config.get("binary") or \
                      find_executable("sam") or \
                      expanduser('~/.local/bin/sam')
        if not isfile(self.binary):
            self.compile_and_install_software()
            self.binary = expanduser('~/.local/bin/sam')
        self.voice = self.voice or "SAM"
        self.set_voice()

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
            speed =  82
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
        if lang and not lang.lower().startswith("en"):
            raise KeyError("only english is supported")
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

    @property
    def available_languages(self) -> set:
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
        lang = self.tts.lang.split("-")[0].lower().strip()
        if lang != "en":
            raise Exception('SAMTTS only supports english')

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
