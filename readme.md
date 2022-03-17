## Description

OpenVoiceOS TTS plugin for S.A.M - Software Automatic Mouth

Sam is a very small Text-To-Speech (TTS) program written in C, that runs on most popular platforms. It is an adaption to C of the speech software SAM (Software Automatic Mouth) for the Commodore C64 published in the year 1982 by Don't Ask Software (now SoftVoice, Inc.). 

A description can be found in the original manual at http://www.retrobits.net/atari/sam.shtml or in the manual of the equivalent Apple II program http://www.apple-iigs.info/newdoc/sam.pdf

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

Some typical values written in the original manual are:

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


# License

The software is a [reverse-engineered version](https://github.com/vidarh/SAM) of a commercial software published more than 30 years ago. The current copyright holder is SoftVoice, Inc. (www.text2speech.com)

Any attempt to contact the company failed. The website was last updated in the year 2009. The status of the original software can therefore best described as Abandonware (http://en.wikipedia.org/wiki/Abandonware)

As long this is the case I cannot put my code under any specific open source software license Use it at your own risk.


## Docker

build it
```bash
docker build . -t ovos/sam
```

run it
```bash
docker run -p 8080:9666 ovos/sam
```

use it `http://localhost:8080/synthesize/hello`