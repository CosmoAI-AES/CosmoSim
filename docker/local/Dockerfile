FROM ubuntu:24.04

# Update package manager (apt-get) 
# and install (with the yes flag `-y`)
# Python and Pip
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python-is-python3 
RUN apt-get install -y vim build-essential git cmake pkg-config
RUN apt-get install -y \
    libxcb-glx0-dev libxcb-cursor-dev libxcb-dri2-0-dev \
    libxcb-present-dev libxcb-composite0-dev libxcb-ewmh-dev \
    libxcb-res0-dev \
    libx11-dev libx11-xcb-dev libfontenc-dev libice-dev \
    libsm-dev libxau-dev libxaw7-dev \
    libva-dev libvdpau-dev xkb-data \
    libx11-dev libx11-xcb-dev libfontenc-dev libice-dev libsm-dev \
    libxau-dev libxaw7-dev libxcomposite-dev libxcursor-dev libxdamage-dev \
    libxfixes-dev libxi-dev libxinerama-dev libxkbfile-dev libxmuu-dev \
    libxrandr-dev libxrender-dev libxres-dev libxss-dev libxtst-dev libxv-dev \
    libxxf86vm-dev libxcb-xkb-dev libxcb-icccm4-dev libxcb-keysyms1-dev \
    libxcb-xinerama0-dev libxcb-dri3-dev uuid-dev libxcb-dri3-dev \
    libxcb-util-dev libglib2.0-0


RUN mkdir setup
WORKDIR /setup
COPY ./requirements-build.txt ./
COPY ./venv.sh ./
RUN sh ./venv.sh
RUN echo 3

WORKDIR /
RUN git clone -b develop https://github.com/CosmoAI-AES/CosmoSim.git


WORKDIR /CosmoSim
RUN sh docker/local/build.sh

