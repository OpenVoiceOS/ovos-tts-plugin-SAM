import subprocess
import os
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.tts import TTS, TTSValidator
from os.path import expanduser, isfile


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
        self.compile_and_install_software()
        super().__init__(*args, **kwargs, audio_ext="wav",
                         validator=SAMTTSValidator(self))
        self.binary = self.config.get("binary") or \
                      expanduser('~/.local/bin/sam')
        if not isfile(self.binary):
            self.compile_and_install_software()
            self.binary = expanduser('~/.local/bin/sam')
        self.voice = self.voice or "SAM"
        self.set_voice()

    def set_voice(self, voice=None):
        if voice:
            self.voice = voice
        if self.voice.lower() == "elf":
            self.pitch = self.config.get("pitch", 64)
            self.throat = self.config.get("throat", 110)
            self.mouth = self.config.get("mouth", 160)
            self.speed = self.config.get("speed", 72)
        elif self.voice.lower() == "little robot":
            self.pitch = self.config.get("pitch", 60)
            self.throat = self.config.get("throat", 190)
            self.mouth = self.config.get("mouth", 190)
            self.speed = self.config.get("speed", 92)
        elif self.voice.lower() == "stuffy guy":
            self.pitch = self.config.get("pitch", 72)
            self.throat = self.config.get("throat", 110)
            self.mouth = self.config.get("mouth", 105)
            self.speed = self.config.get("speed", 82)
        elif self.voice.lower() == "little old lady":
            self.pitch = self.config.get("pitch", 32)
            self.throat = self.config.get("throat", 145)
            self.mouth = self.config.get("mouth", 145)
            self.speed = self.config.get("speed", 82)
        elif self.voice.lower() == "extra-terrestrial":
            self.pitch = self.config.get("pitch", 64)
            self.throat = self.config.get("throat", 150)
            self.mouth = self.config.get("mouth", 200)
            self.speed = self.config.get("speed", 100)
        else: # SAM / default
            self.pitch = self.config.get("pitch", 64)
            self.throat = self.config.get("throat", 128)
            self.mouth = self.config.get("mouth", 128)
            self.speed = self.config.get("speed", 72)

    @staticmethod
    def compile_and_install_software():
        """Use the subprocess module to compile/install the C software."""
        dest_path = os.path.expanduser('~/.local/bin/')
        if os.path.exists(dest_path + 'sam'):
            return  # binary exists no need to build it
        elif not os.path.exists(dest_path):
            os.mkdir(dest_path)

        LOG.info("Fetching SAM source code")
        # Git clone
        repo = 'https://github.com/vidarh/SAM'
        src_path = '/tmp/SAM'
        subprocess.check_call('git clone {} {}'.format(repo, src_path),
                              shell=True)

        LOG.info("Compiling SAM")
        # compile the software
        subprocess.check_call("make", cwd=src_path, shell=True)

        # install the binary
        cmd = 'cp {}/sam {}'.format(src_path, dest_path)
        subprocess.check_call(cmd, cwd=src_path, shell=True)

    def get_tts(self, sentence, wav_file, lang=None):
        subprocess.call(
            [self.binary,
             "-pitch", str(self.pitch),
             "-speed", str(self.speed),
             "-mouth", str(self.mouth),
             "-throat", str(self.throat),
             "-wav", wav_file,
             sentence])

        return wav_file, None


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


if __name__ == "__main__":
    e = SAMTTS()
    e.set_voice("elf")
    ssml = """Hello world"""
    e.get_tts(ssml, "sam.wav")
