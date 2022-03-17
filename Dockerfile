FROM debian:buster-slim

RUN apt-get update && \
  apt-get install -y git python3 python3-dev python3-pip portaudio19-dev curl build-essential libsdl1.2-dev

RUN git clone https://github.com/vidarh/SAM /tmp/SAM
WORKDIR /tmp/SAM
RUN make
RUN cp /tmp/SAM/sam /usr/bin/sam

RUN pip3 install ovos-utils==0.0.15
RUN pip3 install ovos-plugin-manager==0.0.4
RUN pip3 install ovos-tts-server==0.0.2

COPY . /tmp/ovos-tts-plugin-SAM
RUN pip3 install /tmp/ovos-tts-plugin-SAM

ENTRYPOINT ovos-tts-server --engine ovos-tts-plugin-SAM