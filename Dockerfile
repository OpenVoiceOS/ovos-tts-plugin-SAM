# S.A.M. (Software Automatic Mouth) — the 1982 retro voice — served through
# ovos-tts-server's ElevenLabs-compatible API on port 9666. A self-contained,
# fully offline image: any client that speaks the ovos-tts-server / ElevenLabs API
# can hit it, and it can be A/B-tested against other ovos-tts-server voices
# (phoonnx, edge-tts, ...) by pointing at a different port.
#
# SAM is a tiny C program; there is no cloud dependency and no model download, so
# the container needs no network access at runtime.
FROM python:3.14-slim

# build-essential + libsdl1.2-dev: compile the vidarh/SAM binary from source.
# git: fetch the SAM sources.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        libsdl1.2-dev \
    && rm -rf /var/lib/apt/lists/*

# Build the vidarh/SAM binary and drop it on PATH at /usr/bin/sam. The plugin
# probes PATH for a `sam` that speaks the vidarh interface (-pitch/-throat), so a
# system-wide install means it never has to build the binary at runtime.
RUN git clone https://github.com/vidarh/SAM /tmp/SAM \
    && make -C /tmp/SAM \
    && cp /tmp/SAM/sam /usr/bin/sam \
    && rm -rf /tmp/SAM

WORKDIR /app
COPY . /app

# the plugin + the OVOS TTS server. setuptools<81 keeps ovos-plugin-manager's
# pkg_resources usage working. SAM emits WAV natively, so no ffmpeg transcode is
# needed; the alpha floor still lets pip resolve the prerelease server without --pre.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "setuptools<81" "." "ovos-tts-server>=1.13.5a1"

# Default voice, overridable with the SAM_VOICE build arg. Valid voices:
# SAM, elf, little robot, stuffy guy, little old lady, extra-terrestrial.
ARG SAM_VOICE=SAM
RUN useradd -m -u 1000 ovos \
    && mkdir -p /home/ovos/.config/mycroft \
    && printf '{\n  "tts": {\n    "module": "ovos-tts-plugin-SAM",\n    "ovos-tts-plugin-SAM": {\n      "voice": "%s",\n      "binary": "/usr/bin/sam"\n    }\n  }\n}\n' "${SAM_VOICE}" \
        > /home/ovos/.config/mycroft/mycroft.conf \
    && chown -R 1000:1000 /home/ovos/.config
USER 1000

EXPOSE 9666
ENTRYPOINT ["ovos-tts-server", "--engine", "ovos-tts-plugin-SAM", \
            "--host", "0.0.0.0", "--port", "9666", "--cache"]
