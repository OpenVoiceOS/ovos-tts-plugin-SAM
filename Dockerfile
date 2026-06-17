FROM python:3.11-slim

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    git build-essential portaudio19-dev libsdl1.2-dev && \
  rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/vidarh/SAM /tmp/SAM
WORKDIR /tmp/SAM
RUN make
RUN cp /tmp/SAM/sam /usr/bin/sam

RUN pip3 install ovos-tts-server

COPY . /tmp/ovos-tts-plugin-SAM
RUN pip3 install /tmp/ovos-tts-plugin-SAM

ENTRYPOINT ovos-tts-server --engine ovos-tts-plugin-SAM
