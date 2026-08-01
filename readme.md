## Description

This is the OpenVoiceOS TTS plugin for S.A.M. (Software Automatic Mouth).

SAM is a small Text-To-Speech (TTS) program written in C. It runs on most popular platforms. It is a C port of the SAM speech software for the Commodore C64, published in 1982 by Don't Ask Software (now SoftVoice, Inc.).

You can find a description in the [original manual](http://www.retrobits.net/atari/sam.shtml) or in the [manual of the equivalent Apple II program](http://www.apple-iigs.info/newdoc/sam.pdf).

## Install

```bash
pip install ovos-tts-plugin-SAM
```

## Configuration

```json
  "tts": {
    "module": "ovos-tts-plugin-SAM"
 }
```

The original manual lists these typical voice values:

    DESCRIPTION          SPEED     PITCH     THROAT    MOUTH
    Elf                   72        64        110       160
    Little Robot          92        60        190       190
    Stuffy Guy            82        72        110       105
    Little Old Lady       82        32        145       145
    Extra-Terrestrial    100        64        150       200
    SAM                   72        64        128       128

```json
  "tts": {
    "module": "ovos-tts-plugin-SAM",
    "ovos-tts-plugin-SAM": {
      "voice": "stuffy guy"
    }
 }
```

## License

The software is a [reverse-engineered version](https://github.com/vidarh/SAM) of a commercial program published more than 30 years ago. The current copyright holder is SoftVoice, Inc. (www.text2speech.com).

Attempts to contact the company failed. The website was last updated in 2009. The status of the original software is therefore best described as [Abandonware](http://en.wikipedia.org/wiki/Abandonware).

As long as this is the case, the code cannot carry a specific open source software license. Use it at your own risk.

## Docker

SAM runs behind [ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server) (an ElevenLabs-compatible API) on port `9666`. The image is fully offline: the retro `sam` binary is built into it, and it has no cloud dependency and no model download.

Pull the prebuilt image:
```bash
docker run -p 9666:9666 ghcr.io/openvoiceos/ovos-tts-plugin-sam:dev
```

...or build it locally:
```bash
docker build -t ovos-tts-plugin-sam .
docker run -p 9666:9666 ovos-tts-plugin-sam
```

...or use `docker compose up`.

Synthesize speech: `http://localhost:9666/synthesize/hello`

The default voice is `SAM`. Pick another one at build time (`SAM`, `elf`, `little robot`, `stuffy guy`, `little old lady`, `extra-terrestrial`):
```bash
docker build --build-arg SAM_VOICE="stuffy guy" -t ovos-tts-plugin-sam .
```

## Related projects

- [ovos-tts-server](https://github.com/OpenVoiceOS/ovos-tts-server) — the ElevenLabs-compatible API server that serves this plugin over Docker.
- [OpenVoiceOS/ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager) — loads and configures TTS plugins like this one.
